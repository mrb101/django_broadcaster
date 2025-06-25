from django.apps import AppConfig


class DjangoDispatchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_dispatch"
    verbose_name = "Django Dispatch"

    def ready(self):
        from . import signals  # noqa
