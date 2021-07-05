from typing import List

import pytest

from addon.src.marker import Marker
from addon.src.style import Style


@pytest.fixture(scope="session")
def styles() -> List[Style]:
    return [
        Style(
            name="Style0",
            markup="*",
            classes=["parent-style", "style0"],
        ),
        Style(
            name="Style1",
            markup="**",
            classes=["parent-style", "style1"],
        ),
        Style(
            name="Style2",
            markup="~",
            classes=["parent-style", "style2"],
        ),
        Style(
            name="Style3",
            markup="~~",
            classes=["parent-style", "style3"],
        ),
    ]


@pytest.fixture(scope="session")
def marker(styles: List[Style]) -> Marker:
    return Marker(styles=styles)
