import os

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
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'ambition_test',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'db',
                'TEST': {
                    'CHARSET': 'UTF8',
                }
            }
        elif test_db == 'postgres':
            db_config = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'USER': 'postgres',
                'NAME': 'activatable_model',
            }
        elif test_db == 'sqlite':
            db_config = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'activatable_model',
            }
        else:
            raise RuntimeError('Unsupported test DB {0}'.format(test_db))

        travis_ci = os.environ.get('TRAVIS_CI', None)
        if travis_ci:
            db_config.update(
                {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': 'ambition_dev',
                    'USER': 'ambition_dev',
                    'PASSWORD': 'ambition_dev',
                    'HOST': 'localhost'
                }
            )

        settings.configure(
            TEST_RUNNER='django_nose.NoseTestSuiteRunner',
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

#def configure_settings():
#    """
#    Configures settings for manage.py and for run_tests.py.
#    """
#    if not settings.configured:
#        # Determine the database settings depending on if a test_db var is set in CI mode or not
#        test_db = os.environ.get('DB', None)
#        if test_db is None:
#            db_config = {
#                'ENGINE': 'django.db.backends.postgresql_psycopg2',
#                'NAME': 'ambition_dev',
#                'USER': 'ambition_dev',
#                'PASSWORD': 'ambition_dev',
#                'HOST': 'localhost'
#            }
#        elif test_db == 'postgres':
#            db_config = {
#                'ENGINE': 'django.db.backends.postgresql_psycopg2',
#                'USER': 'postgres',
#                'NAME': 'activatable_model',
#            }
#        elif test_db == 'sqlite':
#            db_config = {
#                'ENGINE': 'django.db.backends.sqlite3',
#                'NAME': 'activatable_model',
#            }
#        else:
#            raise RuntimeError('Unsupported test DB {0}'.format(test_db))
#
#        settings.configure(
#            TEST_RUNNER='django_nose.NoseTestSuiteRunner',
#            NOSE_ARGS=['--nocapture', '--nologcapture', '--verbosity=1'],
#            MIDDLEWARE_CLASSES={},
#            DATABASES={
#                'default': db_config,
#            },
#            INSTALLED_APPS=(
#                'django.contrib.auth',
#                'django.contrib.contenttypes',
#                'django.contrib.sessions',
#                'django.contrib.admin',
#                'activatable_model',
#                'activatable_model.tests',
#            ),
#            ROOT_URLCONF='activatable_model.urls',
#            DEBUG=False,
#        )
