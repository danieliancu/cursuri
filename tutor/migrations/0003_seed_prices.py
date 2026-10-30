"""Prețuri inițiale (USD / 1M tokeni). Se pot modifica oricând din admin → Prețuri modele."""
from decimal import Decimal as D

from django.db import migrations

# model: (input, output, cache citit, cache scris)
PRICES = {
    # OpenAI — cache scris nu se facturează separat
    "gpt-4.1": (D("2.00"), D("8.00"), D("0.50"), D("0")),
    "gpt-4.1-mini": (D("0.40"), D("1.60"), D("0.10"), D("0")),
    "gpt-4o": (D("2.50"), D("10.00"), D("1.25"), D("0")),
    "gpt-4o-mini": (D("0.15"), D("0.60"), D("0.075"), D("0")),
    # Anthropic — cache scris = 1.25 × input (TTL 5 minute)
    "claude-opus-5-5": (D("4.00"), D("20.00"), D("0.20"), D("5.00")),
    "claude-opus-5": (D("5.00"), D("25.00"), D("0.50"), D("6.25")),
    "claude-opus-4-8": (D("5.00"), D("25.00"), D("0.50"), D("6.25")),
    "claude-sonnet-5-5": (D("2.00"), D("10.00"), D("0.20"), D("2.50")),
}


def seed(apps, schema_editor):
    ModelPrice = apps.get_model("tutor", "ModelPrice")
    for model, (i, o, cr, cw) in PRICES.items():
        ModelPrice.objects.get_or_create(
            model=model, defaults={"input_usd": i, "output_usd": o, "cache_read_usd": cr, "cache_write_usd": cw}
        )
    apps.get_model("tutor", "CostSettings").objects.get_or_create(pk=1)


class Migration(migrations.Migration):
    dependencies = [("tutor", "0002_usage")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
