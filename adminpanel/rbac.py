from __future__ import annotations

from functools import wraps
from typing import Callable, Iterable

from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


ROLE_ADMINISTRATOR = "Administrator"
ROLE_FOOTWEAR_ADMIN = "FootwearAdmin"
ROLE_BUSINESS_ADMIN = "BusinessAdmin"

ALL_ROLES = (ROLE_ADMINISTRATOR, ROLE_FOOTWEAR_ADMIN, ROLE_BUSINESS_ADMIN)


def ensure_groups_exist() -> None:
    for name in ALL_ROLES:
        Group.objects.get_or_create(name=name)


def user_has_any_role(user, roles: Iterable[str]) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    role_set = set(roles)
    if not role_set:
        return False
    return user.groups.filter(name__in=role_set).exists()


def require_roles(*roles: str) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    def decorator(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not request.user.is_authenticated:
                return redirect("login")
            if not user_has_any_role(request.user, roles):
                return HttpResponse("Forbidden", status=403)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator

