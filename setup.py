# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'activatable_model/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-activatable-model',
    version=get_version(),
    description='Django Activatable Model',
    long_description=open('README.md').read(),
    url='https://github.com/ambitioninc/django-activatable-model',
    author='Wes Kendall',
    author_email='opensource@ambition.com',
    keywords='Django, Model, Activatable',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
    license='MIT',
    install_requires=[
        'django>=1.6,<1.7',
        'django-manager-utils>=0.6.0',
    ],
    tests_require=[
        'psycopg2',
        'django-dynamic-fixture',
        'django-nose',
        'south',
        'mock',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)
