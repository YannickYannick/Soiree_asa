"""Crée les comptes admin et staff par défaut."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

INSTAGRAM_ONLY_GROUP = 'instagram_only'


class Command(BaseCommand):
    help = 'Crée admin/admin (tout) et staff/staff (page Instagram uniquement)'

    def handle(self, *args, **options):
        User = get_user_model()
        instagram_group, _ = Group.objects.get_or_create(name=INSTAGRAM_ONLY_GROUP)

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
        staff_user.is_staff = False
        staff_user.is_superuser = False
        staff_user.is_active = True
        staff_user.save()
        staff_user.groups.set([instagram_group])
        staff_user.user_permissions.clear()
        self.stdout.write(self.style.SUCCESS(
            f"Staff {'créé' if created else 'mis à jour'} — login: staff / staff (Instagram uniquement)"
        ))
