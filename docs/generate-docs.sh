#!/bin/bash

venv=$(mktemp -d)
main_repo=$(dirname $0)/..

pip install virtualenv
virtualenv $venv
trap "rm -rf $venv" EXIT

source $venv/bin/activate

pip install -U pip
pip install -r $main_repo/requirements.txt
pip install $main_repo

(
  c_output=$main_repo/docs/_build/commands
  mkdir -p $c_output
  
  for cmd in $(ls $main_repo/bin); do (
    $cmd -h > $c_output/$cmd.txt
  ) done
)
(
  cd $main_repo/docs
  make latexpdf
)

(
  readme=$main_repo/docs/_build/README.md
  cat >$readme << EOF

# rfstools documentation
This is automatically generated documentation of [rfstools](https://git.profinit.eu/rfs/rfstools).
## rfstools developer documentation
The developer documentation is in file [rfstools-dev-doc.pdf](./rfstools-dev-doc.pdf).
## rfstools commands

EOF

  for cmd in $(ls $main_repo/bin); do
    echo "* [$cmd](./commands/$cmd.txt)" >> $readme
  done
)


