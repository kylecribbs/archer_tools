#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

__version__ = "v0.4.0"

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

try:
    requirements = open('requirements.txt').readlines()
except FileNotFoundError:
    requirements = []

setup(
    author='Kyle Cribbs',
    author_email='kylecribbs@outlook.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description='Archer Tools CLI for multiple things!.',
    install_requires=requirements,
    license='MIT',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='archer_tools',
    name='archer_tools',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/kylecribbs/archer_tools',
    version=__version__,
    zip_safe=False,
)
