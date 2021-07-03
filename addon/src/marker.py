import re
from typing import Iterable
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from markdown import Markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import HTML_RE, HtmlInlineProcessor, Pattern

from .helpers import Key, Tag
from .style import Style


class Marker:
    def __init__(self, styles: Iterable[Style]) -> None:

        self.__marker = Markdown(
            extensions=[MarkerExtension(styles=styles)],
        )
        self.__unmarker = Markdown(
            extensions=[UnMarkerExtension(styles=styles)],
        )

    def render(self, string: str) -> str:
        return self.__marker.convert(source=string)

    def mark(self, string: str, markup: str) -> str:
        return f"{markup}{string}{markup}"

    def unmark(self, string) -> str:

        string = self.__unmarker.convert(source=string)
        string = string.replace(Tag.CLOSE + Tag.OPEN, "\n")
        string = string.replace(Tag.OPEN, "")
        string = string.replace(Tag.CLOSE, "")

        return string


class ParagraphBlockProcessor(BlockProcessor):
    # https://python-markdown.github.io/extensions/api/#blockprocessors

    def test(self, parent: Element, block: str) -> bool:
        return True

    def run(self, parent: Element, blocks: list[str]) -> None:

        block = blocks.pop(0)

        if not block.strip():
            return

        paragraph = ElementTree.SubElement(parent, Tag.NAME)
        paragraph.text = block


class BaseMarkerExtension(Extension):
    def __init__(self, styles: Iterable[Style]) -> None:
        self.__styles = styles

    @property
    def styles(self) -> Iterable[Style]:
        return self.__styles

    def setup_markdown(self, markdown: Markdown) -> None:

        # Deregister all inline patterns.

        for pattern in markdown.inlinePatterns._data.copy():
            markdown.inlinePatterns.deregister(pattern)

        # Register single 'html' inline pattern.

        markdown.inlinePatterns.register(
            item=HtmlInlineProcessor(HTML_RE, markdown),
            name="html",
            priority=90,
        )

        # Deregister all default block processor.

        for processor in markdown.parser.blockprocessors._data.copy():
            markdown.parser.blockprocessors.deregister(processor)

        # Register single paragraph block processor.

        markdown.parser.blockprocessors.register(
            item=ParagraphBlockProcessor(markdown.parser),
            name="paragraph",
            priority=0,
        )


class MarkerExtension(BaseMarkerExtension):
    def extendMarkdown(self, markdown: Markdown) -> None:

        self.setup_markdown(markdown=markdown)

        for style in self.styles:

            markdown.inlinePatterns.register(
                item=PatternMarker(
                    regex=style.regex,
                    classnames=style.classnames,
                ),
                name=style.name,
                priority=0,
            )


class PatternMarker(Pattern):
    def __init__(self, regex: str, classnames: list[str]) -> None:
        super().__init__(regex)

        self.__classnames = classnames

    @property
    def classnames(self) -> str:
        return " ".join(self.__classnames)

    def handleMatch(self, match: re.Match) -> ElementTree.Element:

        element = ElementTree.Element("span")
        element.text = match[Key.CONTENTS]
        element.set("class", self.classnames)

        return element


class UnMarkerExtension(BaseMarkerExtension):
    def extendMarkdown(self, markdown: Markdown) -> None:

        self.setup_markdown(markdown=markdown)

        for style in self.styles:

            markdown.inlinePatterns.register(
                item=PatternUnMarker(regex=style.regex),
                name=style.name,
                priority=0,
            )


class PatternUnMarker(Pattern):
    def __init__(self, regex: str) -> None:
        super().__init__(regex)

    def handleMatch(self, match: re.Match) -> str:
        return match[Key.CONTENTS]
