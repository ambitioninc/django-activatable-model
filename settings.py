import os
import json

from django.conf import settings


def configure_settings():
    """
    Configures settings for manage.py and for run_tests.py.
    """
    if not settings.configured:
        # Determine the database settings depending on if a test_db var is set in CI mode or not
        test_db = os.environ.get('DB', None)
        if test_db is None:
            db_config = {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'activatable_model',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'db',
            }
        elif test_db == 'postgres':
            db_config = {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'activatable_model',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'db',
            }
        else:
            raise RuntimeError('Unsupported test DB {0}'.format(test_db))

        # Check env for db override (used for github actions)
        if os.environ.get('DB_SETTINGS'):
            db_config = json.loads(os.environ.get('DB_SETTINGS'))

        settings.configure(
            TEST_RUNNER='django_nose.NoseTestSuiteRunner',
            SECRET_KEY='*',
            NOSE_ARGS=['--nocapture', '--nologcapture', '--verbosity=1'],
            MIDDLEWARE_CLASSES={},
            DATABASES={
                'default': db_config,
            },
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.admin',
                'activatable_model',
                'activatable_model.tests',
            ),
            ROOT_URLCONF='activatable_model.urls',
            DEBUG=False,
        )
