#!/usr/bin/env bash
# Build a wheel on macOS.
# (c) 2021 Claudio Satriano

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR/.. || exit
rm -rf dist
python setup.py bdist_wheel || exit
mkdir -p wheels
wheel_name=$(basename dist/*.whl)
mv dist/$wheel_name wheels
cd wheels && delocate-wheel $wheel_name
cd $DIR || exit
