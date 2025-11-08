

from django.apps import AppConfig

class CoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cores'

    def ready(self):
        try:
            from .tasks import start_scheduler
            start_scheduler()
        except Exception as e:
            import traceback
            print("⚠️ Scheduler not started (possible first run before migrations):", e)
            traceback.print_exc()
