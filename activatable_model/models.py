from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_syncdb, pre_migrate
from django.dispatch import receiver

from manager_utils import ManagerUtilsQuerySet, ManagerUtilsManager

from activatable_model.signals import model_activations_changed


class ActivatableQuerySet(ManagerUtilsQuerySet):
    """
    Provides bulk activation/deactivation methods.
    """
    def update(self, *args, **kwargs):
        ret_val = super(ActivatableQuerySet, self).update(*args, **kwargs)
        if self.model.ACTIVATABLE_FIELD_NAME in kwargs:
            model_activations_changed.send(
                self.model, instances=list(self), is_active=kwargs[self.model.ACTIVATABLE_FIELD_NAME])
        return ret_val

    def activate(self):
        return self.update(**{
            self.model.ACTIVATABLE_FIELD_NAME: True
        })

    def deactivate(self):
        return self.update(**{
            self.model.ACTIVATABLE_FIELD_NAME: False
        })

    def delete(self, force=False):
        return super(ActivatableQuerySet, self).delete() if force else self.deactivate()


class ActivatableManager(ManagerUtilsManager):
    def get_queryset(self):
        return ActivatableQuerySet(self.model)

    def activate(self):
        return self.get_queryset().activate()

    def deactivate(self):
        return self.get_queryset().deactivate()


class BaseActivatableModel(models.Model):
    """
    Adds an is_active flag and processes information about when an is_active flag is changed.
    """
    class Meta:
        abstract = True

    # The name of the Boolean field that determines if this model is active or inactive. A field
    # must be defined with this name, and it must be a BooleanField. Note that the reason we don't
    # define a BooleanField is because this would eliminate the ability for the user to easily
    # define default values for the field and if it is indexed.
    ACTIVATABLE_FIELD_NAME = 'is_active'

    objects = ActivatableManager()

    def save(self, *args, **kwargs):
        """
        A custom save method that handles figuring out when something is activated or deactivated.
        """
        is_active_changed = (
            self.id is None or self.__class__.objects.filter(id=self.id).exclude(**{
                self.ACTIVATABLE_FIELD_NAME: getattr(self, self.ACTIVATABLE_FIELD_NAME)
            }).exists())

        ret_val = super(BaseActivatableModel, self).save(*args, **kwargs)

        # Emit the signal for when the is_active flag is changed
        if is_active_changed:
            model_activations_changed.send(
                self.__class__, instances=[self], is_active=getattr(self, self.ACTIVATABLE_FIELD_NAME))

        return ret_val

    def delete(self, force=False, **kwargs):
        """
        It is impossible to delete an activatable model unless force is True. This function instead sets it to inactive.
        """
        if force:
            return super(BaseActivatableModel, self).delete(**kwargs)
        else:
            setattr(self, self.ACTIVATABLE_FIELD_NAME, False)
            return self.save(update_fields=[self.ACTIVATABLE_FIELD_NAME])


def get_activatable_models():
    """
    Gets all models in a project that inherit BaseActivatableModel
    """
    return [model for model in models.get_models() if issubclass(model, BaseActivatableModel)]


@receiver(pre_migrate, dispatch_uid='make_sure_activatable_models_cannot_be_cascade_deleted_pre_migrate')
@receiver(pre_syncdb, dispatch_uid='make_sure_activatable_models_cannot_be_cascade_deleted_pre_syncdb')
def make_sure_activatable_models_cannot_be_cascade_deleted(*args, **kwargs):
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

        # Ensure all foreign keys and onetoone fields will not result in cascade deletions
        for field in model._meta.fields:
            if field.__class__ in (models.ForeignKey, models.OneToOneField):
                if field.rel.on_delete == models.CASCADE:
                    raise ValidationError((
                        'Model {0} is an activatable model. All ForeignKey and OneToOneFields '
                        'must set on_delete methods to something other than CASCADE (the default)'.format(model)
                    ))
