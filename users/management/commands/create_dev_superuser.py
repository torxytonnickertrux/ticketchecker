from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserRole
import os


class Command(BaseCommand):
    help = "Create a development superuser using environment variables or defaults."

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.getenv("DEV_SUPERUSER_EMAIL", "admin@example.com")
        name = os.getenv("DEV_SUPERUSER_NAME", "Admin")
        password = os.getenv("DEV_SUPERUSER_PASSWORD", "admin123")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # Garantir que é staff/superuser
            user.is_staff = True
            user.is_superuser = True
            user.save()
            # Atribuir roles padrão se faltarem
            ensured = []
            for role in ['admin', 'event_manager']:
                _, created = UserRole.objects.get_or_create(user=user, role=role)
                if created:
                    ensured.append(role)
            if ensured:
                self.stdout.write(self.style.SUCCESS(
                    f"Existing superuser updated with roles: {', '.join(ensured)}"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"Superuser with email '{email}' already exists and has required roles."
                ))
            return

        user = User.objects.create_superuser(email=email, name=name, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Atribuir roles padrão ao superusuário de desenvolvimento
        for role in ['admin', 'event_manager']:
            UserRole.objects.get_or_create(user=user, role=role)

        self.stdout.write(self.style.SUCCESS(
            f"Created superuser: email='{email}', name='{name}'"
        ))