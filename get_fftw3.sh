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

# exit on error
set -e

# Get the script directory and move to it
scriptdir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$scriptdir"

# remove any existing FFTW3 package and directory
rm -rf fftw-3.3.10.tar.gz fftw-3.3.10 fftw3

# Download the FFTW3 library and unpack it
curl -O http://www.fftw.org/fftw-3.3.10.tar.gz
tar -xzf fftw-3.3.10.tar.gz
mkdir -p fftw3

# Build the FFTW3 library
cd fftw-3.3.10
./configure --prefix="$scriptdir/fftw3" --enable-threads
make -s
make -s install