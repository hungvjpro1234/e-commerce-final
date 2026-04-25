from django.core.management.base import BaseCommand

from app.models import User


class Command(BaseCommand):
    help = "Seed sample data for user service"

    def handle(self, *args, **options):
        users = [
            ("admin", "admin@example.com", "admin", True, True),
            ("staff", "staff@example.com", "staff", True, False),
            ("customer", "customer@example.com", "customer", False, False),
        ]
        for username, email, role, is_staff, is_superuser in users:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="password123",
                    role=role,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                )
                user.save()
        self.stdout.write(self.style.SUCCESS("User seed data loaded"))

