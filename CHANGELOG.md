# Stockwell

Python package for time-frequency analysis through Stockwell transform.

Based on original code from [NIMH MEG Core Facility].

[NIMH MEG Core Facility]: https://kurage.nimh.nih.gov/meglab/Meg/Stockwell.

(c) 2021-2026 Claudio Satriano <satriano@ipgp.fr>

## Unreleased

- Add support for Python 3.14
- Minimum required Python version: 3.9

## v1.2 - 2025-01-08

- Add support for Python 3.13
- Remove support for Python 3.8

## v1.1.2 - 2024-05-22

- Make it possible again to directly call functions from submodules, like it
  was in versions prior to v1.1. Example:

  ```python
  import stockwell
  stockwell.st.st(data, fmin, fmax)
  ```

## v1.1.1 - 2024-05-21

- Remove support for Python 3.6 and 3.7
- Add support for Python 3.11 and 3.12
- Support for Numpy 2.0!
- Added a script to download and compile FFTW3

## v1.1 - 2023-06-05

- Use ctypes to wrap the modules written in C
- License changed to GPLv3

## v1.0.7 - 2022-07-27

- Packages for Python 3.10 and macOS arm (M1, M2)

## v1.0.6 - 2022-04-21

- Fix for missing file in source distribution

## v1.0.5 - 2022-04-21

- New parameters for `st.st()`: `gamma` and `win_type`:
  - `gamma` can be used to tune the time and frequency resolutions
     of the S-transform.
  - `win_type` can be set to 'gauss' (default) and 'kazemi' (Kazemi, 2014)

## v1.0.4 - 2021-11-04

- Use `versioneer` to generate package version
- Add tests

## v1.0.3 - 2021-09-15

- Automated wheel building and deploy to PyPI

## v1.0.2 - 2021-09-15

- Updated install instructions in `README`
- Copy FFTW3 dynamic library into macOS wheel

## v1.0.1 - 2021-09-15

- Add `numpy` dependency

## v1.0 - 2021-09-15

- Initial release
