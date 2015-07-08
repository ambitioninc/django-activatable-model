from django.db import models

from manager_utils import ManagerUtilsQuerySet, ManagerUtilsManager

from activatable_model.signals import model_activations_changed


class ActivatableQuerySet(ManagerUtilsQuerySet):
    """
    Provides bulk activation/deactivation methods.
    """
    def update(self, *args, **kwargs):
        if self.model.ACTIVATABLE_FIELD_NAME in kwargs:
            # Fetch the instances that are about to be updated if they have an activatable flag. This
            # is because their activatable flag may be changed in the subsequent update, causing us
            # to potentially lose what this original query referenced
            updated_instance_ids = list(self.values_list('id', flat=True))

        ret_val = super(ActivatableQuerySet, self).update(*args, **kwargs)

        if self.model.ACTIVATABLE_FIELD_NAME in kwargs and updated_instance_ids:
            # Refetch the instances that were updated and send them to the activation signal
            model_activations_changed.send(
                self.model, instance_ids=updated_instance_ids,
                is_active=kwargs[self.model.ACTIVATABLE_FIELD_NAME])
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

    # The original activatable field value, for determining when it changes
    __original_activatable_value = None

    def __init__(self, *args, **kwargs):
        super(BaseActivatableModel, self).__init__(*args, **kwargs)

        # Keep track of the original activatable value to know when it changes
        self.__original_activatable_value = getattr(self, self.ACTIVATABLE_FIELD_NAME)

    def save(self, *args, **kwargs):
        """
        A custom save method that handles figuring out when something is activated or deactivated.
        """
        current_activable_value = getattr(self, self.ACTIVATABLE_FIELD_NAME)
        is_active_changed = self.id is None or self.__original_activatable_value != current_activable_value
        self.__original_activatable_value = current_activable_value

        ret_val = super(BaseActivatableModel, self).save(*args, **kwargs)

        # Emit the signal for when the is_active flag is changed
        if is_active_changed:
            model_activations_changed.send(self.__class__, instance_ids=[self.id], is_active=current_activable_value)

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
