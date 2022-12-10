import pytest

from addon.src.marker import Marker
from addon.src.processor import Processor


@pytest.fixture(scope="session")
def markers() -> list[Marker]:
    return [
        Marker(
            name="Marker0",
            markup="*",
            classes=["parent-marker", "marker0"],
        ),
        Marker(
            name="Marker1",
            markup="**",
            classes=["parent-marker", "marker1"],
        ),
        Marker(
            name="Marker2",
            markup="~",
            classes=["parent-marker", "marker2"],
        ),
        Marker(
            name="Marker3",
            markup="~~",
            classes=["parent-marker", "marker3"],
        ),
    ]


@pytest.fixture(scope="session")
def marker(markers: list[Marker]) -> Processor:
    return Processor(markers=markers)
