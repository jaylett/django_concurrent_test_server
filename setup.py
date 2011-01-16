# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

PACKAGE = 'django_concurrent_test_server'
VERSION = '0.1'

setup(
    name=PACKAGE, version=VERSION,
    description="Django app to give a concurrent alternative to the runserver command.",
    packages=[
        'django_concurrent_test_server',
        'django_concurrent_test_server.management',
        'django_concurrent_test_server.management.commands'
    ],
    license='MIT',
    author='James Aylett',
    url = 'http://tartarus.org/james/computers/django/',
)
