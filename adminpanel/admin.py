from django.contrib import admin

from .models import AuditLog, InviteCode


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "group", "expires_at", "used_by", "used_at", "created_at")
    list_filter = ("group",)
    search_fields = ("code", "used_by__username", "created_by__username")
    readonly_fields = ("created_at", "used_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "object_type", "object_id", "ip")
    list_filter = ("action", "object_type")
    search_fields = ("actor__username", "action", "object_type", "object_id")
    readonly_fields = ("created_at",)
