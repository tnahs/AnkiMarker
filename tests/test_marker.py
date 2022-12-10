import pytest

from addon.src.helpers import InvalidMarkup, Key
from addon.src.processor import Processor


def test__valid_basic(marker: Processor) -> None:
    marked = " *Marker0* **Marker1** ~Marker2~ ~~Marker3~~ "
    unmarked = " Marker0 Marker1 Marker2 Marker3 "

    rendered = (
        f' <{Key.MARKER} class="parent-marker marker0">Marker0</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-marker marker1">Marker1</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-marker marker2">Marker2</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-marker marker3">Marker3</{Key.MARKER}>'
        f" "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_tags(marker: Processor) -> None:
    marked = " *ABC* <div><p><strong>ABC</strong></p></div> *ABC* "
    unmarked = " ABC <div><p><strong>ABC</strong></p></div> ABC "

    rendered = (
        f' <{Key.MARKER} class="parent-marker marker0">ABC</{Key.MARKER}>'
        f" <div><p><strong>ABC</strong></p></div>"
        f' <{Key.MARKER} class="parent-marker marker0">ABC</{Key.MARKER}>'
        f" "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_entities(marker: Processor) -> None:
    marked = " *ABC* *&amp;* *&#38;* *&#x26;* *ABC* "
    unmarked = " ABC &amp; &#38; &#x26; ABC "

    rendered = (
        f' <{Key.MARKER} class="parent-marker marker0">ABC</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-marker marker0">&amp;</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-marker marker0">&#38;</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-marker marker0">&#x26;</{Key.MARKER}>'
        f' <{Key.MARKER} class="parent-marker marker0">ABC</{Key.MARKER}>'
        f" "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_linebreak(marker: Processor) -> None:
    marked = " *ABC*\n*ABC* "
    unmarked = " ABC\nABC "

    rendered = (
        f' <{Key.MARKER} class="parent-marker marker0">ABC</{Key.MARKER}>'
        f'\n<{Key.MARKER} class="parent-marker marker0">ABC</{Key.MARKER}>'
        f" "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_paragraph1(marker: Processor) -> None:
    marked = " start <p>*ABC*</p> end "
    unmarked = " start <p>ABC</p> end "

    rendered = (
        f" start <p>"
        f'<{Key.MARKER} class="parent-marker marker0">ABC</{Key.MARKER}>'
        f"</p> end "
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__valid_with_paragraph2(marker: Processor) -> None:
    marked = "<p>ABC *ABC* ABC</p>"
    unmarked = "<p>ABC ABC ABC</p>"

    rendered = (
        f'<p>ABC <{Key.MARKER} class="parent-marker marker0">ABC</{Key.MARKER}> ABC</p>'
    )

    assert rendered == marker.render(string=marked)
    assert unmarked == marker.unmark(string=marked)


def test__invalid_with_linebreak(marker: Processor) -> None:
    marked = " *ABC\nABC* "

    with pytest.raises(InvalidMarkup):
        marker.render(string=marked)

    with pytest.raises(InvalidMarkup):
        marker.unmark(string=marked)


def test__invalid_with_paragraph(marker: Processor) -> None:
    marked = "<p>ABC *ABC ABC</p><p>ABC ABC* ABC</p>"

    with pytest.raises(InvalidMarkup):
        marker.render(string=marked)

    with pytest.raises(InvalidMarkup):
        marker.unmark(string=marked)
