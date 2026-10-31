"""Raport „înainte / după”: ce s-a plătit pe AI și cât ar fi costat aceleași cereri cu verificarea prin cod.

Doar citește din baza de date. Fiecare apel AI (UsageRecord) e legat de mesajul elevului care l-a pornit
(ultimul mesaj al elevului din conversație, de dinainte de apel), apoi e reevaluat în sistemul nou:
- „Rulează și verifică” / „Verifică-mi codul” pe fișierul unei lecții cu exercițiu fix → o formulare cu modelul mic;
- aceleași verificări, când programul a crăpat cu o eroare pe care o explică `tutor/erori.py` → 0 (caseta din terminal);
- celelalte verificări → modelul mic, cu contextul redus (mesajul curent, fără curriculum, profil și istoric);
- întrebările libere, rezumatele, lecțiile scrise de AI → neschimbate.
Apelurile din conversații șterse între timp nu mai pot fi legate de un mesaj: le socotim neschimbate (estimare prudentă).
"""
import json
import re
from collections import defaultdict
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand

from tutor import ai, erori, usage, verificare
from tutor.models import ChatMessage, CostSettings, UsageRecord

CHARS_PER_TOKEN = 3  # româna cu diacritice (aceeași aproximare ca în ai.py)
PHRASE_TOKENS = (450, 120)  # formularea unui verdict: ~prompt + verdict, ~2-3 propoziții
_FILE_RE = re.compile(r"Fișier deschis în editor: capitole/(\d{2})-")
_RUN_RE = re.compile(r"Finalul output-ului:\n```\n(.*?)\n```", re.S)

CATEGORIES = [
    ("check_ex", "Verificare, exercițiu fix (lecțiile 1–11)"),
    ("check_err", "Verificare, eroare cunoscută"),
    ("check", "Verificare, alt cod"),
    ("explain", "„Explică eroarea” / traceback lipit în chat (socotit neschimbat)"),
    ("free", "Întrebări libere, „Următorul pas”, exerciții noi"),
    ("background", "Rezumate și plasa de siguranță (model mic)"),
    ("lesson", "Lecții scrise de AI"),
    ("unknown", "Conversații șterse (neidentificate)"),
]


def _category(msg: ChatMessage | None) -> str:
    if msg is None:
        return "unknown"
    text = msg.ui_text
    ctx = next((b.get("text", "") for b in msg.content if b.get("text", "").startswith("<context>")), "")
    if text.startswith("Am o eroare.") or "Traceback" in text or erori.explica(text):
        return "explain"
    if not (text.startswith("Am rulat codul") or text.startswith("Am terminat. Verifică-mi codul")):
        return "free"
    m = _FILE_RE.search(ctx)
    if m and verificare.exercitiu_numar(int(m[1])):
        return "check_ex"
    run = _RUN_RE.search(ctx)
    if run and erori.explica(run[1]):
        return "check_err"
    return "check"


class Command(BaseCommand):
    help = "Compară costul AI real cu cel estimat pentru verificarea prin cod (doar citește)."

    def handle(self, *args, **opts):
        rate = CostSettings.get().usd_to_gbp
        small = usage.price_for(settings.OPENAI_CHECK_MODEL if settings.PYTUTOR_PROVIDER == "openai"
                                else settings.ANTHROPIC_CHECK_MODEL)
        fixed_check = (len(ai.CHECK_PROMPT) + len(json.dumps(ai.CHECK_TOOLS, ensure_ascii=False))) // CHARS_PER_TOKEN

        def cost(price, i, o):
            return (Decimal(i) * price.input_usd + Decimal(o) * price.output_usd) / Decimal(1_000_000)

        # mesajele elevilor, pe conversație, ca să legăm fiecare apel de cererea care l-a pornit
        asks = defaultdict(list)
        for m in ChatMessage.objects.filter(role="user", is_tool_result=False).select_related("conversation"):
            asks[(m.conversation.user_id, m.conversation.project)].append(m)

        real, new, calls = defaultdict(Decimal), defaultdict(Decimal), defaultdict(int)
        turns: dict[int, list[UsageRecord]] = defaultdict(list)
        for r in UsageRecord.objects.order_by("created_at"):
            if r.project.startswith("lecție:"):
                cat = "lesson"
            elif r.model.startswith(("gpt-4.1-mini", "claude-haiku")):
                cat = "background"
            else:
                before = [m for m in asks[(r.user_id, r.project)] if m.created_at <= r.created_at]
                msg = before[-1] if before else None
                cat = _category(msg)
                if msg is not None and cat.startswith("check"):
                    turns[msg.id].append(r)
                    real[cat] += r.cost_usd
                    calls[cat] += 1
                    continue
            real[cat] += r.cost_usd
            new[cat] += r.cost_usd
            calls[cat] += 1

        # verificările, reevaluate pe tură (o tură = toate rundele de după un mesaj al elevului)
        n_turns = defaultdict(int)
        for msg_id, records in turns.items():
            msg = ChatMessage.objects.get(pk=msg_id)
            cat = _category(msg)
            n_turns[cat] += 1
            if cat == "check_ex":
                new[cat] += cost(small, *PHRASE_TOKENS)
            elif cat == "check":
                user_text = sum(len(b.get("text", "")) for b in msg.content) // CHARS_PER_TOKEN
                rounds = min(len(records), ai.CHECK_MAX_ROUNDS)
                out = sum(r.output_tokens for r in records)
                new[cat] += cost(small, rounds * (fixed_check + user_text) + out, out)

        total_real, total_new = sum(real.values()), sum(new.values())
        gbp = lambda usd: f"£{usd * rate:.3f}"  # noqa: E731
        self.stdout.write("| Tip de cerere | Apeluri | Plătit | În sistemul nou | Economie |")
        self.stdout.write("|---|---:|---:|---:|---:|")
        for key, label in CATEGORIES:
            if not calls[key]:
                continue
            saved = real[key] - new[key]
            pct = f"{100 * saved / real[key]:.0f}%" if real[key] else "-"
            turns_note = f" ({n_turns[key]} ture)" if n_turns[key] else ""
            self.stdout.write(f"| {label} | {calls[key]}{turns_note} | {gbp(real[key])} | {gbp(new[key])} | {pct} |")
        saved = total_real - total_new
        self.stdout.write(f"| **Total** | {sum(calls.values())} | **{gbp(total_real)}** | **{gbp(total_new)}** | "
                          f"**{100 * saved / total_real:.0f}%** |" if total_real else "| Total | 0 | - | - | - |")
        identified = total_real - real["unknown"]
        if identified:
            saved_id = identified - (total_new - new["unknown"])
            self.stdout.write(
                f"\nPe cererile identificate ({gbp(identified)}, {100 * identified / total_real:.0f}% din total): "
                f"{gbp(saved_id)} economisiți ({100 * saved_id / identified:.0f}%)."
            )
            if real["unknown"]:
                self.stdout.write(
                    f"Dacă și conversațiile șterse aveau același amestec de cereri (estimare): "
                    f"~{gbp(saved_id / identified * total_real)} economisiți din {gbp(total_real)}."
                )
        for key in ("check_ex", "check_err", "check"):
            if n_turns[key]:
                self.stdout.write(f"Cost mediu pe tură, {dict(CATEGORIES)[key].lower()}: "
                                  f"£{real[key] / n_turns[key] * rate:.4f} → £{new[key] / n_turns[key] * rate:.4f}")
        self.stdout.write(f"\nPreț model mic folosit la estimare: {small.model} (${small.input_usd} / ${small.output_usd} "
                          f"pe 1M tokeni); 1 USD = {rate} GBP; ~{CHARS_PER_TOKEN} caractere pe token.")
