from django.db import migrations


def seed(apps, schema_editor):
    from tutor.curriculum import sync

    sync(apps.get_model("tutor", "Module"), apps.get_model("tutor", "Topic"))


class Migration(migrations.Migration):
    dependencies = [("tutor", "0005_curriculum")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
