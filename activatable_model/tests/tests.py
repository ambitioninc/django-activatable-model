from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_syncdb
from django.test import TestCase
from mock import patch

from activatable_model import BaseActivatableModel


class SaveTest(TestCase):
    """
    Tests that the save function emits the proper signals.
    """
    pass


class PreSyncdbTest(TestCase):
    """
    Tests that activatable models are validated properly upon pre_syncdb signal.
    """
    def test_all_valid_models(self):
        """
        Tests emitting the pre_syncdb signal. All models should validate fine.
        """
        pre_syncdb.send(sender=self)

    @patch('activatable_model.models.get_activatable_models')
    def test_foreign_key_is_null(self, mock_get_activatable_models):
        """
        SET_NULL is a valid option for foreign keys in activatable models.
        """
        # Make this an object and not an actual django model. This prevents it from always
        # being included when syncing the db. This is true for all other test models in this file.
        class CascadableModel(BaseActivatableModel):
            class Meta:
                abstract = True

            ctype = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)

        mock_get_activatable_models.return_value = [CascadableModel]
        pre_syncdb.send(sender=self)
        self.assertEquals(mock_get_activatable_models.call_count, 1)

    @patch('activatable_model.models.get_activatable_models')
    def test_foreign_key_protect(self, mock_get_activatable_models):
        """
        PROTECT is a valid option for foreign keys in activatable models.
        """
        # Make this an object and not an actual django model. This prevents it from always
        # being included when syncing the db. This is true for all other test models in this file.
        class CascadableModel(BaseActivatableModel):
            class Meta:
                abstract = True

            ctype = models.ForeignKey(ContentType, null=True, on_delete=models.PROTECT)

        mock_get_activatable_models.return_value = [CascadableModel]
        pre_syncdb.send(sender=self)
        self.assertEquals(mock_get_activatable_models.call_count, 1)

    @patch('activatable_model.models.get_activatable_models')
    def test_foreign_key_cascade(self, mock_get_activatable_models):
        """
        The default cascade behavior is invalid for activatable models.
        """
        class CascadableModel(BaseActivatableModel):
            class Meta:
                abstract = True

            ctype = models.ForeignKey(ContentType)

        mock_get_activatable_models.return_value = [CascadableModel]
        with self.assertRaises(ValidationError):
            pre_syncdb.send(sender=self)

    @patch('activatable_model.models.get_activatable_models')
    def test_one_to_one_is_null(self, mock_get_activatable_models):
        """
        SET_NULL is a valid option for foreign keys in activatable models.
        """
        # Make this an object and not an actual django model. This prevents it from always
        # being included when syncing the db. This is true for all other test models in this file.
        class CascadableModel(BaseActivatableModel):
            class Meta:
                abstract = True

            ctype = models.OneToOneField(ContentType, null=True, on_delete=models.SET_NULL)

        mock_get_activatable_models.return_value = [CascadableModel]
        pre_syncdb.send(sender=self)
        self.assertEquals(mock_get_activatable_models.call_count, 1)

    @patch('activatable_model.models.get_activatable_models')
    def test_one_to_one_protect(self, mock_get_activatable_models):
        """
        PROTECT is a valid option for foreign keys in activatable models.
        """
        # Make this an object and not an actual django model. This prevents it from always
        # being included when syncing the db. This is true for all other test models in this file.
        class CascadableModel(BaseActivatableModel):
            class Meta:
                abstract = True

            ctype = models.OneToOneField(ContentType, null=True, on_delete=models.PROTECT)

        mock_get_activatable_models.return_value = [CascadableModel]
        pre_syncdb.send(sender=self)
        self.assertEquals(mock_get_activatable_models.call_count, 1)

    @patch('activatable_model.models.get_activatable_models')
    def test_one_to_one_cascade(self, mock_get_activatable_models):
        """
        The default cascade behavior is invalid for activatable models.
        """
        class CascadableModel(BaseActivatableModel):
            class Meta:
                abstract = True

            ctype = models.OneToOneField(ContentType)

        mock_get_activatable_models.return_value = [CascadableModel]
        with self.assertRaises(ValidationError):
            pre_syncdb.send(sender=self)
