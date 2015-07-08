from django.db import models

from manager_utils import ManagerUtilsQuerySet, ManagerUtilsManager

from activatable_model.signals import model_activations_changed


class ActivatableQuerySet(ManagerUtilsQuerySet):
    """
    Provides bulk activation/deactivation methods.
    """
    def update(self, *args, **kwargs):
        if self.model.ACTIVATABLE_FIELD_NAME in kwargs:
            updated_instances = list(self)
        ret_val = super(ActivatableQuerySet, self).update(*args, **kwargs)
        if self.model.ACTIVATABLE_FIELD_NAME in kwargs:
            model_activations_changed.send(
                self.model, instances=updated_instances, is_active=kwargs[self.model.ACTIVATABLE_FIELD_NAME])
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
