# flake8: noqa
from .models import BaseActivatableModel, ActivatableManager, ActivatableQuerySet
from .signals import model_activations_changed
from .version import __version__

django_app_config = 'activatable_model.apps.ActivatableModelConfig'
