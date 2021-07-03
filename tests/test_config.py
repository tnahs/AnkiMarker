import pytest

from addon.src.config import Config
from addon.src.helpers import ConfigError, Key
from addon.src.style import Style


def test__valid_config(styles: list[Style]) -> None:

    data = {
        Key.PARENT_CLASSNAMES: [
            "parent-style",
        ],
        Key.STYLES: [
            {
                Key.NAME: "Style0",
                Key.MARKUP: "*",
                Key.CLASSNAMES: ["style0"],
            },
            {
                Key.NAME: "Style1",
                Key.MARKUP: "**",
                Key.CLASSNAMES: ["style1"],
            },
            {
                Key.NAME: "Style2",
                Key.MARKUP: "~",
                Key.CLASSNAMES: ["style2"],
            },
            {
                Key.NAME: "Style3",
                Key.MARKUP: "~~",
                Key.CLASSNAMES: ["style3"],
            },
        ],
    }

    config = Config(data=data)

    assert config.styles == styles


def test__missing_name() -> None:

    data = {
        Key.STYLES: [
            {
                # MISSING NAME
                Key.MARKUP: "*",
                Key.CLASSNAMES: ["style"],
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__missing_markup() -> None:

    data = {
        Key.STYLES: [
            {
                Key.NAME: "Style",
                # MISSING MARKUP
                Key.CLASSNAMES: ["style"],
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__missing_classnames() -> None:

    data = {
        Key.STYLES: [
            {
                Key.NAME: "Style",
                Key.MARKUP: "*",
                # MISSING CLASSNAMES
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__markup_blank() -> None:

    data = {
        Key.STYLES: [
            {
                Key.NAME: "Style",
                Key.MARKUP: "",
                Key.CLASSNAMES: ["style"],
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__invalid_markup() -> None:

    data = {
        Key.STYLES: [
            {
                Key.NAME: "Style",
                Key.MARKUP: "&",
                Key.CLASSNAMES: ["style"],
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__asymmetric_markup() -> None:

    data = {
        Key.STYLES: [
            {
                Key.NAME: "Style",
                Key.MARKUP: "=~",
                Key.CLASSNAMES: ["style"],
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)
