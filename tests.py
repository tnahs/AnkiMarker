import pytest

from ankimarker.src.addon import Addon
from ankimarker.src.errors import ConfigError


class TestAddon(object):
    # TODO: Doument tests...

    config = {
        "add_context_menu": True,
        "parent_classnames": [],
        "styles": [
            {"name": "Style0", "markup": "*", "classname": "style0"},
            {"name": "Style1", "markup": "**", "classname": "style1"},
            {"name": "Style3", "markup": "~", "classname": "style3"},
            {"name": "Style4", "markup": "~~", "classname": "style4"},
        ],
    }

    marked = "*abcd* **abcd** ~abcd~ ~~abcd~~"
    unmarked = "abcd abcd abcd abcd"
    as_html = " ".join(
        [
            '<anki-marker><span class="style0">abcd</span>',
            '<span class="style1">abcd</span>',
            '<span class="style3">abcd</span>',
            '<span class="style4">abcd</span></anki-marker>',
        ]
    )

    def test_config(self):

        with pytest.raises(ConfigError):
            Addon(config=[])

        with pytest.raises(ConfigError):
            Addon(config={})

        #

        bad_config = self.config.copy()

        #

        bad_config["styles"] = []

        with pytest.raises(ConfigError):
            Addon(config=bad_config)

        #

        del bad_config["styles"]

        with pytest.raises(ConfigError):
            Addon(config=bad_config)

        #

        bad_config["styles"] = [
            {"markup": "*", "classname": "style-bad"},
        ]

        with pytest.raises(ConfigError):
            Addon(config=bad_config)

        bad_config["styles"] = [
            {"name": "StyleBad", "classname": "style-bad"},
        ]

        with pytest.raises(ConfigError):
            Addon(config=bad_config)

        bad_config["styles"] = [
            {"name": "StyleBad", "markup": "*"},
        ]

        with pytest.raises(ConfigError):
            Addon(config=bad_config)

    def test_marker(self):

        addon = Addon(config=self.config)

        as_html = addon._marker.mark(string=self.marked)
        unmarked = addon._marker.unmark(string=self.marked)

        assert as_html == self.as_html
        assert unmarked == self.unmarked
