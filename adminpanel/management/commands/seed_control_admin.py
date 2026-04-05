from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from adminpanel.rbac import ROLE_ADMINISTRATOR, ensure_groups_exist


class Command(BaseCommand):
    help = "Create/update the Control Administrator user and role."

    def handle(self, *args, **options):
        ensure_groups_exist()
        admin_group = Group.objects.get(name=ROLE_ADMINISTRATOR)

        username = "admin"
        email = "venkateshulli666@gmail.com"
        password = "jagam123!"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if not created:
            changed = False
            if user.email != email:
                user.email = email
                changed = True
            if not user.is_staff:
                user.is_staff = True
                changed = True
            if not user.is_superuser:
                user.is_superuser = True
                changed = True
            if changed:
                user.save(update_fields=["email", "is_staff", "is_superuser"])

        user.set_password(password)
        user.save(update_fields=["password"])

        user.groups.add(admin_group)

        self.stdout.write(
            self.style.SUCCESS(
                f"Control admin ready: username={username} email={email} (password set)"
            )
        )

