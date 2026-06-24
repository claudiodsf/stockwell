Theory
======

This page describes the mathematical background of the Stockwell transform
(S-transform) and its implementation in this package.


Continuous S-Transform
----------------------

The S-transform of a continuous signal :math:`x(t)` is defined by :cite:t:`stockwell1996`:

.. math::

   S_x(t, f) = \int_{-\infty}^{\infty} x(\tau) \,
               w(t - \tau, f) \,
               e^{-j 2\pi f \tau} \, d\tau

where :math:`w(t, f)` is a frequency-dependent window function.  The
choice of window determines the time-frequency resolution trade-off;
two window types are available (see :ref:`Window functions <windows>` below).

The inverse S-transform recovers the original signal by integrating over
time and frequency:

.. math::

   x(\tau) = \int_{-\infty}^{\infty}
             \left[ \int_{-\infty}^{\infty} S_x(t, f) \, dt \right]
             e^{j 2\pi f \tau} \, df


Discrete Implementation
-----------------------

This package implements the discrete S-transform in the frequency domain,
following the fast algorithm of :cite:t:`brown2010` (see also
:cite:t:`stockwell1999`).
Given a discrete signal :math:`x[k]` of length :math:`N`, the algorithm
proceeds as follows:

1. Compute the discrete Fourier transform (DFT) :math:`X[m]` of
   :math:`x[k]`, where :math:`m = 0, \dots, N-1` is the frequency bin
   index.

2. Apply the Hilbert transform in the frequency domain: double the positive
   frequencies and zero the negative frequencies.

3. For each frequency voice :math:`n` (from ``lo`` to ``hi``), where
   :math:`n` is the frequency row index in the output S-transform:

   a. Compute the frequency-domain window :math:`W[n, m]`.
   b. Shift the spectrum: multiply :math:`X[m]` by
      :math:`W[n, (m-n) \bmod N]`.
   c. Inverse DFT to obtain the :math:`n`-th row of the S-transform.

The result is a complex matrix of shape :math:`(\text{nfreqs}, N)`, where the
first dimension runs over frequency and the second over time.


.. _windows:

Window functions
----------------

The S-transform is implemented in the frequency domain: for each frequency
voice :math:`n`, the spectrum :math:`X[m]` is multiplied by a shifted
frequency-domain window :math:`W[n, m]` and then inverse-transformed.

Two window functions are available.  Both depend on the :ref:`gamma
parameter <gamma-parameter>` described below.

Gaussian window (default, ``win_type='gauss'``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the time domain the window is a scaled Gaussian, following the
original definition of :cite:t:`stockwell1996`:

.. math::

   w(t, f) = \frac{|f|}{\gamma\sqrt{2\pi}} \,
             e^{-t^2 f^2 / (2\gamma^2)}

Its Fourier transform gives the frequency-domain form used in the
implementation:

.. math::

   G(n, m, \gamma) = \exp\left(
       -\frac{2\pi^2 m^2 \gamma^2}{n^2}
   \right)

where :math:`n` is the frequency voice index and :math:`m` the frequency
sample index.

.. note::

   The `Wikipedia article on the S-transform`_ uses an alternative Gaussian
   convention: :math:`|f| e^{-\pi t^2 f^2}`, whose frequency-domain
   counterpart is :math:`e^{-\pi m^2 / n^2}`.  Both forms are equivalent up
   to a different choice of the :math:`\gamma` scaling.  This package
   follows the original convention of :cite:t:`stockwell1996`.

Kazemi window (``win_type='kazemi'``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Introduced by :cite:t:`kazemi2014`, this window provides sharper frequency
localisation.  In the frequency domain:

.. math::

   K(n, m, \gamma) = \frac{1}{1 + \left( \dfrac{m^2 \gamma}{n} \right)^2}

.. _gamma-parameter:

Gamma parameter
^^^^^^^^^^^^^^^

The parameter :math:`\gamma > 0` (default 1) controls the number of Fourier
sinusoidal periods within one standard deviation of the window: raising
:math:`\gamma` increases frequency resolution at the expense of time
resolution, and vice versa.  Typical values are around 1; very large values
produce an extremely narrow window in time.


Hilbert Transform
-----------------

The Hilbert transform :math:`\mathcal{H}\{x(t)\}` of a real signal
:math:`x(t)` is computed in the frequency domain:

.. math::

   \mathcal{F}\{\mathcal{H}\{x\}\}[m] =
   \begin{cases}
       2 \, X[m] & 0 < m < \lceil N/2 \rceil \\
       X[m]      & m = 0 \;\text{or}\; m = N/2 \;(\text{if } N \text{ even}) \\
       0         & m \geq \lfloor N/2 \rfloor + 1
   \end{cases}

where :math:`\mathcal{F}` denotes the Fourier transform and
:math:`X[m] = \mathcal{F}\{x\}[m]`.  In words: positive frequencies
(excluding DC and Nyquist) are doubled, negative frequencies are zeroed,
and DC (and Nyquist for even :math:`N`) are left unchanged.


Sine Tapers
-----------

The :math:`K`-th sine taper of length :math:`N` is defined as
:cite:t:`riedel1979`:

.. math::

   w_K[n] = \sqrt{\frac{2}{N+1}} \,
            \sin\left( \frac{\pi (K+1) (n+1)}{N+1} \right),
            \quad n = 0, \dots, N-1


Acknowledgments
---------------

The C implementation of the Stockwell transform is based on original code
from the `NIMH MEG Core Facility`_, released into the public domain.

The following modifications have been made to the original code:

* **Windows compatibility**: added portable defines and MSVC export
  declarations.
* **ctypes interface** (v1.1): replaced Python C extension modules with
  :mod:`ctypes`-based loading for easier cross-platform packaging.
* **Gamma parameter** (v1.0.5): added :math:`\gamma` to control the
  time-frequency resolution trade-off.
* **Kazemi window** (v1.0.5): added the alternative window of
  :cite:t:`kazemi2014` alongside the original Gaussian.
* **FFTW plan caching**: static FFTW plans are reused across calls,
  with proper cleanup at process exit to prevent segfaults.
* **Hilbert phase fix**: corrected the Hilbert phase by no longer shifting
  the spectrum in frequency when multiplying by the window, preserving the
  correct instantaneous phase in the Stockwell spectrum.
* **Input validation**: reject empty arrays and non-integer ``lo``/``hi``
  parameters.


.. _NIMH MEG Core Facility:
   https://kurage.nimh.nih.gov/meglab/Meg/Stockwell

.. _Wikipedia article on the S-transform:
   https://en.wikipedia.org/wiki/S_transform


References
----------

.. bibliography:: refs.bib
   :style: unsrt
