#!/usr/bin/env python3

import setuptools
import os

with open("README.md", "r", encoding="utf-8") as freadme, open("version.txt", "r") as fversion:
  long_description = freadme.read()
  version = fversion.read().splitlines()[0]

  setuptools.setup(name='rfstools',
    version=version,
    description='Remote file system tools for data manipulation between remote /and local host/ (cp, mv, ls, rm,..)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    author='Přemysl Šťastný',
    author_email='p-w@stty.cz',
    url='https://git.profinit.eu/pstastny/rfstools',
    package_dir={"": "src"},
    packages=['_rfstools','rfslib'],
    install_requires=[
      'ConfigArgParse>=1.4.1,<2',
      'texttable>=1.6.4,<2',

      # rfslib dependencies
      'pysmb>=1.2.7,<2',
      'paramiko>=2.7.2,<4',
      'smbprotocol>=1.6.1,<2',
      'ftputil>=5.0.1,<6'
      
    ],
    scripts=[*map(lambda x: 'bin/' + x, os.listdir('bin'))],
  )
