#!/usr/bin/env python3

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

  setuptools.setup(name='rfstools',
    version='0.1.0',
    description='Remote file system tools for data manipulation between remote /and local host/ (cp, mv, ls, rm,..)',
    long_description=long_description,
    author='Přemysl Šťastný',
    author_email='p-w@stty.cz',
    url='https://git.profinit.eu/pstastny/rfstools',
    package_dir={"": "src"},
    install_requires=[
      'rfslib>=0,<1',
      'ConfigArgParse>=1,<2'
    ]
  )
