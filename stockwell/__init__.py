"""
Time-frequency analysis through Stockwell transform.

:copyright:
    2021-2025 Claudio Satriano <satriano@ipgp.fr>

:license:
    GNU General Public License v3.0 or later.
    (https://www.gnu.org/licenses/gpl-3.0.html)
"""
from . import st, sine  # noqa
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
