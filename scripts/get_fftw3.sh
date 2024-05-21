#!/usr/bin/env bash
# Download and build the FFTW3 library
#
# This script is part of the Stockwell project.
#
# :copyright:
#     2024 Claudio Satriano <satriano@ipgp.fr>
#
# :license:
#     GNU General Public License v3.0 or later.
#     (https://www.gnu.org/licenses/gpl-3.0.html)

FFWT_VERSION="3.3.10"

# exit on error
set -e

# Get the script directory
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# Create a directory named "external" in the project root, if it doesn't exist
ext_dir="$script_dir/../external"
mkdir -p "$ext_dir"
cd "$ext_dir"

# remove any existing FFTW3 package and directory
rm -rf fftw-*.tar.gz fftw-* fftw3

# Download the FFTW3 library and unpack it
curl -O http://www.fftw.org/fftw-$FFWT_VERSION.tar.gz
tar -xzf fftw-$FFWT_VERSION.tar.gz
rm fftw-$FFWT_VERSION.tar.gz
mkdir -p fftw3

# Build the FFTW3 library
cd fftw-$FFWT_VERSION
./configure --prefix="$ext_dir/fftw3" --enable-threads
make -s
make -s install