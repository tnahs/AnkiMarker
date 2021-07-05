import os
import pathlib
from enum import Enum

import aqt


class ConfigError(Exception):
    pass


class InvalidMarkup(Exception):
    pass


class E_Filter(str, Enum):
    MARKED = "marked"
    UNMARKED = "unmarked"


class Key:
    ASSETS = "assets"
    CLASSES = "classes"
    CONTENTS = "contents"
    MAIN_CSS = "main.css"
    MARKER = "marker"
    MARKERS_JSON = "markers.json"
    MARKERS_CSS = "markers.css"
    MARKUP = "markup"
    NAME = "name"
    PARENT_CLASSES = "parent-classes"
    SRC = "src"
    STYLES = "styles"
    USER_FILES = (
        "user_files"
        if "ANKI_ADDON_DEVELOPMENT" not in os.environ
        else "user_files__dev"
    )


class Defaults:
    NAME = "AnkiMarker"
    NAME_INTERNAL = (
        aqt.mw.addonManager.addonFromModule(__name__) if aqt.mw is not None else NAME
    )

    # [/absolute/path/to/addon]
    ADDON_ROOT = pathlib.Path(__file__).parent.parent
    # [/absolute/path/to/addon]/user_files
    USER_FILES = ADDON_ROOT / Key.USER_FILES
    # [/absolute/path/to/addon]/user_files/markers.json
    MARKERS_JSON = USER_FILES / Key.MARKERS_JSON

    # /_addons
    WEB_ROOT = pathlib.Path("/_addons")
    # /_addons/[addon-name]/src/assets/main.css
    MAIN_CSS = WEB_ROOT / NAME_INTERNAL / Key.SRC / Key.ASSETS / Key.MAIN_CSS
    # /_addons/[addon-name]/user_files/markers.css
    MARKERS_CSS = WEB_ROOT / NAME_INTERNAL / Key.USER_FILES / Key.MARKERS_CSS

    INVALID_CHARACTERS = r""" & " ' > < \ / ; """.split()
