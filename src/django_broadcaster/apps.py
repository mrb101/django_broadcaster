from django.apps import AppConfig


class DjangoBroadcasterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_broadcaster"
    verbose_name = "Django Broadcaster"

    def ready(self):
        from . import signals  # noqa
