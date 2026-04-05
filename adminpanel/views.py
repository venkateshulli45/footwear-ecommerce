from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db import connection, models, transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
import json
from pathlib import Path

from .models import AuditLog, InviteCode
from .audit import log_event
from .rbac import (
    ROLE_ADMINISTRATOR,
    ROLE_BUSINESS_ADMIN,
    ROLE_FOOTWEAR_ADMIN,
    ensure_groups_exist,
    require_roles,
)


def _vite_manifest_assets():
    manifest_path = (
        Path(settings.BASE_DIR) / "static" / "control-ui" / ".vite" / "manifest.json"
    )
    if not manifest_path.exists():
        return ([], [])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = manifest.get("index.html")
    if not entry:
        # fallback: pick first entry with isEntry
        for v in manifest.values():
            if isinstance(v, dict) and v.get("isEntry"):
                entry = v
                break
    if not entry:
        return ([], [])
    js = [f"control-ui/{entry['file']}"]
    css = [f"control-ui/{c}" for c in entry.get("css", [])]
    return (css, js)


@require_roles(ROLE_ADMINISTRATOR)
def control_app(request):
    css, js = _vite_manifest_assets()
    return render(request, "control/app.html", {"vite_css": css, "vite_js": js})


@require_roles(ROLE_ADMINISTRATOR)
def dashboard(request):
    return control_app(request)


def _role_groups():
    ensure_groups_exist()
    groups = Group.objects.filter(
        name__in=[ROLE_ADMINISTRATOR, ROLE_FOOTWEAR_ADMIN, ROLE_BUSINESS_ADMIN]
    )
    by_name = {g.name: g for g in groups}
    return by_name


@require_roles(ROLE_ADMINISTRATOR)
@require_http_methods(["GET", "POST"])
def users(request):
    return control_app(request)


@require_roles(ROLE_ADMINISTRATOR)
@require_http_methods(["GET", "POST"])
def role_codes(request):
    return control_app(request)


@require_roles(ROLE_ADMINISTRATOR)
def logs(request):
    return control_app(request)


@require_roles(ROLE_ADMINISTRATOR)
def health(request):
    return control_app(request)


@require_roles(ROLE_ADMINISTRATOR)
@require_http_methods(["GET"])
def api_me(request):
    names = list(request.user.groups.values_list("name", flat=True))
    return JsonResponse(
        {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "roles": names,
        }
    )


@require_roles(ROLE_ADMINISTRATOR)
@require_http_methods(["GET"])
def api_users(request):
    by_name = _role_groups()

    def current_role(u: User) -> str:
        names = set(u.groups.values_list("name", flat=True))
        if ROLE_ADMINISTRATOR in names:
            return ROLE_ADMINISTRATOR
        if ROLE_FOOTWEAR_ADMIN in names:
            return ROLE_FOOTWEAR_ADMIN
        if ROLE_BUSINESS_ADMIN in names:
            return ROLE_BUSINESS_ADMIN
        return "normal"

    qs = User.objects.all().order_by("username")
    payload = [
        {"id": u.id, "username": u.username, "email": u.email, "role": current_role(u)}
        for u in qs
    ]
    return JsonResponse(
        {
            "users": payload,
            "roles": ["normal", ROLE_ADMINISTRATOR, ROLE_FOOTWEAR_ADMIN, ROLE_BUSINESS_ADMIN],
        }
    )


@require_roles(ROLE_ADMINISTRATOR)
@require_http_methods(["POST"])
def api_set_user_role(request, user_id: int):
    by_name = _role_groups()
    role = (request.POST.get("role") or "").strip()
    if role not in ("normal", ROLE_ADMINISTRATOR, ROLE_FOOTWEAR_ADMIN, ROLE_BUSINESS_ADMIN):
        return JsonResponse({"error": "invalid_role"}, status=400)
    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "user_not_found"}, status=404)

    if target.id == request.user.id and role == "normal":
        return JsonResponse({"error": "cannot_remove_self_admin"}, status=400)

    with transaction.atomic():
        target.groups.remove(*by_name.values())
        if role != "normal":
            target.groups.add(by_name[role])

    log_event(
        request=request,
        actor=request.user,
        action="role.set",
        object_type="auth.User",
        object_id=str(target.id),
        metadata={"username": target.username, "role": role},
    )
    return JsonResponse({"ok": True})


@require_roles(ROLE_ADMINISTRATOR)
@require_http_methods(["GET", "POST"])
def api_invite_codes(request):
    by_name = _role_groups()

    if request.method == "POST":
        role = (request.POST.get("role") or "").strip()
        ttl = request.POST.get("ttl_hours") or "72"
        try:
            ttl_hours = max(1, min(720, int(ttl)))
        except Exception:
            ttl_hours = 72

        if role not in (ROLE_FOOTWEAR_ADMIN, ROLE_BUSINESS_ADMIN):
            return JsonResponse({"error": "invalid_role"}, status=400)

        code = InviteCode.create_code(
            group=by_name[role], created_by=request.user, ttl_hours=ttl_hours
        )
        log_event(
            request=request,
            actor=request.user,
            action="invite.create",
            object_type="adminpanel.InviteCode",
            object_id=str(code.id),
            metadata={"code": code.code, "role": role, "ttl_hours": ttl_hours},
        )

    codes = (
        InviteCode.objects.select_related("group", "created_by", "used_by")
        .all()
        .order_by("-created_at")[:200]
    )
    payload = [
        {
            "id": c.id,
            "code": c.code,
            "role": c.group.name,
            "expires_at": c.expires_at,
            "created_at": c.created_at,
            "used_by": c.used_by.username if c.used_by else None,
            "used_at": c.used_at,
        }
        for c in codes
    ]
    return JsonResponse({"codes": payload, "roles": [ROLE_FOOTWEAR_ADMIN, ROLE_BUSINESS_ADMIN]})


@require_roles(ROLE_ADMINISTRATOR)
@require_http_methods(["GET"])
def api_audit_logs(request):
    q = (request.GET.get("q") or "").strip()
    action = (request.GET.get("action") or "").strip()
    qs = AuditLog.objects.select_related("actor").all()
    if action:
        qs = qs.filter(action=action)
    if q:
        qs = qs.filter(
            models.Q(actor__username__icontains=q)
            | models.Q(action__icontains=q)
            | models.Q(object_type__icontains=q)
            | models.Q(object_id__icontains=q)
        )
    logs = qs.order_by("-created_at")[:300]
    payload = [
        {
            "id": e.id,
            "created_at": e.created_at,
            "actor": e.actor.username if e.actor else None,
            "action": e.action,
            "object_type": e.object_type,
            "object_id": e.object_id,
            "ip": e.ip,
            "metadata": e.metadata,
        }
        for e in logs
    ]
    actions = list(
        AuditLog.objects.values_list("action", flat=True).distinct().order_by("action")[:100]
    )
    return JsonResponse({"logs": payload, "actions": actions})


@require_roles(ROLE_ADMINISTRATOR)
@require_http_methods(["GET"])
def api_health(request):
    return JsonResponse(
        {
            "server_time": timezone.now(),
            "db_vendor": connection.vendor,
            "db_name": connection.settings_dict.get("NAME"),
            "db_host": connection.settings_dict.get("HOST"),
        }
    )

