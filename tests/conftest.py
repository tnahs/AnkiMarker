import pytest

from addon.src.marker import Marker
from addon.src.style import Style


@pytest.fixture(scope="session")
def styles() -> list[Style]:
    return [
        Style(
            name="Style0",
            markup="*",
            classnames=["parent-style", "style0"],
        ),
        Style(
            name="Style1",
            markup="**",
            classnames=["parent-style", "style1"],
        ),
        Style(
            name="Style2",
            markup="~",
            classnames=["parent-style", "style2"],
        ),
        Style(
            name="Style3",
            markup="~~",
            classnames=["parent-style", "style3"],
        ),
    ]


@pytest.fixture(scope="session")
def marker(styles: list[Style]) -> Marker:
    return Marker(styles=styles)
