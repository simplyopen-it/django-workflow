from django.apps import AppConfig

class WorkflowConfig(AppConfig):
    name = 'workflow'

    def ready(self):
        from . import signals
