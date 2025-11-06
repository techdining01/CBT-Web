from django.core.management.base import BaseCommand
from exams.models import Class  # adjust if Class model is elsewhere

class Command(BaseCommand):
    help = "Create school classes JSS1 - SSS3"

    def handle(self, *args, **kwargs):
        classes = [
            "JSS1", "JSS2", "JSS3",
            "SSS1", "SSS2", "SSS3"
        ]

        created = 0
        for cls in classes:
            obj, was_created = Class.objects.get_or_create(name=cls)
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created {cls}"))
            else:
                self.stdout.write(self.style.WARNING(f"{cls} already exists"))

        self.stdout.write(self.style.SUCCESS(f"Done. {created} new classes created."))
