#!/usr/bin/env python
import imp
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
__version__ = imp.load_source(
    '_version', os.path.join(here, 'kearch_evaluater', '_version.py')).__version__

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='kearch_evaluater',
    version=__version__,
    description='kearch_evaluater',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=required,
    tests_require=['pytest'],
)
