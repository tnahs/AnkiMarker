import re
from typing import List

import markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern


class Defaults:

    tag_name = "anki-marker"
    tag_open = f"<{tag_name}>"
    tag_close = f"</{tag_name}>"


class AnkiMarker:
    def __init__(self, config: dict):

        self._config = config

        marker_extention = Marker(config=self._config)
        unmarker_extention = UnMarker(config=self._config)

        self._marker = markdown.Markdown(extensions=[marker_extention])
        self._unmarker = markdown.Markdown(extensions=[unmarker_extention])

    def mark(self, string) -> str:
        return self._marker.convert(source=string)

    def unmark(self, string) -> str:

        unmarked = self._unmarker.convert(source=string)

        return self._strip_outer_tags(string=unmarked)

    def _strip_outer_tags(self, string) -> str:

        string = string.replace(Defaults.tag_close + Defaults.tag_open, "\n")
        string = string.replace(Defaults.tag_open, "")
        string = string.replace(Defaults.tag_close, "")

        return string


class BaseMarker(Extension):
    def __init__(self, config) -> None:
        self._config = config

    @property
    def _parent_classnames(self) -> List[str]:
        return self._config.get("parent_classnames", [])

    @property
    def _styles(self) -> List[dict]:
        return self._config.get("styles", [{}])

    def _setup_markdown(self, md) -> None:

        # Deregister all default inline patterns.
        inline_patterns = list(md.inlinePatterns._data.keys())
        for pattern in inline_patterns:
            md.inlinePatterns.deregister(pattern)

        # Deregister all default block processor.
        blockprocessors = list(md.parser.blockprocessors._data.keys())
        for processor in blockprocessors:
            md.parser.blockprocessors.deregister(processor)

        # Register single paragraph block processor.
        md.parser.blockprocessors.register(
            item=ParagraphProcessor(md.parser), name="paragraph", priority=1110
        )

    def _register_markdown_patterns(
        self, md: markdown.core.Markdown, PatternType: Pattern
    ):

        if not self._styles:
            return

        for style in self._styles:

            name = style.get("name", None)
            markup = style.get("markup", None)
            classname = style.get("classname", None)

            if not all([name, markup, classname]):
                continue

            pattern = self._compile_pattern(markup=markup)
            classnames = [*self._parent_classnames, classname]

            item = PatternType(pattern=pattern, tag="span", classnames=classnames)

            md.inlinePatterns.register(item=item, name=name, priority=0)

    def _compile_pattern(self, markup: str) -> str:
        """ TODO: Document.

        I'm so sorry. This prevents text marked with `~` from having
        overlapping matches with those with `~~`.

        markup: `~` --> (?<!~)~(?!~)([^~]*?)~(?!~)
        markup: `~~` --> (?<!~)~~(?!~)([^~]*?)~~(?!~)
        markup: `~~~` --> (?<!~)~~~(?!~)([^~]*?)~~~(?!~)

        `(?<!~)`

        `~~`

        `(?!~)`

        `([^~]*?)`

        `~~`

        `(?!~)`

        via. https://stackoverflow.com/a/51083965
        """

        # markup: `~`
        # `m0` --> `~`
        # `mf` --> `~`
        #
        # markup: `~~`
        # `m0` --> `~`
        # `mf` --> `~~`
        #
        # markup: `~~~`
        # `m0` --> `~`
        # `mf` --> `~~~`
        m0 = re.escape(markup[0])
        mf = re.escape(markup)

        return fr"(?<!{m0}){mf}(?!{m0})([^{m0}]*?){mf}(?!{m0})"


class Marker(BaseMarker):
    def extendMarkdown(self, md: markdown.core.Markdown, md_globals: dict) -> None:
        self._setup_markdown(md=md)
        self._register_markdown_patterns(md=md, PatternType=PatternMarked)


class UnMarker(BaseMarker):
    def extendMarkdown(self, md: markdown.core.Markdown, md_globals: dict) -> None:
        self._setup_markdown(md=md)
        self._register_markdown_patterns(md=md, PatternType=PatternUnMarked)


class PatternMarked(markdown.inlinepatterns.Pattern):
    def __init__(self, pattern: str, tag: str, classnames: str, **kwargs) -> None:
        super().__init__(pattern)

        self._tag = tag
        self._classnames = classnames

    def handleMatch(self, match: re.Match):

        classnames = " ".join(self._classnames)

        element = markdown.util.etree.Element(self._tag)
        element.text = match.group(2)
        element.set("class", classnames)

        return element


class PatternUnMarked(Pattern):
    def __init__(self, pattern: str, **kwargs) -> None:
        super().__init__(pattern)

    def handleMatch(self, match: re.Match):
        return match.group(2)


class ParagraphProcessor(BlockProcessor):
    def test(self, parent, block):
        return True

    def run(self, parent, blocks):

        block = blocks.pop(0)

        if not block.strip():
            return

        p = markdown.util.etree.SubElement(parent, Defaults.tag_name)
        p.text = block.lstrip()


if __name__ == "__main__":

    CONFIG = {
        "parent_classnames": ["marker"],
        "styles": [
            {"name": "Accent", "markup": "*", "classname": "accent"},
            {"name": "Bold", "markup": "**", "classname": "bold"},
            {"name": "Highlight", "markup": "==", "classname": "highlight"},
            {"name": "Masculine", "markup": "++", "classname": "masculine"},
            {"name": "Feminine", "markup": "~~", "classname": "feminine"},
        ],
    }

    marker = AnkiMarker(config=CONFIG)

    print()
    print(
        marker.mark(
            """
            This is a ~~sentence~~ that has *many* words that are **modified** with ==custom== ++markdown++!\n
            What happens if we add a second paragraph after a line-break. And some extra text.
            """
        )
    )
    print()
    print(
        marker.unmark(
            """
            This is a ~~sentence~~ that has *many* words that are **modified** with ==custom== ++markdown++!\n
            What happens if we add a second paragraph after a line-break. And some extra text.
            """
        )
    )
    print()
