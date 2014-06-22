from django.db import models

from activatable_model import BaseActivatableModel


class ActivatableModel(BaseActivatableModel):
    char_field = models.CharField(max_length=64)


class Rel(models.Model):
    char_field = models.CharField(max_length=64)


class ActivatableModelWRel(BaseActivatableModel):
    rel_field = models.ForeignKey(Rel, on_delete=models.PROTECT)
