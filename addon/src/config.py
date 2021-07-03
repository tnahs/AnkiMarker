import json
from typing import Iterator, Optional

from addon.src.style import Style

from .helpers import ConfigError, Defaults, Key


class Config:

    __data: dict = {}
    __styles: list[Style] = []

    def __init__(self, data: Optional[dict] = None) -> None:

        self.__data = self.__load() if data is None else data
        self.__validate()
        self.__build_styles()

    @property
    def styles(self) -> list[Style]:
        return self.__styles

    def __load(self) -> dict:

        try:
            with open(Defaults.MARKERS_JSON, "r") as f:
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

        for (name, markup, classnames) in self.__iter_styles():

            if not all([name, markup, len(classnames)]):
                raise ConfigError(
                    f"All styles require: '{Key.NAME}' '{Key.MARKUP}' and '{Key.CLASSNAMES}'."
                )

            if markup != markup[0] * len(markup):
                raise ConfigError(
                    f"Style '{Key.MARKUP}' can only contain one type of character."
                )

            if markup[0] in Defaults.INVALID_CHARACTERS:
                raise ConfigError(
                    f"Style '{Key.MARKUP}' contains invalid characters '{markup[0]}'"
                )

    def __build_styles(self) -> None:

        self.__styles *= 0

        for (name, markup, classnames) in self.__iter_styles():

            self.__styles.append(
                Style(
                    name=name,
                    markup=markup,
                    classnames=classnames,
                ),
            )

    def __iter_styles(self) -> Iterator[tuple[str, str, list[str]]]:

        styles = self.__data.get(Key.STYLES, [])

        parent_classnames = self.__data.get(Key.PARENT_CLASSNAMES, [])

        for style in styles:

            name = style.get(Key.NAME, "")
            markup = style.get(Key.MARKUP, "")
            classnames = style.get(Key.CLASSNAMES, [])

            yield (name, markup, [*parent_classnames, *classnames])
