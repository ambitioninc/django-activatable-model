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


install_requires = [
    'Django>=1.11',
    'django-manager-utils>=1.1.1',
]

tests_require = [
    'coverage',
    'psycopg2',
    'django-dynamic-fixture',
    'django-nose>=1.4',
    'mock',
]

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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
    ],
    license='MIT',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'dev': tests_require},
    test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)
