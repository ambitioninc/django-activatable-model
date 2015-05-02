from django.apps import AppConfig


class ActivatableModelConfig(AppConfig):
    name = 'activatable_model'
    verbose_name = 'Django Activatable Model'

    def ready(self):
        from activatable_model.activatable_model_validation import validate_activatable_models
        validate_activatable_models()
