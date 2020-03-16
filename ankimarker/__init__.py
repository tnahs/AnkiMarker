import sys

from .src import addon, errors


try:
    anki_marker = addon.Addon()
except errors.ConfigError as error:
    # TODO: Document when/why errors are raised and what it prevents.
    sys.stderr.write(f"{anki_marker.name}: {error}")
else:
    anki_marker.setup()
