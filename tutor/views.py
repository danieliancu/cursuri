import json
import re
from functools import wraps

from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.http import Http404, HttpResponseNotAllowed, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from . import ai, chapters, runner, sandbox, verificare, workspace
from .models import (
    STATUS_DOING,
    STATUS_DONE,
    STATUS_TODO,
    ChatMessage,
    CodeAnnotation,
    Conversation,
    ExerciseAttempt,
    Module,
    StudentProfile,
    Topic,
    TopicEvidence,
    TopicProgress,
)


def api(methods):
    """JSON API: cere login, verifică metoda, parsează corpul și transformă WorkspaceError în 400."""

    def deco(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Trebuie să fii autentificat.", "login": True}, status=401)
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)
            body = {}
            if request.method in ("POST", "PUT") and request.body:
                try:
                    body = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({"error": "JSON invalid"}, status=400)
            try:
                result = fn(request, body, *args, **kwargs)
            except workspace.WorkspaceError as e:
                return JsonResponse({"error": str(e)}, status=400)
            return result if not isinstance(result, dict) else JsonResponse(result)

        return wrapper

    return deco


# --- Pagini ---

@ensure_csrf_cookie
@login_required
def index(request):
    return render(request, "tutor/index.html")


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label="Prenume", max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        fields = ("username", "first_name")


def signup(request):
    if not settings.PYTUTOR_ALLOW_SIGNUP:
        raise Http404("Înregistrarea e dezactivată. Cere un cont administratorului.")
    if request.user.is_authenticated:
        return redirect("index")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("index")
    return render(request, "registration/signup.html", {"form": form})


# --- Utilizator ---

@api(["GET"])
def me(request, body):
    u = request.user
    return {
        "username": u.get_username(),
        "name": u.first_name or u.get_username(),
        "is_staff": u.is_staff,
        "sandbox": {
            "mode": "docker" if sandbox.enabled() else "local",
            "server_url": sandbox.server_url(u) if sandbox.enabled() else "http://127.0.0.1:8001",
        },
    }


# --- Proiecte & fișiere ---

@api(["GET", "POST"])
def projects(request, body):
    if request.method == "POST":
        workspace.create_project(request.user, body.get("name", ""))
    return {"projects": workspace.list_projects(request.user)}


@api(["GET"])
def tree(request, body, project):
    return {"tree": workspace.tree(request.user, project)}


@api(["GET", "PUT", "POST", "DELETE"])
def file(request, body, project):
    u = request.user
    if request.method == "GET":
        return workspace.read_file(u, project, request.GET.get("path", ""))
    if request.method == "PUT":
        rel = workspace.write_file(u, project, body.get("path", ""), body.get("content", ""))
        chapters.sync(u, project, rel)
        return {"path": rel}
    if request.method == "POST":
        rel = workspace.create(u, project, body.get("path", ""), body.get("type", "file"))
        chapters.sync(u, project, rel)
        return {"path": rel}
    rel = request.GET.get("path", "")
    workspace.delete(u, project, rel)
    chapters.forget(u, project, rel)
    return {"ok": True}


@api(["POST"])
def rename(request, body, project):
    rel = workspace.rename(request.user, project, body.get("from", ""), body.get("to", ""))
    chapters.forget(request.user, project, body.get("from", ""))
    chapters.sync(request.user, project, rel)
    return {"path": rel}


# --- Terminal ---

@api(["POST"])
def term_run(request, body, project):
    command = body.get("command", "")
    runner.run(request.user, project, command)
    # `python capitole/NN-slug/...py`: elevul lucrează la lecția aceea
    m = re.match(r"""^\s*python3?\s+["']?(capitole/[^\s"']+\.py)""", command)
    topic = chapters.topic_for_path(m[1]) if m else None
    if topic:
        mark_working(request.user, topic)
    return {"ok": True}


@api(["POST"])
def term_stop(request, body, project):
    runner.stop(request.user, project)
    return {"ok": True}


@api(["POST"])
def term_input(request, body, project):
    runner.send_input(request.user, project, body.get("text", ""))
    return {"ok": True}


@api(["POST"])
def term_clear(request, body, project):
    runner.clear(request.user, project)
    return {"ok": True}


@api(["GET"])
def term_output(request, body, project):
    workspace.project_dir(request.user, project)
    try:
        since = int(request.GET.get("since", "0"))
    except ValueError:
        since = 0
    return runner.output(request.user, project, since)


# --- Chat ---

@api(["GET", "POST", "DELETE"])
def chat(request, body, project):
    user = request.user
    workspace.project_dir(user, project)
    if request.method == "GET":
        return {"messages": ai.ui_messages(user, project)}
    if request.method == "DELETE":
        Conversation.objects.filter(user=user, project=project).delete()
        return {"ok": True}

    text = (body.get("message") or "").strip()
    if not text:
        return JsonResponse({"error": "Mesaj gol"}, status=400)
    ctx = body.get("context") or {}
    mode = "check" if body.get("mode") == "check" else "chat"

    def sse():
        try:
            for ev in ai.chat_stream(user, project, text, ctx, mode=mode):
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except Exception as e:  # noqa: BLE001 — orice eroare ajunge în UI, nu în gol
            yield f"data: {json.dumps({'type': 'error', 'message': f'Eroare internă: {e}'}, ensure_ascii=False)}\n\n"

    resp = StreamingHttpResponse(sse(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp


def _open_lesson(user, project: str, topic: Topic) -> str | None:
    """Elevul a deschis lecția (oricare, și una învățată): devine lecția curentă și îi pregătim folderul de cod.
    Statusul nu se schimbă: o lecție doar privită nu e „în lucru”."""
    path = chapters.ensure(user, project, topic)
    StudentProfile.for_user(user)  # profilul poate lipsi la un elev nou
    # update(), nu save(): „profil actualizat” (updated_at) înseamnă că l-a actualizat tutorele
    StudentProfile.objects.filter(user=user).update(current_topic=topic)
    return path


def mark_working(user, topic: Topic) -> None:
    """Elevul chiar lucrează la lecție (rulează cod în fișierul ei, cere sau verifică exercițiul): „în lucru”.
    O lecție învățată rămâne învățată."""
    tp, created = TopicProgress.objects.get_or_create(user=user, topic=topic, defaults={"status": STATUS_DOING})
    if not created and tp.status != STATUS_DONE:
        tp.status = STATUS_DOING
        tp.save()  # actualizează data: e lecția la care s-a lucrat ultima dată


def current_topic(user) -> Topic | None:
    """Lecția curentă: ultima deschisă de elev, altfel pasul următor din curriculum."""
    p = StudentProfile.objects.filter(user=user).select_related("current_topic__module").first()
    return (p.current_topic if p and p.current_topic else None) or _current_topic(user)


@api(["POST"])
def chapter(request, body, project):
    """Elevul a ales o lecție: îi dăm folderul de cod al capitolului și o facem lecția curentă."""
    user = request.user
    topic = Topic.objects.filter(slug=body.get("topic", "")).first()
    if not topic:
        return JsonResponse({"error": "Subiect inexistent"}, status=404)
    path = _open_lesson(user, project, topic)
    tp = TopicProgress.objects.filter(user=user, topic=topic).first()
    return {"path": path, "status": tp.status if tp else STATUS_TODO}


def _current_topic(user) -> Topic | None:
    """Pasul activ, după aceeași regulă ca sumarul din stânga: ultimul subiect „în lucru”, altfel primul neînvățat."""
    tp = TopicProgress.objects.filter(user=user, status=STATUS_DOING).select_related("topic").order_by("-updated_at").first()
    if tp:
        return tp.topic
    done = TopicProgress.objects.filter(user=user, status=STATUS_DONE).values_list("topic_id", flat=True)
    return Topic.objects.exclude(id__in=list(done)).order_by("module__order", "order").first()


def _exercise_pending(user, topic: Topic) -> bool:
    """Lecția are exercițiu fix pe care elevul nu l-a rezolvat încă."""
    if not chapters.exercise_path(topic):
        return False  # lecția n-are exercițiu fix
    solved = ExerciseAttempt.objects.filter(user=user, topic=topic, solved_at__isnull=False).exists()
    return not solved and not TopicProgress.objects.filter(user=user, topic=topic, status=STATUS_DONE).exists()


def _resume_exercise(user, topic: Topic) -> None:
    """Elevul a primit iar exercițiul fix: fișierul capitolului se verifică din nou cu testele lui."""
    ExerciseAttempt.objects.filter(user=user, topic=topic, skipped=True).update(skipped=False, failed=0)


def _exercise_text(topic: Topic, path: str) -> str:
    ex = verificare.exercitiu(topic.slug)
    n = chapters.folder_for(topic).split("/")[1].split("-")[0]
    return (f"Exercițiul lecției {int(n)}, **{ex['titlu']}**: {ex.get('enunt', '')} Îl găsești în `{path}` "
            f"(l-am deschis în editor); enunțul complet e în [lecție](/progres/#{topic.slug}), la „Exercițiu”. "
            "Când e gata, apasă **Rulează și verifică**: îl verific pe loc, cu testele lecției.")


@api(["POST"])
def step(request, body, project):
    """„Următorul pas” și „Exercițiu nou”, fără AI, când răspunsul se știe din curriculum și din exercițiile fixe.

    `{"ai": true}` = nu se poate răspunde din cod (ex. exercițiu nou la o lecție fără exercițiu fix sau deja
    rezolvat): interfața trimite atunci cererea tutorelui AI, ca înainte.
    """
    user = request.user
    workspace.project_dir(user, project)
    kind = body.get("tip")
    if kind == "exercitiu":
        # lecția fișierului deschis, altfel pasul activ
        topic = chapters.topic_for_path(body.get("path") or "") or current_topic(user)
        if not topic or not _exercise_pending(user, topic):
            return {"ai": True}
        _open_lesson(user, project, topic)
        mark_working(user, topic)
        path = chapters.exercise_path(topic)
        text = _exercise_text(topic, path)
        _resume_exercise(user, topic)
    elif kind == "urmator":
        topic = _current_topic(user)
        if not topic:
            return {"ai": True}
        main = _open_lesson(user, project, topic)
        mark_working(user, topic)
        n = chapters.folder_for(topic).split("/")[1].split("-")[0] if chapters.has_folder(topic) else ""
        lesson = f"lecția {int(n)}, **{topic.title}**" if n else f"lecția **{topic.title}**"
        if _exercise_pending(user, topic):
            path = chapters.exercise_path(topic)
            text = f"Următorul pas e {lesson}. " + _exercise_text(topic, path)
            _resume_exercise(user, topic)
        else:
            path = main
            text = (f"Următorul pas e {lesson}. Citește [lecția](/progres/#{topic.slug}), apoi apasă "
                    "**Exercițiu nou** ca să primești un exercițiu" + (f", pe care îl scrii în `{main}`." if main else "."))
    else:
        return JsonResponse({"error": "Pas necunoscut"}, status=400)

    conv, _ = Conversation.objects.get_or_create(user=user, project=project)
    ask = body.get("text") or ("Dă-mi un exercițiu." if kind == "exercitiu" else "Care e următorul pas?")
    ChatMessage.objects.create(conversation=conv, role="user", ui_text=ask, content=[{"type": "text", "text": ask}])
    ChatMessage.objects.create(conversation=conv, role="assistant", content=[{"type": "text", "text": text}])
    return {"ai": False, "mesaj": text, "path": path, "topic": topic.title}


def _chapter_exercise(user, project: str, path: str):
    """(cale relativă, subiect, exercițiu) dacă `path` e fișierul capitolului și exercițiul fix e încă de rezolvat.

    După ce e rezolvat, sau dacă elevul a spus că lucrează la altceva, fișierul îl verifică modelul mic."""
    rel = workspace.rel_of(user, project, workspace.safe_path(user, project, path))
    topic = chapters.topic_for_path(rel)
    if not topic or rel != chapters.exercise_path(topic) or not _exercise_pending(user, topic):
        return rel, None, None
    if ExerciseAttempt.objects.filter(user=user, topic=topic, skipped=True).exists():
        return rel, None, None
    return rel, topic, verificare.exercitiu(topic.slug)


@api(["POST"])
def exercise_check(request, body, project):
    """„Rulează și verifică” pe exercițiul fix al lecției: verdictul îl dă codul, modelul mic doar îl formulează."""
    user = request.user
    rel, topic, ex = _chapter_exercise(user, project, body.get("path", ""))
    if not ex:
        return {"exercitiu": False}
    source = workspace.read_file(user, project, rel)["content"]

    def run(stdin):
        return runner.run_capture(user, project, rel, stdin, timeout=10, echo_input=True)

    try:
        v = verificare.verifica_cod(source, ex, run, rel.rsplit("/", 1)[-1])
    except RuntimeError as e:  # ex. Docker oprit
        return JsonResponse({"error": str(e)}, status=400)

    mark_working(user, topic)
    att, _ = ExerciseAttempt.objects.get_or_create(user=user, topic=topic)
    if verificare.alt_program(att.last_code, source):
        att.failed = 0  # elevul a început altceva: indiciile pornesc iar de la prima treaptă
    att.last_code = source
    hint = None
    if v["rezultat"] == "corect":
        att.solved_at = att.solved_at or timezone.now()
    else:
        att.failed += 1
        level = min(att.failed, len(ex["indicii"]))
        att.hints_shown = max(att.hints_shown, level)
        hint = {"treapta": level, "din": len(ex["indicii"]), "text": ex["indicii"][level - 1]}
    att.save()

    mesaj = ai.formuleaza(user, project, verificare.pentru_ai(v, hint), verificare.mesaj_simplu(v, hint and hint["text"]))
    conv, _ = Conversation.objects.get_or_create(user=user, project=project)
    ask = "Am rulat programul. Verifică exercițiul."
    ChatMessage.objects.create(conversation=conv, role="user", ui_text=ask, content=[
        {"type": "text", "text": f"{ask}\n(Verificare automată: {json.dumps(verificare.pentru_ai(v, hint), ensure_ascii=False)})"},
    ])
    ChatMessage.objects.create(conversation=conv, role="assistant", content=[{"type": "text", "text": mesaj}])

    # Tot ce s-a găsit (testul, ce trebuia, output-ul, indiciul) stă într-un balon pe rândul potrivit;
    # în chat rămâne doar fraza tutorelui.
    events: list = []
    note = verificare.balon(v, source, hint)
    ai._run_tool(user, project, "annotate_code", {"path": rel, "notes": [note] if note else []}, events)
    if v["rezultat"] == "corect":
        done = TopicProgress.objects.filter(user=user, topic=topic, status=STATUS_DONE).exists()
        if not done:
            ai._record_progress(user, project, {"topic": topic.slug, "status": STATUS_DONE, "comment": mesaj,
                                                "path": rel}, events)
    return {"exercitiu": True, "verdict": v, "indiciu": hint, "mesaj": mesaj, "events": events}


@api(["POST"])
def exercise_skip(request, body, project):
    """Plasa de siguranță din balon: „Nu lucrez la exercițiul lecției”. Fișierul capitolului nu mai e
    verificat cu testele lui (până când elevul cere din nou exercițiul) și i se șterge balonul."""
    user = request.user
    rel = workspace.rel_of(user, project, workspace.safe_path(user, project, body.get("path", "")))
    topic = chapters.topic_for_path(rel)
    if not topic or rel != chapters.exercise_path(topic):
        return JsonResponse({"error": "Fișierul nu are exercițiu fix."}, status=404)
    ExerciseAttempt.objects.update_or_create(user=user, topic=topic, defaults={"skipped": True, "failed": 0})
    CodeAnnotation.objects.filter(user=user, project=project, path=rel).delete()
    return {"ok": True}


@api(["GET", "DELETE"])
def notes(request, body, project):
    """Baloanele de explicații ale tutorelui pentru proiect: {path: [note, ...]}."""
    user = request.user
    workspace.project_dir(user, project)
    qs = CodeAnnotation.objects.filter(user=user, project=project)
    if request.method == "DELETE":
        qs.filter(path=request.GET.get("path", "")).delete()
        return {"ok": True}
    return {"notes": {a.path: a.notes for a in qs}}


@api(["GET", "DELETE"])
def profile(request, body):
    p = StudentProfile.for_user(request.user)
    if request.method == "DELETE":
        # Resetare completă: tutorele va reevalua elevul de la zero.
        p.delete()
        TopicProgress.objects.filter(user=request.user).delete()
        TopicEvidence.objects.filter(user=request.user).delete()
        p = StudentProfile.for_user(request.user)
    return {"profile": p.as_dict()}


# --- Progres & lecții ---

@ensure_csrf_cookie
@login_required
def progress_page(request):
    return render(request, "tutor/progress.html")


@api(["GET"])
def progress(request, body):
    user = request.user
    statuses, touched = {}, {}
    for tid, st, at in TopicProgress.objects.filter(user=user).values_list("topic_id", "status", "updated_at"):
        statuses[tid], touched[tid] = st, at
    counts = dict(
        TopicEvidence.objects.filter(user=user).values("topic_id").annotate(n=Count("id")).values_list("topic_id", "n")
    )
    project = request.GET.get("project", "")
    code_paths = {}
    cur = current_topic(user)
    if project:
        if cur:  # editorul deschide la pornire codul lecției curente
            code_paths[cur.id] = chapters.ensure(user, project, cur)
        code_paths = {**chapters.paths_by_topic(user, project), **code_paths}
    modules = []
    for m in Module.objects.prefetch_related("topics"):
        topics = [
            {
                "slug": t.slug,
                "title": t.title,
                "summary": t.summary,
                "status": statuses.get(t.id, STATUS_TODO),
                "evidence": counts.get(t.id, 0),
                "updated_at": touched[t.id].isoformat() if t.id in touched else None,
                "code_path": code_paths.get(t.id),
            }
            for t in m.topics.all()
        ]
        modules.append({"slug": m.slug, "title": m.title, "description": m.description, "topics": topics})
    return {"profile": StudentProfile.for_user(user).as_dict(), "modules": modules, "current": cur.slug if cur else None}


@api(["GET"])
def topic_detail(request, body, slug):
    t = Topic.objects.select_related("module").filter(slug=slug).first()
    if not t:
        return JsonResponse({"error": "Subiect inexistent"}, status=404)
    tp = TopicProgress.objects.filter(user=request.user, topic=t).first()
    evidence = [
        {
            "status": e.status,
            "comment": e.comment,
            "project": e.project,
            "path": e.path,
            "start_line": e.start_line,
            "code": e.code,
            "created_at": e.created_at.isoformat(),
        }
        for e in TopicEvidence.objects.filter(user=request.user, topic=t)
    ]
    return {
        "slug": t.slug,
        "title": t.title,
        "module": t.module.title,
        "summary": t.summary,
        "lesson": t.lesson,
        "status": tp.status if tp else STATUS_TODO,
        "evidence": evidence,
    }


@api(["POST"])
def topic_lesson(request, body, slug):
    """Scrie lecția cu AI-ul (streaming), dacă încă nu există."""
    t = Topic.objects.select_related("module").filter(slug=slug).first()
    if not t:
        return JsonResponse({"error": "Subiect inexistent"}, status=404)
    user = request.user

    def sse():
        if t.lesson:
            yield f"data: {json.dumps({'type': 'text', 'text': t.lesson}, ensure_ascii=False)}\n\n"
            yield 'data: {"type": "done"}\n\n'
            return
        try:
            for ev in ai.generate_lesson(user, t):
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except Exception as e:  # noqa: BLE001
            yield f"data: {json.dumps({'type': 'error', 'message': f'Eroare internă: {e}'}, ensure_ascii=False)}\n\n"

    resp = StreamingHttpResponse(sse(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp
