from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'categories'
    # Preserves existing migration history and DB table names (categoryc_*).
    label = 'categoryc'

    def ready(self):
        from . import signals  # noqa: F401
