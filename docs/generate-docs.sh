#!/bin/bash

venv=$(mktemp -d)

pip install virtualenv
virtualenv $venv
trap "rm -rf $venv" EXIT

source $venv/bin/activate

pip install -U pip
pip install -r ../requirements.txt
pip install ..

(
  c_output=./docs/_build/commands
  mkdir -p $c_output


  for cmd in $(ls bin); do (
    $cmd -h > $c_output/$cmd.txt
  ) done
)
(
  make latexpdf
)

