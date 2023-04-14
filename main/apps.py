from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'

    def ready(self) -> None:
        from . import signals
