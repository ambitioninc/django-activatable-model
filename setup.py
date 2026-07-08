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


def get_lines(file_path):
    return open(file_path, 'r').read().split('\n')


install_requires = get_lines('requirements/requirements.txt')
tests_require = get_lines('requirements/requirements-testing.txt')


setup(
    name='django-activatable-model',
    version=get_version(),
    description='Django Activatable Model',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ambitioninc/django-activatable-model',
    author='Wes Kendall',
    author_email='opensource@ambition.com',
    keywords='Django, Model, Activatable',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 5.2',
        'Framework :: Django :: 6.0',
    ],
    license='MIT',
    python_requires='>=3.10',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'dev': tests_require},
    test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)
