from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = "Create a default superadmin if it doesn't exist"

    def handle(self, *args, **kwargs):
        username = "tbs_admin"
        email = "superadmin@tbs.com"
        password = "tbs25"  # Change or pull from env for security

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                role="superadmin",
                first_name="hassan",
                last_name="olalekan jamiu",
                approved = True
            )
            self.stdout.write(self.style.SUCCESS("✅ Superadmin created."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Superadmin already exists."))
