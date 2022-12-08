__version__ = "0.2.0"

import sys


if "pytest" not in sys.modules:
    from .src.addon import AnkiMarker

    addon = AnkiMarker()
    addon.setup()
