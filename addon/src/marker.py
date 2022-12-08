from __future__ import annotations

import re
from collections.abc import Iterable
from re import Pattern
from typing import NoReturn

from markdown.inlinepatterns import HTML_RE

from .helpers import InvalidMarkup, Key
from .style import Style


RE_ALL = re.compile(rf"(?P<{Key.CONTENTS}>.*)", flags=re.DOTALL)


class Marker:
    def __init__(self, styles: Iterable[Style]) -> None:
        self.__styles = styles

    def __render(self, string: str) -> str | NoReturn:

        for style in self.__styles:

            self.__check_input(pattern=style.pattern, string=string)

            string = re.sub(
                pattern=style.pattern, repl=style.repl_render, string=string
            )

        return string

    def __unmark(self, string: str) -> str | NoReturn:

        for style in self.__styles:

            self.__check_input(pattern=style.pattern, string=string)

            string = re.sub(
                pattern=style.pattern, repl=style.repl_unmark, string=string
            )

        return string

    def __check_input(self, pattern: Pattern, string: str) -> None | NoReturn:

        for match in re.finditer(pattern, string):

            if re.search(HTML_RE, match[Key.CONTENTS]):
                raise InvalidMarkup

            if re.search(r"\n", match[Key.CONTENTS]):
                raise InvalidMarkup

    def render(self, string: str) -> str:
        return self.__render(string=string)

    def unmark(self, string) -> str:
        return self.__unmark(string=string)

    def mark(self, string: str, markup: str) -> str | NoReturn:

        self.__check_input(pattern=RE_ALL, string=string)

        return f"{markup}{string}{markup}"
