from __future__ import annotations

import json
from collections.abc import Iterator

from .helpers import ConfigError, Defaults, Key
from .style import Style


class Config:

    __data = {}
    __styles: list[Style] = []

    def __init__(self, data: dict | None = None) -> None:

        self.__data = self.__load() if data is None else data
        self.__validate()
        self.__build_styles()

    def __load(self) -> dict:

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

    def __validate(self) -> None:

        for (name, markup, classes) in self.__iter_styles():

            if not all([name, markup, len(classes)]):
                raise ConfigError(
                    f"Styles require: '{Key.NAME}' '{Key.MARKUP}' and '{Key.CLASSES}'."
                )

            if markup != markup[0] * len(markup):
                raise ConfigError(
                    f"A style '{Key.MARKUP}' can only contain one type of character."
                )

            if markup[0] in Defaults.INVALID_CHARACTERS:
                raise ConfigError(
                    f"A style '{Key.MARKUP}' contains invalid characters '{markup[0]}'"
                )

    def __build_styles(self) -> None:

        self.__styles *= 0

        for (name, markup, classes) in self.__iter_styles():

            self.__styles.append(
                Style(
                    name=name,
                    markup=markup,
                    classes=classes,
                ),
            )

    def __iter_styles(self) -> Iterator[tuple[str, str, list[str]]]:

        styles = self.__data.get(Key.STYLES, [])

        parent_classes = self.__data.get(Key.PARENT_CLASSES, [])

        for style in styles:

            name = style.get(Key.NAME, "")
            markup = style.get(Key.MARKUP, "")
            classes = style.get(Key.CLASSES, [])

            yield (name, markup, [*parent_classes, *classes])

    @property
    def styles(self) -> list[Style]:
        return self.__styles
