#!/usr/bin/env python3

import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

  setuptools.setup(name='rfstools',
    version='0.2.1-r2',
    description='Remote file system tools for data manipulation between remote /and local host/ (cp, mv, ls, rm,..)',
    long_description=long_description,
    author='Přemysl Šťastný',
    author_email='p-w@stty.cz',
    url='https://git.profinit.eu/pstastny/rfstools',
    package_dir={"": "src"},
    packages=['_rfstools'],
    install_requires=[
      'rfslib>=0,<1',
      'ConfigArgParse>=1,<2'
    ],
    scripts=[*map(lambda x: 'bin/' + x, os.listdir('bin'))],
  )
