from appdirs import user_cache_dir
from pathlib import Path
from blib2to3 import pygram
from _black_version import version as __version__

CACHE_DIR = Path(user_cache_dir("black", version=__version__))

pygram.initialize(CACHE_DIR)
