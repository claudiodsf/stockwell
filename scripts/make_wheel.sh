#!/usr/bin/env bash
# Build a wheel on Linux/macOS.
# (c) 2021 Claudio Satriano

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR/.. || exit
python setup.py bdist_wheel || exit
mkdir -p wheels
mv dist/*.whl wheels
cd - || exit
