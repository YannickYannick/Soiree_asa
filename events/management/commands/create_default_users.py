"""Crée les comptes admin et staff par défaut."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Crée admin/admin (superuser) et staff/staff (accès application + admin limité)'

    def handle(self, *args, **options):
        User = get_user_model()

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@afronight.local'},
        )
        admin_user.set_password('admin')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(
            f"Admin {'créé' if created else 'mis à jour'} — login: admin / admin (accès total)"
        ))

        staff_user, created = User.objects.get_or_create(
            username='staff',
            defaults={'email': 'staff@afronight.local'},
        )
        staff_user.set_password('staff')
        staff_user.is_staff = True
        staff_user.is_superuser = False
        staff_user.is_active = True
        staff_user.save()

        content_types = ContentType.objects.filter(app_label='events')
        perms = Permission.objects.filter(content_type__in=content_types)
        staff_user.user_permissions.set(perms)
        self.stdout.write(self.style.SUCCESS(
            f"Staff {'créé' if created else 'mis à jour'} — login: staff / staff (accès modules + admin événements)"
        ))
