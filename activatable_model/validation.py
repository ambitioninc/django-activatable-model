from itertools import chain

from activatable_model.models import BaseActivatableModel
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models


def get_activatable_models():
    all_models = chain(*[app.get_models() for app in apps.get_app_configs()])
    return [model for model in all_models if issubclass(model, BaseActivatableModel)]


def validate_activatable_models():
    """
    Raises a ValidationError for any ActivatableModel that has ForeignKeys or OneToOneFields that will
    cause cascading deletions to occur. This function also raises a ValidationError if the activatable
    model has not defined a Boolean field with the field name defined by the ACTIVATABLE_FIELD_NAME variable
    on the model.
    """
    for model in get_activatable_models():
        # Verify the activatable model has an activatable boolean field
        activatable_field = next((
            f for f in model._meta.fields
            if f.__class__ == models.BooleanField and f.name == model.ACTIVATABLE_FIELD_NAME
        ), None)
        if activatable_field is None:
            raise ValidationError((
                'Model {0} is an activatable model. It must define an activatable BooleanField that '
                'has a field name of model.ACTIVATABLE_FIELD_NAME (which defaults to is_active)'.format(model)
            ))

        # Ensure all foreign keys and onetoone fields will not result in cascade deletions if not cascade deletable
        if not model.ALLOW_CASCADE_DELETE:
            for field in model._meta.fields:
                if field.__class__ in (models.ForeignKey, models.OneToOneField):
                    if field.remote_field.on_delete == models.CASCADE:
                        raise ValidationError((
                            'Model {0} is an activatable model. All ForeignKey and OneToOneFields '
                            'must set on_delete methods to something other than CASCADE (the default). '
                            'If you want to explicitely allow cascade deletes, then you must set the '
                            'ALLOW_CASCADE_DELETE=True class variable on your model.'
                        ).format(model))
