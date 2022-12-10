from __future__ import annotations

import re
from collections.abc import Iterable
from typing import NoReturn

from markdown.inlinepatterns import HTML_RE

from .helpers import InvalidMarkup, Key
from .marker import Marker


ALL_RE = re.compile(rf"(?P<{Key.CONTENTS}>.*)", flags=re.DOTALL)
LINEBREAK_RE = re.compile(r"(\r\n|\r|\n)")


class Processor:
    """A class used for processing text by (1) adding markup (2) removing any markup or
    (3) rendering any markup into HTML.

    Arguments:
        marker: A list of `Markers`s used to mark, unmark and render text.
    """

    def __init__(self, markers: Iterable[Marker]) -> None:
        self._markers = markers

    def mark(self, string: str, markup: str) -> str | NoReturn:
        """Surrounds a string with markup.

        The lazy dog --> ==The lazy dog==
        """

        self._validate_string(string=string, pattern=ALL_RE)

        return f"{markup}{string}{markup}"

    def unmark(self, string: str) -> str | NoReturn:
        """Strips a marked string of all its markup. For example:

        The ==lazy== dog --> The lazy dog
        """

        for marker in self._markers:

            self._validate_string(string=string, pattern=marker.pattern)

            string = re.sub(
                pattern=marker.pattern,
                repl=marker.replacement_unmark,
                string=string,
            )

        return string

    def render(self, string: str) -> str | NoReturn:
        """Renders a marked string into its HTML eqivalent. For exmaple:

        The ==lazy== dog. --> The <marker style="my-markers highlight">lazy</marker> dog
        """

        for marker in self._markers:

            self._validate_string(string=string, pattern=marker.pattern)

            string = re.sub(
                pattern=marker.pattern,
                repl=marker.replacement_render,
                string=string,
            )

        return string

    @staticmethod
    def _validate_string(string: str, pattern: re.Pattern) -> None | NoReturn:
        """Validates that a string matching a pattern does not contain line-breaks or
        HTML."""

        for match in re.finditer(pattern, string):

            # https://stackoverflow.com/a/20056634
            if re.search(LINEBREAK_RE, match[Key.CONTENTS]):
                raise InvalidMarkup

            if re.search(HTML_RE, match[Key.CONTENTS]):
                raise InvalidMarkup
