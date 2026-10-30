from django.core.management.base import BaseCommand

from tutor.curriculum import sync
from tutor.models import Module, Topic


class Command(BaseCommand):
    help = "Sincronizează modulele și subiectele din tutor/curriculum.py (lecțiile scrise rămân neatinse)."

    def handle(self, *args, **options):
        sync(Module, Topic)
        self.stdout.write(self.style.SUCCESS(f"{Module.objects.count()} module, {Topic.objects.count()} subiecte."))
