# flake8: noqa
from .models import BaseActivatableModel, ActivatableManager, ActivatableQuerySet
from .signals import model_activations_changed, model_activations_updated
from .version import __version__

default_app_config = 'activatable_model.apps.ActivatableModelConfig'
