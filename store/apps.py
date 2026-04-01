from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    # Preserves existing migration history and DB table names (jagamfoot_*).
    label = 'jagamfoot'
