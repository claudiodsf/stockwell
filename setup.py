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
    name='stockwell',
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    ext_package='stockwell.lib',
    ext_modules=ext_modules,
    description='Time-frequency analysis through Stockwell transform',
    long_description=long_descr,
    long_description_content_type='text/markdown',
    author='Claudio Satriano',
    author_email='satriano@ipgp.fr',
    url=project_urls['Homepage'],
    project_urls=project_urls,
    license='GNU General Public License v3 or later (GPLv3+)',
    platforms='OS Independent',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: '
            'GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics'],
    install_requires=['numpy>=1.18']
    )
