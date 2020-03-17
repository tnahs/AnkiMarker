import re
import xml

import markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern


class Defaults:

    tag_name = "anki-marker"
    tag_open = f"<{tag_name}>"
    tag_close = f"</{tag_name}>"


class Marker:
    def __init__(self, addon) -> None:

        marker_extention = MarkerExtension(addon=addon)
        unmarker_extention = UnMarkerExtension(addon=addon)

        self._marker = markdown.Markdown(extensions=[marker_extention])
        self._unmarker = markdown.Markdown(extensions=[unmarker_extention])

    def render(self, string) -> str:
        return self._marker.convert(source=string)

    def mark(self, string, markup) -> str:
        return f"{markup}{string}{markup}"

    def unmark(self, string) -> str:
        # FIXME: Leading spaces are lost: " *abc*" gets unmarked to "abc"

        unmarked = self._unmarker.convert(source=string)

        return self._strip_outer_tags(string=unmarked)

    def _strip_outer_tags(self, string) -> str:

        string = string.replace(Defaults.tag_close + Defaults.tag_open, "\n")
        string = string.replace(Defaults.tag_open, "")
        string = string.replace(Defaults.tag_close, "")

        return string


class BaseMarkerExtension(Extension):
    def __init__(self, addon) -> None:

        self._addon = addon

    def _setup_markdown(self, md) -> None:

        # Deregister all but `html` inline patterns.
        inline_patterns = list(md.inlinePatterns._data.keys())
        for pattern in inline_patterns:

            if pattern == "html":
                continue

            md.inlinePatterns.deregister(pattern)

        # Deregister all default block processor.
        blockprocessors = list(md.parser.blockprocessors._data.keys())
        for processor in blockprocessors:
            md.parser.blockprocessors.deregister(processor)

        # Register single paragraph block processor.
        md.parser.blockprocessors.register(
            item=ParagraphBlockProcessor(md.parser), name="paragraph", priority=0
        )

    def _register_markdown_patterns(
        self, md: markdown.core.Markdown, PatternType: Pattern
    ):

        for (name, markup, classname) in self._addon.styles:

            pattern = self._compile_pattern(markup=markup)
            classnames = [*self._addon.parent_classnames, classname]

            item = PatternType(pattern=pattern, tag="span", classnames=classnames)

            md.inlinePatterns.register(item=item, name=name, priority=0)

    def _compile_pattern(self, markup: str) -> str:
        """ TODO: Document this...

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


class MarkerExtension(BaseMarkerExtension):
    def extendMarkdown(self, md: markdown.core.Markdown) -> None:
        self._setup_markdown(md=md)
        self._register_markdown_patterns(md=md, PatternType=PatternMarked)


class UnMarkerExtension(BaseMarkerExtension):
    def extendMarkdown(self, md: markdown.core.Markdown) -> None:
        self._setup_markdown(md=md)
        self._register_markdown_patterns(md=md, PatternType=PatternUnMarked)


class PatternMarked(Pattern):
    def __init__(self, pattern: str, tag: str, classnames: str, **kwargs) -> None:
        super().__init__(pattern)

        self._tag = tag
        self._classnames = classnames

    def handleMatch(self, match: re.Match) -> xml.etree.ElementTree.Element:

        classnames = " ".join(self._classnames)

        element = xml.etree.ElementTree.Element(self._tag)
        element.text = match.group(2)
        element.set("class", classnames)

        return element


class PatternUnMarked(Pattern):
    def __init__(self, pattern: str, **kwargs) -> None:
        super().__init__(pattern)

    def handleMatch(self, match: re.Match) -> str:
        return match.group(2)


class ParagraphBlockProcessor(BlockProcessor):
    def test(self, parent, block) -> bool:
        return True

    def run(self, parent, blocks) -> None:

        block = blocks.pop(0)

        if not block.strip():
            return

        p = xml.etree.ElementTree.SubElement(parent, Defaults.tag_name)
        p.text = block.lstrip()
