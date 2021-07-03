from addon.src.helpers import Tag
from addon.src.marker import Marker


def test__valid_basic(marker: Marker) -> None:

    marked = " *Style0* **Style1** ~Style2~ ~~Style3~~ "
    unmarked = " Style0 Style1 Style2 Style3 "

    rendered = (
        f"{Tag.OPEN}"
        f' <span class="parent-style style0">Style0</span>'
        f' <span class="parent-style style1">Style1</span>'
        f' <span class="parent-style style2">Style2</span>'
        f' <span class="parent-style style3">Style3</span>'
        f" {Tag.CLOSE}"
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_tags(marker: Marker) -> None:

    marked = " *ABC* <div><p><strong>abc</strong></p></div> *ABC* "
    unmarked = " ABC <div><p><strong>abc</strong></p></div> ABC "

    rendered = (
        f"{Tag.OPEN}"
        f' <span class="parent-style style0">ABC</span>'
        f" <div><p><strong>abc</strong></p></div>"
        f' <span class="parent-style style0">ABC</span>'
        f" {Tag.CLOSE}"
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_entities(marker: Marker) -> None:

    marked = " *ABC* *&amp;* *&#38;* *&#x26;* *ABC* "
    unmarked = " ABC &amp; &#38; &#x26; ABC "

    rendered = (
        f"{Tag.OPEN}"
        f' <span class="parent-style style0">ABC</span>'
        f' <span class="parent-style style0">&amp;</span>'
        f' <span class="parent-style style0">&#38;</span>'
        f' <span class="parent-style style0">&#x26;</span>'
        f' <span class="parent-style style0">ABC</span>'
        f" {Tag.CLOSE}"
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_linebreak1(marker: Marker) -> None:

    marked = " *ABC*\n*ABC* "
    unmarked = " ABC\nABC "

    rendered = (
        f"{Tag.OPEN}"
        f' <span class="parent-style style0">ABC</span>'
        f'\n<span class="parent-style style0">ABC</span>'
        f" {Tag.CLOSE}"
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_linebreak2(marker: Marker) -> None:

    marked = " *ABC\nABC* "
    unmarked = " ABC\nABC "

    rendered = (
        f'{Tag.OPEN} <span class="parent-style style0">ABC\nABC</span> {Tag.CLOSE}'
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)
