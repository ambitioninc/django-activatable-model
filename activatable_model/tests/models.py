from django.db import models

from activatable_model.models import BaseActivatableModel


class ActivatableModel(BaseActivatableModel):
    is_active = models.BooleanField(default=False)
    char_field = models.CharField(max_length=64)


class Rel(models.Model):
    is_active = models.BooleanField(default=False)
    char_field = models.CharField(max_length=64)


class ActivatableModelWRel(BaseActivatableModel):
    is_active = models.BooleanField(default=False)
    rel_field = models.ForeignKey(Rel, on_delete=models.PROTECT)


class ActivatableModelWNonDefaultField(BaseActivatableModel):
    ACTIVATABLE_FIELD_NAME = 'active'
    active = models.BooleanField(default=False)
    char_field = models.CharField(max_length=64)
