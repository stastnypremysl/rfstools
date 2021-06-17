#!/bin/bash
mkdir -p doc/commands

pip install virtualenv
virtualenv .venv-doc
trap "rm -rf .venv-doc" EXIT

source .venv-doc/bin/activate

pip install -U pip
pip install .

for cmd in $(ls bin); do
  $cmd -h > doc/commands/$cmd.txt
done
