import re
from dataclasses import dataclass

from .helpers import Key


@dataclass
class Marker:
    """A class representing a marker style.

    Used to generate its respective HTML tags, replacement strings for rendering and
    unmarking text and its regex pattern for capturing text that matches its markup.
    """

    name: str
    markup: str
    classes: list[str]

    @property
    def tag_open(self) -> str:
        """Returns the marker's opening tag. For example:

        <marker class="my-markers highlight">
        """

        return f"<{Key.MARKER} class=\"{' '.join(self.classes)}\">"

    @property
    def tag_close(self) -> str:
        """Returns the marker's closing tag. For example:

        <marker>
        """

        return f"</{Key.MARKER}>"

    @property
    def replacement_render(self) -> str:
        r"""Returns the marker's replacement string used when rendering. For
        example:

        <marker class="my-markers highlight">\g<contents><marker>

        Note that '\g<NAME>' is a back-reference to the capture group 'NAME'. So this
        string will place the contents of the 'contents' capture group inside the
        marker's opening and closing tags.
        """

        return rf"{self.tag_open}\g<{Key.CONTENTS}>{self.tag_close}"

    @property
    def replacement_unmark(self) -> str:
        r"""Returns the marker's replacement string used then unmarking. For
        example:

        \g<contents>

        Note that '\g<NAME>' is a back-reference to the capture group 'NAME'. So this
        string will extract the contents of the 'contents' capture group.
        """

        return rf"\g<{Key.CONTENTS}>"

    @property
    def pattern(self) -> re.Pattern:
        """Returns a regex pattern that captures the text between a symmetrical markup
        syntax e.g. '~~string~~' would yield 'string'."""

        # markup:  '~'
        # 'm0' --> '~'
        # 'mf' --> '~'
        #
        # markup:  '~~'
        # 'm0' --> '~'
        # 'mf' --> '~~'
        #
        # markup:  '~~~'
        # 'm0' --> '~'
        # 'mf' --> '~~~'
        m0 = re.escape(self.markup[0])
        mf = re.escape(self.markup)

        # 1. Select '~~' only if it's *not* preceded or followed by '~'. This captures
        # the opening markup ignoring those that do not have the exact markup string
        # length. Therefore this will *only* capture '~~' and never capture '~~' inside
        # '~~~'.
        #
        #     (?<!~)~~(?!~)
        #
        # 2. Lazy select anything that is not '~'. This captures the marked text.
        #
        #     ([^~]*?)
        #
        # 3. Again select '~~' only if it's *not* preceded or followed by '~'. This is
        # identical to the first part.
        #
        #     (?<!~)~~(?!~)
        #
        # markup: '~'   --> (?<!~)~(?!~)([^~]*?)~(?!~)
        # markup: '~~'  --> (?<!~)~~(?!~)([^~]*?)~~(?!~)
        # markup: '~~~' --> (?<!~)~~~(?!~)([^~]*?)~~~(?!~)
        return re.compile(
            rf"""
                (?<!{m0}){mf}(?!{m0})
                (?P<{Key.CONTENTS}>[^{m0}]*?)
                (?<!{m0}){mf}(?!{m0})
            """,
            flags=re.VERBOSE,
        )
