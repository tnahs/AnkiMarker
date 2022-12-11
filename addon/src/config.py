from __future__ import annotations

import json
from collections.abc import Iterator

from .helpers import ConfigError, Defaults, Key
from .marker import Marker


class Config:
    """A class used to store the add-on's configuration.

    During testing, the `data` argument can be supplied to bypass loading the
    configuration from disk.

    The data structure is as follows:

    {
        "parent-classname": "my-markers",
        "markers": [
            {
                "name": "Highlight",
                "markup": "==",
                "classname": "highlight"
            },
            ...
        ]
    }
    """

    _data: dict = {}
    _markers: list[Marker] = []

    def __init__(self, data: dict | None = None) -> None:
        self._data = self._load() if data is None else data
        self._validate()
        self._build_markers()

    @property
    def markers(self) -> list[Marker]:
        return self._markers

    def _load(self) -> dict:
        """Loads the add-on's configuration from disk."""

        try:
            with open(Defaults.MARKERS_JSON) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ConfigError(
                f"Missing {Key.MARKERS_JSON} in {Defaults.MARKERS_JSON.parent}."
            )
        except json.JSONDecodeError:
            raise ConfigError(
                f"Cannot read {Key.MARKERS_JSON} in {Defaults.MARKERS_JSON.parent}."
            )

        return data

    def _validate(self) -> None:
        """Validates the add-on's configuration."""

        for (name, markup, _, classname) in self._iter_raw_config():

            if not all([name, markup, classname]):
                raise ConfigError(
                    f"All markers require: '{Key.NAME}', '{Key.MARKUP}' and "
                    f"'{Key.CLASSNAME}'."
                )

            if markup != markup[0] * len(markup):
                raise ConfigError(
                    f"A marker's '{Key.MARKUP}' can only contain one type of character."
                )

            if markup[0] in Defaults.INVALID_CHARACTERS:
                raise ConfigError(
                    f"Marker '{name}' contains an invalid character: '{markup[0]}'. "
                    f"Invalid characters are: {' '.join(Defaults.INVALID_CHARACTERS)}."
                )

    def _build_markers(self) -> None:
        """Builds a list of `Marker`s from the raw config data."""

        self._markers *= 0

        for (name, markup, parent_classname, classname) in self._iter_raw_config():

            classnames = [parent_classname, classname]
            classnames = list(filter(None, classnames))

            self._markers.append(
                Marker(
                    name=name,
                    markup=markup,
                    classnames=classnames,
                ),
            )

    def _iter_raw_config(self) -> Iterator[tuple[str, str, str, str]]:
        """Iterates through the raw config data and returns a tuple for each marker
        containing the name, its markup, its parent classname and its classname."""

        parent_classname = self._data.get(Key.PARENT_CLASSNAME, "")

        for marker in self._data.get(Key.MARKERS, []):

            name = marker.get(Key.NAME, "")
            markup = marker.get(Key.MARKUP, "")
            classname = marker.get(Key.CLASSNAME, "")

            # ("Highlight", "==", "my-markers", "highlight")
            yield (name, markup, parent_classname, classname)
