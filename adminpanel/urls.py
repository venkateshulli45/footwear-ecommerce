from django.urls import path

from . import views


urlpatterns = [
    path('', views.dashboard, name='control_dashboard'),
    path('users/', views.users, name='control_users'),
    path('roles/codes/', views.role_codes, name='control_role_codes'),
    path('logs/', views.logs, name='control_logs'),
    path('health/', views.health, name='control_health'),

    # JSON APIs for the shadcn control UI (SPA)
    path('api/me/', views.api_me, name='control_api_me'),
    path('api/users/', views.api_users, name='control_api_users'),
    path('api/users/<int:user_id>/role/', views.api_set_user_role, name='control_api_set_user_role'),
    path('api/invite-codes/', views.api_invite_codes, name='control_api_invite_codes'),
    path('api/audit-logs/', views.api_audit_logs, name='control_api_audit_logs'),
    path('api/health/', views.api_health, name='control_api_health'),
]

