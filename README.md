# Stockwell

Time-frequency analysis through Stockwell transform.

## Installation

Make sure that you have [FFTW](http://www.fftw.org) installed.
For example:

```bash
# macOS
brew install fftw

# debian or ubuntu
sudo apt-get install libfftw3-dev
```

Then install this python package using pip:

```bash
pip install .
```

Or, alternatively, in "editable" mode:

```bash
pip install -e .
```

## Usage

From the command line:

```bash
stockwell file.sac
```

It will produce `file.sac.pdf` with the time-frequency representation of the signal.

Example usage from python:

```python
import numpy as np
from scipy.signal import chirp
import matplotlib.pyplot as plt
from stockwell import st

t = np.linspace(0, 10, 5001)
w = chirp(t, f0=12.5, f1=2.5, t1=10, method='linear')

fmin = 0  # Hz
fmax = 25  # Hz
df = 1./(t[-1]-t[0])  # sampling step in frequency domain (Hz)
fmin_samples = int(fmin/df)
fmax_samples = int(fmax/df)
stock = st.st(w, fmin_samples, fmax_samples)
extent = (t[0], t[-1], fmin, fmax)

fig, ax = plt.subplots(2, 1, sharex=True)
ax[0].plot(t, w)
ax[0].set(ylabel='amplitude')
ax[1].imshow(np.abs(stock), origin='lower', extent=extent)
ax[1].axis('tight')
ax[1].set(xlabel='time (s)', ylabel='frequency (Hz)')
plt.show()
```
You should get the following output:
![stockwell.png](stockwell.png)

You can also compute the inverse Stockwell transform, ex:

```python
inv_stock = st.ist(stock, fmin_samples, fmax_samples)
fig, ax = plt.subplots(2, 1, sharex=True)
ax[0].plot(t, w, label='original signal')
ax[0].plot(t, inv_stock, label='inverse Stockwell')
ax[0].set(ylabel='amplitude')
ax[0].legend(loc='upper right')
ax[1].plot(t, w - inv_stock)
ax[1].set_xlim(0, 10)
ax[1].set(xlabel='time (s)', ylabel='amplitude difference')
plt.show()
```
![inv_stockwell.png](inv_stockwell.png)


## References

Stockwell, R.G., Mansinha, L. & Lowe, R.P., 1996. Localization of the complex spectrum: the S transform, IEEE Trans. Signal Process., 44(4), 998–1001, doi:[10.1109/78.492555](https://doi.org/10.1109/78.492555)

[S transform on Wikipedia](https://en.wikipedia.org/wiki/S_transform).
