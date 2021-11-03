"""Time-frequency analysis through Stockwell transform."""
from .lib import st  #NOQA
from .lib import sine  #NOQA
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
