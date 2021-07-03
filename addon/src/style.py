import re
from dataclasses import dataclass


@dataclass
class Style:
    name: str
    markup: str
    classnames: list[str]

    @property
    def regex(self) -> str:
        """Return a regex that captures text between symmetrical markup."""

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
        return fr"(?<!{m0}){mf}(?!{m0})(?P<contents>[^{m0}]*?)(?<!{m0}){mf}(?!{m0})"
