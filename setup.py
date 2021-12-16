# -*- coding: utf-8 -*-
"""setup.py: setuptools control."""
import sys
import os
from setuptools import setup
from distutils.core import Extension
try:
    import numpy
except ImportError:
    sys.exit('NumPy is required for installation. Please install it first.')

# import inspect
# import os
# import sys

# Import the version string.
# path = os.path.join(os.path.abspath(os.path.dirname(inspect.getfile(
#     inspect.currentframe()))), 'stockwell')
# sys.path.insert(0, path)
# from version import get_git_version

with open('README.md', 'rb') as f:
    long_descr = f.read().decode('utf-8')

include_dirs_st = [numpy.get_include()]
library_dirs_st = []
# This seems necessary only for Windows
if 'CONDA_PREFIX' in os.environ:
    include_dirs_st.append(
        os.path.join(os.environ['CONDA_PREFIX'], 'Library', 'include'))
    library_dirs_st.append(
        os.path.join(os.environ['CONDA_PREFIX'], 'Library', 'lib'))

ext_modules = []
ext_modules.append(Extension(
    'st',
    sources=['stockwell/c_libs/st.c', 'stockwell/c_libs/stmodule.c'],
    include_dirs=include_dirs_st,
    library_dirs=library_dirs_st,
    libraries=['fftw3']
    ))
ext_modules.append(Extension(
    'sine',
    sources=['stockwell/c_libs/sinemodule.c'],
    include_dirs=[numpy.get_include()]
    ))

setup(
    name='stockwell',
    packages=['stockwell'],
    include_package_data=True,
    # version=get_git_version(),
    version=1.0,
    ext_package='stockwell.lib',
    ext_modules=ext_modules,
    description='Time-frequency analysis through Stockwell transform',
    long_description=long_descr,
    author='Claudio Satriano',
    author_email='satriano@ipgp.fr',
    url='http://www.ipgp.fr/~satriano',
    license='CeCILL Free Software License Agreement, Version 2.1',
    platforms='OS Independent',
    classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre '
                'License, version 2.1 (CeCILL-2.1)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Physics'],
    )
