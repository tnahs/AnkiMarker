import pytest

from addon.src.config import Config
from addon.src.helpers import ConfigError, Key
from addon.src.marker import Marker


def test__valid_config(markers: list[Marker]) -> None:
    data = {
        Key.PARENT_CLASSNAME: "parent-marker",
        Key.MARKERS: [
            {
                Key.NAME: "Marker0",
                Key.MARKUP: "*",
                Key.CLASSNAME: "marker0",
            },
            {
                Key.NAME: "Marker1",
                Key.MARKUP: "**",
                Key.CLASSNAME: "marker1",
            },
            {
                Key.NAME: "Marker2",
                Key.MARKUP: "~",
                Key.CLASSNAME: "marker2",
            },
            {
                Key.NAME: "Marker3",
                Key.MARKUP: "~~",
                Key.CLASSNAME: "marker3",
            },
        ],
    }

    config = Config(data=data)

    assert config.markers == markers


def test__missing_name() -> None:
    data = {
        Key.MARKERS: [
            {
                # MISSING NAME
                Key.MARKUP: "*",
                Key.CLASSNAME: "marker",
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__missing_markup() -> None:
    data = {
        Key.MARKERS: [
            {
                Key.NAME: "Marker",
                # MISSING MARKUP
                Key.CLASSNAME: "marker",
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__missing_classname() -> None:
    data = {
        Key.MARKERS: [
            {
                Key.NAME: "Marker",
                Key.MARKUP: "*",
                # MISSING CLASSNAME
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__markup_blank() -> None:
    data = {
        Key.MARKERS: [
            {
                Key.NAME: "Marker",
                Key.MARKUP: "",
                Key.CLASSNAME: "marker",
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__invalid_markup() -> None:
    data = {
        Key.MARKERS: [
            {
                Key.NAME: "Marker",
                Key.MARKUP: "&",
                Key.CLASSNAME: "marker",
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__asymmetric_markup() -> None:
    data = {
        Key.MARKERS: [
            {
                Key.NAME: "Marker",
                Key.MARKUP: "=~",
                Key.CLASSNAME: "marker",
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)
