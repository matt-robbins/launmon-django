from django.apps import AppConfig

class LaundryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'laundry'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
