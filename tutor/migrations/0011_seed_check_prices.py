"""Prețul modelului mic Anthropic (verificări de rutină, rezumate), care lipsea din 0003."""
from decimal import Decimal as D

from django.db import migrations

# model: (input, output, cache citit, cache scris) — USD / 1M tokeni, prompturi sub 100K tokeni
PRICES = {
    "claude-haiku-5-5": (D("0.10"), D("0.50"), D("0.01"), D("0.125")),
}


def seed(apps, schema_editor):
    ModelPrice = apps.get_model("tutor", "ModelPrice")
    for model, (i, o, cr, cw) in PRICES.items():
        ModelPrice.objects.get_or_create(
            model=model, defaults={"input_usd": i, "output_usd": o, "cache_read_usd": cr, "cache_write_usd": cw}
        )


class Migration(migrations.Migration):
    dependencies = [("tutor", "0010_lesson_help_text")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
