"""
Time-frequency analysis through Stockwell transform.

:copyright:
    2021-2026 Claudio Satriano <satriano@ipgp.fr>

:license:
    GNU General Public License v3.0 or later.
    (https://www.gnu.org/licenses/gpl-3.0.html)
"""
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
# pylint: disable=import-outside-toplevel


# Lazy import of modules to avoid requiring compiled libraries at import time
def __getattr__(name):
    if name == 'st':
        import importlib
        return importlib.import_module('.st', __name__)
    if name == 'sine':
        import importlib
        return importlib.import_module('.sine', __name__)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
