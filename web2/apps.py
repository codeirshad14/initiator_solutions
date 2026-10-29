from django.apps import AppConfig


class Web2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web2'

    def ready(self):
        from . import indexnow  # noqa: F401  (connects the IndexNow save signals)
