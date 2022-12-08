import pytest

from addon.src.helpers import InvalidMarkup, Key
from addon.src.marker import Marker


def test__valid_basic(marker: Marker) -> None:

    marked = " *Style0* **Style1** ~Style2~ ~~Style3~~ "
    unmarked = " Style0 Style1 Style2 Style3 "

    rendered = (
        f' <{Key.MARKER} class="parent-style style0">Style0</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-style style1">Style1</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-style style2">Style2</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-style style3">Style3</{Key.MARKER}>'
        f" "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_tags(marker: Marker) -> None:

    marked = " *ABC* <div><p><strong>ABC</strong></p></div> *ABC* "
    unmarked = " ABC <div><p><strong>ABC</strong></p></div> ABC "

    rendered = (
        f' <{Key.MARKER} class="parent-style style0">ABC</{Key.MARKER}>'
        f" <div><p><strong>ABC</strong></p></div>"
        f' <{Key.MARKER} class="parent-style style0">ABC</{Key.MARKER}>'
        f" "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_entities(marker: Marker) -> None:

    marked = " *ABC* *&amp;* *&#38;* *&#x26;* *ABC* "
    unmarked = " ABC &amp; &#38; &#x26; ABC "

    rendered = (
        f' <{Key.MARKER} class="parent-style style0">ABC</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-style style0">&amp;</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-style style0">&#38;</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-style style0">&#x26;</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-style style0">ABC</{Key.MARKER}>'
        f" "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_linebreak(marker: Marker) -> None:

    marked = " *ABC*\n*ABC* "
    unmarked = " ABC\nABC "

    rendered = (
        f' <{Key.MARKER} class="parent-style style0">ABC</{Key.MARKER}>'
        f'\n<{Key.MARKER} class="parent-style style0">ABC</{Key.MARKER}>'
        f" "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_paragraph1(marker: Marker) -> None:

    marked = " start <p>*ABC*</p> end "
    unmarked = " start <p>ABC</p> end "

    rendered = (
        f" start <p>"
        f'<{Key.MARKER} class="parent-style style0">ABC</{Key.MARKER}>'
        f"</p> end "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_paragraph2(marker: Marker) -> None:

    marked = "<p>ABC *ABC* ABC</p>"
    unmarked = "<p>ABC ABC ABC</p>"

    rendered = (
        f'<p>ABC <{Key.MARKER} class="parent-style style0">ABC</{Key.MARKER}> ABC</p>'
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__invalid_with_linebreak(marker: Marker) -> None:

    marked = " *ABC\nABC* "

    with pytest.raises(InvalidMarkup):
        marker.render(string=marked)

    with pytest.raises(InvalidMarkup):
        marker.unmark(string=marked)


def test__invalid_with_paragraph(marker: Marker) -> None:

    marked = "<p>ABC *ABC ABC</p><p>ABC ABC* ABC</p>"

    with pytest.raises(InvalidMarkup):
        marker.render(string=marked)

    with pytest.raises(InvalidMarkup):
        marker.unmark(string=marked)
