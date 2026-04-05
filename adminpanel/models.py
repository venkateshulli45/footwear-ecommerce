import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone


class InviteCode(models.Model):
    code = models.CharField(max_length=24, unique=True, db_index=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name="invite_codes")
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invite_codes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="used_invite_codes",
    )
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.group.name} — {self.code}"

    @property
    def is_used(self) -> bool:
        return bool(self.used_at)

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @classmethod
    def create_code(
        cls,
        *,
        group: Group,
        created_by=None,
        ttl_hours: int = 72,
    ) -> "InviteCode":
        now = timezone.now()
        expires_at = now + timedelta(hours=max(1, int(ttl_hours)))
        # URL-safe, human-shareable token (no confusing chars like 0/O).
        token = secrets.token_urlsafe(12).replace("-", "").replace("_", "")[:18].upper()
        return cls.objects.create(
            code=token,
            group=group,
            expires_at=expires_at,
            created_by=created_by if getattr(created_by, "is_authenticated", False) else None,
        )


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    action = models.CharField(max_length=64, db_index=True)
    object_type = models.CharField(max_length=64, blank=True)
    object_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.created_at} {self.action}"
