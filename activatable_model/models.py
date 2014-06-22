from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_syncdb
from django.dispatch import receiver

from manager_utils import ManagerUtilsQuerySet, ManagerUtilsManager

from activatable_model.signals import model_activations_changed


class ActivatableQuerySet(ManagerUtilsQuerySet):
    """
    Provides bulk activation/deactivation methods.
    """
    def update(self, *args, **kwargs):
        super(ActivatableQuerySet, self).update(*args, **kwargs)
        if 'is_active' in kwargs:
            model_activations_changed.send(self.model.__class__, instances=list(self), is_active=kwargs['is_active'])

    def activate(self):
        self.update(is_active=True)

    def deactivate(self):
        self.update(is_active=False)

    def delete(self, force=False):
        if force:
            super(ActivatableQuerySet, self).delete()
        else:
            self.deactivate()


class ActivatableManager(ManagerUtilsManager):
    def get_queryset(self):
        return ActivatableQuerySet(self.model)

    def activate(self):
        return self.get_queryset().activate()

    def deactivate(self):
        return self.get_queryset().deactivate()

    def delete(self, force=False):
        return self.get_queryset().delete(force=force)


class BaseActivatableModel(models.Model):
    """
    Adds an is_active flag and processes information about when an is_active flag is changed.
    """
    class Meta:
        abstract = True

    # Determines whether this object is active
    is_active = models.BooleanField(default=False)

    objects = ActivatableManager()

    def save(self, *args, **kwargs):
        """
        A custom save method that handles figuring out when something is activated or deactivated.
        """
        is_active_changed = (
            self.id is None or self.__class__.objects.filter(id=self.id).exclude(is_active=self.is_active).exists())

        super(BaseActivatableModel, self).save(*args, **kwargs)

        # Emit the signal for when the is_active flag is changed
        if is_active_changed:
            model_activations_changed.send(self.__class__, instances=[self], is_active=self.is_active)

    def delete(self, force=False, **kwargs):
        """
        It is impossible to delete an activatable model unless force is True. This function instead sets it to inactive.
        """
        if force:
            return super(BaseActivatableModel, self).delete(**kwargs)
        else:
            self.is_active = False
            self.save(update_fields=['is_active'])


def get_activatable_models():
    """
    Gets all models in a project that inherit BaseActivatableModel
    """
    return [model for model in models.get_models() if issubclass(model, BaseActivatableModel)]


@receiver(pre_syncdb, dispatch_uid='make_sure_activatable_models_cannot_be_cascade_deleted')
def make_sure_activatable_models_cannot_be_cascade_deleted(*args, **kwargs):
    """
    Raises a ValidationError for any ActivatableModel that has ForeignKeys or OneToOneFields that will
    cause cascading deletions to occur.
    """
    for model in get_activatable_models():
        for field in model._meta.fields:
            if field.__class__ in (models.ForeignKey, models.OneToOneField):
                # Ensure the on_delete method is not CASCADE
                if field.rel.on_delete == models.CASCADE:
                    raise ValidationError((
                        'Model {0} is an activatable model. All ForeignKey and OneToOneFields '
                        'must set on_delete methods to something other than CASCADE (the default)'.format(model)
                    ))
