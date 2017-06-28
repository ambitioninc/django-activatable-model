from django.db import models

from manager_utils import ManagerUtilsQuerySet, ManagerUtilsManager

from activatable_model.signals import model_activations_changed, model_activations_updated


class ActivatableQuerySet(ManagerUtilsQuerySet):
    """
    Provides bulk activation/deactivation methods.
    """
    def update(self, *args, **kwargs):
        if self.model.ACTIVATABLE_FIELD_NAME in kwargs:
            # Fetch the instances that are about to be updated if they have an activatable flag. This
            # is because their activatable flag may be changed in the subsequent update, causing us
            # to potentially lose what this original query referenced
            new_active_state_kwargs = {
                self.model.ACTIVATABLE_FIELD_NAME: kwargs.get(self.model.ACTIVATABLE_FIELD_NAME)
            }
            changed_instance_ids = list(self.exclude(**new_active_state_kwargs).values_list('id', flat=True))
            updated_instance_ids = list(self.values_list('id', flat=True))

        ret_val = super(ActivatableQuerySet, self).update(*args, **kwargs)

        if self.model.ACTIVATABLE_FIELD_NAME in kwargs and updated_instance_ids:
            # send the instances that were updated to the activation signals
            model_activations_changed.send(
                self.model, instance_ids=changed_instance_ids,
                is_active=kwargs[self.model.ACTIVATABLE_FIELD_NAME])
            model_activations_updated.send(
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

    # There are situations where you might actually want other models to be able to force-delete
    # you ActivatibleModel.  In this case, no special delete action is taken and you model will
    # be removed from the database.  To enable this behavior, set ALLOW_CASCADE_DELETE to True
    ALLOW_CASCADE_DELETE = False

    objects = ActivatableManager()

    # The original activatable field value, for determining when it changes
    __original_activatable_value = None

    def __init__(self, *args, **kwargs):
        super(BaseActivatableModel, self).__init__(*args, **kwargs)

        # Keep track of the updated status of the activatable field
        self.activatable_field_updated = self.id is None

        # Keep track of the original activatable value to know when it changes
        self.__original_activatable_value = getattr(self, self.ACTIVATABLE_FIELD_NAME)

    def __setattr__(self, key, value):
        if key == self.ACTIVATABLE_FIELD_NAME:
            self.activatable_field_updated = True
        return super(BaseActivatableModel, self).__setattr__(key, value)

    def save(self, *args, **kwargs):
        """
        A custom save method that handles figuring out when something is activated or deactivated.
        """
        current_activable_value = getattr(self, self.ACTIVATABLE_FIELD_NAME)
        is_active_changed = self.id is None or self.__original_activatable_value != current_activable_value
        self.__original_activatable_value = current_activable_value

        ret_val = super(BaseActivatableModel, self).save(*args, **kwargs)

        # Emit the signals for when the is_active flag is changed
        if is_active_changed:
            model_activations_changed.send(self.__class__, instance_ids=[self.id], is_active=current_activable_value)
        if self.activatable_field_updated:
            model_activations_updated.send(self.__class__, instance_ids=[self.id], is_active=current_activable_value)

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
