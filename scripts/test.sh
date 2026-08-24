#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
project_root=$(dirname -- "$script_dir")
cd "$project_root"
python3 -m unittest discover -s tests -p 'test_*.py' -v
