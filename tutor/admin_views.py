"""Raportul „Consum AI” din panoul de administrare (doar superadmin)."""
from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Max, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from .models import CostSettings, UsageRecord


@user_passes_test(lambda u: u.is_active and u.is_superuser, login_url="admin:login")
def usage_report(request):
    rate = CostSettings.get().usd_to_gbp
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    d7, d30 = now - timedelta(days=7), now - timedelta(days=30)

    def cost_since(since):
        return Sum("ai_usage__cost_usd", filter=Q(ai_usage__created_at__gte=since))

    users = (
        User.objects.annotate(
            calls=Count("ai_usage"),
            tok_in=Sum("ai_usage__input_tokens"),
            tok_out=Sum("ai_usage__output_tokens"),
            c_today=cost_since(today),
            c_7=cost_since(d7),
            c_30=cost_since(d30),
            c_all=Sum("ai_usage__cost_usd"),
            last=Max("ai_usage__created_at"),
        )
        .select_related("tutor_profile")
        .order_by("-c_all", "username")
    )

    def g(v):
        return (v or Decimal(0)) * rate

    rows, totals = [], {"today": Decimal(0), "d7": Decimal(0), "d30": Decimal(0), "all": Decimal(0), "calls": 0}
    for u in users:
        level = getattr(getattr(u, "tutor_profile", None), "level", "") or "—"
        row = {
            "user": u,
            "level": level,
            "calls": u.calls,
            "tok_in": u.tok_in or 0,
            "tok_out": u.tok_out or 0,
            "today": g(u.c_today),
            "d7": g(u.c_7),
            "d30": g(u.c_30),
            "all": g(u.c_all),
            "last": u.last,
        }
        rows.append(row)
        for k in ("today", "d7", "d30", "all"):
            totals[k] += row[k]
        totals["calls"] += u.calls

    by_model = (
        UsageRecord.objects.values("model")
        .annotate(calls=Count("id"), cost=Sum("cost_usd"), tok_in=Sum("input_tokens"), tok_out=Sum("output_tokens"))
        .order_by("-cost")
    )
    unpriced = UsageRecord.objects.filter(priced=False).values_list("model", flat=True).distinct()

    ctx = {
        **admin.site.each_context(request),
        "title": "Consum AI per utilizator",
        "rows": rows,
        "totals": totals,
        "by_model": [{**m, "cost_gbp": g(m["cost"])} for m in by_model],
        "unpriced": list(unpriced),
        "rate": rate,
    }
    return render(request, "admin/tutor/usage_report.html", ctx)
