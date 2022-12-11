__version__ = "0.3.0"

import sys


if "pytest" not in sys.modules:
    from .src.addon import AnkiMarker
    from .src.helpers import ConfigError, show_info

    try:
        addon = AnkiMarker()
    except ConfigError as error:
        show_info(str(error))
    else:
        addon.setup()
