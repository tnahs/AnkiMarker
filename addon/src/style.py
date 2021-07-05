import re
from dataclasses import dataclass
from typing import List

from .helpers import Key


@dataclass
class Style:
    name: str
    markup: str
    classes: List[str]

    @property
    def tag_open(self) -> str:
        return f"<{Key.MARKER} class=\"{' '.join(self.classes)}\">"

    @property
    def tag_close(self) -> str:
        return f"</{Key.MARKER}>"

    @property
    def repl_render(self) -> str:
        return fr"{self.tag_open}\g<{Key.CONTENTS}>{self.tag_close}"

    @property
    def repl_unmark(self) -> str:
        return fr"\g<{Key.CONTENTS}>"

    @property
    def pattern(self) -> re.Pattern:
        """Return a regex pattern that captures between symmetrical markup."""

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

        """ Select '~~' only if it's *not* preceded or followed by '~'. This
        captures our opening markup ignoring those that do not have the exact
        markup string length. Therefore this will *only* capture '~~' and never
        capture '~~' inside '~~~'.

            (?<!~)~~(?!~)

        Lazy select anything that is not '~'. This captures the marked text.

            ([^~]*?)

        Again select '~~' only if it's *not* preceded or followed by '~'. This
        is identical to the first part.

            (?<!~)~~(?!~)

        markup: '~' --> (?<!~)~(?!~)([^~]*?)~(?!~)
        markup: '~~' --> (?<!~)~~(?!~)([^~]*?)~~(?!~)
        markup: '~~~' --> (?<!~)~~~(?!~)([^~]*?)~~~(?!~)
        """
        return re.compile(
            fr"""
                #
                (?<!{m0}){mf}(?!{m0})
                #
                (?P<{Key.CONTENTS}>[^{m0}]*?)
                #
                (?<!{m0}){mf}(?!{m0})
            """,
            flags=re.VERBOSE,
        )
