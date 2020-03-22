import sys

from .src import AnkiMarker, errors


try:
    addon = AnkiMarker()
except errors.ConfigError as error:
    # Prevents AnkiMarker from hooking to Anki if there are any config errors.
    # See `../tests.py` and `ankimark.src.AnkiMarker._validate_config()`
    sys.stderr.write(f"{AnkiMarker.name}: {error}")
else:

    try:
        addon.setup()
    except ImportError:
        # Anki is not currently running. Tests are being run. Prevents
        # AnkiMarker from hooking to Anki if Anki is not running.
        pass
