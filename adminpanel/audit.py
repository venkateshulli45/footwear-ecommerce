from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from .models import AuditLog


def _client_ip(request: HttpRequest) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def log_event(
    *,
    request: HttpRequest | None,
    actor=None,
    action: str,
    object_type: str = "",
    object_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    user = actor
    if user is None and request is not None:
        user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False) is False:
        user = None

    AuditLog.objects.create(
        actor=user,
        action=action,
        object_type=object_type or "",
        object_id=str(object_id or ""),
        metadata=metadata or {},
        ip=_client_ip(request) if request is not None else None,
        user_agent=(request.META.get("HTTP_USER_AGENT", "") if request is not None else ""),
    )

