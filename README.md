[![Build Status](https://travis-ci.org/ambitioninc/django-activatable-model.png)](https://travis-ci.org/ambitioninc/django-activatable-model)
Django Activatable Model
==================
Provides functionality for Django models that have active and inactive states. Features of this app are:

1. An abstract BaseActivatableModel that allows the user to specify an 'activatable' (i.e. Boolean) field
1. A model_activations_changed signal that fires when models' activatable field are changed or bulk updated
1. Validation to ensure activatable models cannot be cascade deleted
1. Overriding of delete methods so that the activatable flag is set to False instead of the model(s) being deleted (unless force=True)
1. Manager/QuerySet methods to activate and deactivate models

## Installation
```python
sudo pip install django-activatable-model
```

Add ``activatable_model`` to the list of ``INSTALLED_APPS``. Although this app does not define any concrete models, it does connect signals that Django needs to know about.

## Basic Usage
Assume you have a model called ``Account`` in your app, and it is an activatable model that has a ``name`` field and a ``ForeignKey`` to a ``Group`` model.

```python
from activatable_model import BaseActivatableModel

class Account(BaseActivatableModel):
    is_active = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    group = models.ForeignKey(Group)
```

By just inheriting ``BaseActivatableModel``, your model will need to define an ``is_active`` boolean field (this field name can be changed, more on that later). If you create an ``Account`` model, the ``model_activations_changed`` signal will be sent with an ``is_active`` keyword argument set to False and an ``instances`` keyword argument that is a list of the single created account. Similarly, if you updated the ``is_active`` flag at any time via the ``save`` method, the ``model_activations_changed`` signal will be emitted again. This allows the user to do things like this:

```python
from django.dispatch import receiver
from activatable_model import model_activations_changed

@receiver(model_activations_changed, sender=Account)
def do_something_on_deactivation(sender, instances, is_active, **kwargs):
    if not is_active:
        # Either an account was deactivated or an inactive account was created...
        for account in instances:
            # Do something with every deactivated account
```

## Activatable Model Deletion
Django activatable model is meant for models that should never be deleted but rather activated/deactivated instead. Given the assumption that activatable models should never be deleted, Django activatable model does some magic underneath to ensure your activatable models are properly updated when the user calls ``delete``. Instead of deleting the object(s) directly, the ``is_active`` flag is set to False and ``model_activations_changed`` is fired.

```python
account = Account.objects.create(is_active=True)
account.delete()  # Or Account.objects.all().delete()

# The account still exists
print Account.objects.count()
1

# But it is deactivated
print Account.objects.get().is_active
False
```

The user can override this behavior by passing ``force=True`` to the model or queryset's ``delete`` method.

Along with overriding deletion, Django activatable model also overrides cascade deletion. No model that inherits ``BaseActivatableModel`` can be cascade deleted by another model. This is accomplished by connecting to Django's ``pre_syncdb`` signal and verifying that all ``ForeignKey`` and ``OneToOneField`` fields of activatable models have their ``on_delete`` arguments set to something other than the default of ``models.CASCADE``.

In fact, our ``Account`` model will not pass validation. In order to make it validate properly on syncdb, it must do the following:

```python
from django.db import models

class Account(BaseActivatableModel):
    is_active = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
```

This will ensure a ``ProtectedError`` is thrown everytime a Group is deleted. For other options on foreign key deletion behavior, go to https://docs.djangoproject.com/en/1.6/ref/models/fields/#django.db.models.ForeignKey.on_delete.

## Manager and QuerySet methods
Django activatable models automatically use an ``ActivatableManager`` manager that uses an ``ActivatableQuerySet`` queryset. This provides the following functionality:

1. Two methods - ``activate()`` and ``deactivate()`` that can be applied to a queryset
1. Overriding the ``update()`` method so that it emits ``model_activations_changed`` when the ``is_active`` flag is updated
1. Overriding the ``delete()`` method so that it calls ``deactivate()`` unless ``force=True``

## Overriding the activatable field name
The name of the activatable field can be overridden by defining the ``ACTIVATABLE_FIELD_NAME`` constant on the model to something else. By default, this constant is set to ``is_active``. An example is as follows:

```python
from activatable_model import BaseActivatableModel

class Account(BaseActivatableModel):
    ACTIVATABLE_FIELD_NAME = 'active'
    active = models.BooleanField(default=False)
```

In the above example, the model instructs the activatable model app to use ``active`` as the activatable field on the model. If the user does not define a ``BooleanField`` on the model with the same name as ``ACTIVATABLE_FIELD_NAME``, a ``ValidationError`` is raised during syncdb / migrate.

## Notes

The reason for not defining an ``is_active`` field directly on the abstract base model is to provide greater flexibility in allowing the user to specify properties of this field (such as default values, database indices, etc).

## License
MIT License (see the LICENSE file in this repo)