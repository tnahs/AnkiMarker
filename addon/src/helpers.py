import os
import pathlib

import aqt
import aqt.utils


def is_development_mode() -> bool:
    """Returns a bool for whether or not the the add-on is being developed."""

    return "ANKI_ADDON_DEVELOPMENT" in os.environ


def show_info(message: str) -> None:
    """Shows the user a message related to this add-on."""

    aqt.utils.showInfo(f"{Defaults.NAME}: {message}")


def escape_quotes(string: str) -> str:
    """Escapes single and double quotes within a string."""

    string = string.replace("'", r"\'")
    string = string.replace('"', r"\"")

    return string


class ConfigError(Exception):
    """The exception raised when the addon's configuration has JSON syntax errors,
    missing keys, invalid markup syntax or invalid markup characters."""

    pass


class InvalidMarkup(Exception):
    """The exception raised when a string to be processed i.e. marked, unmarked or
    rendered, contains line-breaks or HTML."""

    pass


class Key:
    """A class defining re-usable strings."""

    ASSETS = "assets"
    CLASSES = "classes"
    CONTENTS = "contents"
    MAIN_CSS = "main.css"
    MARKED = "marked"
    MARKER = "marker"
    MARKERS = "markers"
    MARKERS_JSON = "markers.json"
    MARKERS_CSS = "markers.css"
    MARKUP = "markup"
    NAME = "name"
    PARENT_CLASSES = "parent-classes"
    SRC = "src"
    UNMARKED = "unmarked"
    USER_FILES = "user_files" if not is_development_mode() else "user_files_dev"


class Defaults:
    """A class defining all the add-on's default values."""

    NAME = "AnkiMarker"

    # This name is used for properly setting the path to where the web exports
    # are located. Anki expects this to be: `/_addons/[addon-name]/`. Hard-
    # coding the name can result in missing web assets as depending on how the
    # add-on is installed, its name will be different.
    NAME_INTERNAL = (
        aqt.mw.addonManager.addonFromModule(__name__) if aqt.mw is not None else NAME
    )

    # [path-to-addon]
    ADDON_ROOT = pathlib.Path(__file__).parent.parent
    # [path-to-addon]/user_files
    USER_FILES = ADDON_ROOT / Key.USER_FILES
    # [path-to-addon]/user_files/markers.json
    MARKERS_JSON = USER_FILES / Key.MARKERS_JSON

    # /_addons/[addon-name]
    WEB_ADDON_ROOT = pathlib.Path("/") / "_addons" / NAME_INTERNAL
    # /_addons/[addon-name]/src/assets/main.css
    MAIN_CSS = WEB_ADDON_ROOT / Key.SRC / Key.ASSETS / Key.MAIN_CSS
    # /_addons/[addon-name]/user_files/markers.css
    MARKERS_CSS = WEB_ADDON_ROOT / Key.USER_FILES / Key.MARKERS_CSS

    INVALID_CHARACTERS = r""" & " ' > < \ / ; """.split()
