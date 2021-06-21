#!/bin/bash
cd $(dirname $0)/..

c_output=./docs/_build/commands
mkdir -p $c_output

pip install virtualenv
virtualenv .venv-doc
trap "rm -rf .venv-doc" EXIT

source .venv-doc/bin/activate

pip install -U pip
pip install .

for cmd in $(ls bin); do
  $cmd -h > $c_output/$cmd.txt
done
