from django.apps import AppConfig


class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.menu'

    def ready(self):
        try:
            from . import signals
        except:
            print("failed to import apps.menu.signals.")