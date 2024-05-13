#!/usr/bin/env bash
set -eu -o pipefail

required_py_version="Python 3.10.6"

function check-py-version() {
  py_version=$( python3 --version )
  if [[ $py_version != $required_py_version ]]; then
    echo "You do not have the correct python version! You need [$required_py_version]"
    exit 1
  fi
}

function create-venv() {
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  deactivate
  echo "Virtual environment set up successfully"
}

check-py-version
create-venv
