#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa

from os import path
from setuptools import setup, find_packages


with open(path.join(find_packages().pop(0), '__about__.py')) as f:
    exec(f.read())


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name=__title__,
    version=__version__,
    description='Command line tool to generate ignore files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/%s/%s' % (__author__, __title__),
    author=__author__,
    author_email=__email__,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'dotignore=dotignore.cli:main',
        ]
    },
    keywords=['git', 'ignore files', 'command line tool'],
    packages=find_packages(),
    install_requires=['requests'],
    tests_require=[],
    zip_safe=False,
)

