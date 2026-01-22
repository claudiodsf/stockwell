# -*- coding: utf-8 -*-
"""setup.py: setuptools control."""
import os
from setuptools import setup, find_packages, Extension
import versioneer

with open('README.md', 'rb') as f:
    long_descr = f.read().decode('utf-8').replace(
        '(stockwell.png)',
        '(https://cdn.jsdelivr.net/gh/claudiodsf/stockwell/stockwell.png)'
    ).replace(
        '(inv_stockwell.png)',
        '(https://cdn.jsdelivr.net/gh/claudiodsf/stockwell/inv_stockwell.png)'
    )

project_urls = {
    'Homepage': 'https://github.com/claudiodsf/stockwell',
    'Source': 'https://github.com/claudiodsf/stockwell',
}

include_dirs_st = []
library_dirs_st = []
# First search for fftw3 in the "external" directory
# (i.e., installed using the script "get_fftw3.sh")
fftw3_dir = os.path.join('external', 'fftw3')
if os.path.exists(fftw3_dir):
    include_dirs_st.append(os.path.join(fftw3_dir, 'include'))
    library_dirs_st.append(os.path.join(fftw3_dir, 'lib'))
else:
    # Search Homebrew fftw3 on macOS
    if 'HOMEBREW_PREFIX' in os.environ:
        include_dirs_st.append(
            os.path.join(os.environ['HOMEBREW_PREFIX'], 'include'))
        library_dirs_st.append(
            os.path.join(os.environ['HOMEBREW_PREFIX'], 'lib'))
    # Search for a version of fftw3 provided by Conda
    if 'CONDA_PREFIX' in os.environ:
        include_dirs_st.append(
            os.path.join(os.environ['CONDA_PREFIX'], 'Library', 'include'))
        library_dirs_st.append(
            os.path.join(os.environ['CONDA_PREFIX'], 'Library', 'lib'))
    # This is needed for Miniconda on GitHub-hosted Windows runner
    if 'CONDA' in os.environ:
        include_dirs_st.append(
            os.path.join(os.environ['CONDA'], 'Library', 'include'))
        library_dirs_st.append(
            os.path.join(os.environ['CONDA'], 'Library', 'lib'))

ext_modules = [
    Extension(
        'st',
        sources=['stockwell/c_libs/st.c'],
        include_dirs=include_dirs_st,
        library_dirs=library_dirs_st,
        libraries=['fftw3'],
    ),
    Extension(
        'sine',
        sources=['stockwell/c_libs/sine.c'],
    )
]

setup(
    long_description=long_descr,
    long_description_content_type='text/markdown',
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    ext_package='stockwell.lib',
    ext_modules=ext_modules,
)
