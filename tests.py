import pathlib

import pytest

from ankimarker.src import AnkiMarker, errors


class TestAddon(object):

    config = {
        "parent-classnames": [],
        "styles": [
            {"name": "Style0", "markup": "*", "classname": "style0"},
            {"name": "Style1", "markup": "**", "classname": "style1"},
            {"name": "Style3", "markup": "~", "classname": "style3"},
            {"name": "Style4", "markup": "~~", "classname": "style4"},
        ],
    }

    def test_config_missing(self) -> None:

        # When running in Anki, `<AnkiMarker>` is not instantiated with a
        # `config` but reads `config.json` from  the addon directory. This path
        # is stored as a class variable in `<AnkiMarker>.config_path`. We
        # simulate a missing file by monkey-patching `config_path`.
        AnkiMarker.config_path = pathlib.Path("/missing/path/to/styles.json")

        with pytest.raises(errors.ConfigError):
            AnkiMarker()

    def test_config_empty(self) -> None:

        with pytest.raises(errors.ConfigError):
            AnkiMarker(config=[])

        with pytest.raises(errors.ConfigError):
            AnkiMarker(config={})

    def test_config_missing_styles(self) -> None:

        # Missing `styles`.
        bad_config: dict = {}
        with pytest.raises(errors.ConfigError):
            AnkiMarker(config=bad_config)

    def test_config_bad_styles(self) -> None:

        bad_config: dict = {}

        # Config with style missing `name`.
        bad_config["styles"] = [
            {"markup": "*", "classname": "bad-style"},
        ]
        with pytest.raises(errors.ConfigError):
            AnkiMarker(config=bad_config)

        # Config with style missing `markup`.
        bad_config["styles"] = [
            {"name": "BadStyle", "classname": "bad-style"},
        ]
        with pytest.raises(errors.ConfigError):
            AnkiMarker(config=bad_config)

        # Config with style missing `classname`.
        bad_config["styles"] = [
            {"name": "BadStyle", "markup": "*"},
        ]
        with pytest.raises(errors.ConfigError):
            AnkiMarker(config=bad_config)

    def test_config_bad_style_markup(self) -> None:

        bad_config: dict = {}

        # Config with no `markup` character(s).
        bad_config["styles"] = [
            {"name": "BadStyle", "markup": "", "classname": "bad-style"},
        ]
        with pytest.raises(errors.ConfigError):
            AnkiMarker(config=bad_config)

        # Config with invalid `markup` character(s).
        bad_config["styles"] = [
            {"name": "BadStyle", "markup": "&", "classname": "bad-style"},
        ]
        with pytest.raises(errors.ConfigError):
            AnkiMarker(config=bad_config)

        # Config with invalid `markup` syntax.
        bad_config["styles"] = [
            {"name": "BadStyle", "markup": "@#", "classname": "bad-style"},
        ]
        with pytest.raises(errors.ConfigError):
            AnkiMarker(config=bad_config)

    def test_marker(self) -> None:

        addon = AnkiMarker(config=self.config)

        base_marked = "*abcd* **abcd** ~abcd~ ~~abcd~~"
        base_unmarked = "abcd abcd abcd abcd"
        _base_rendered = " ".join(
            [
                '<span class="style0">abcd</span>',
                '<span class="style1">abcd</span>',
                '<span class="style3">abcd</span>',
                '<span class="style4">abcd</span>',
            ]
        )
        base_rendered = f"<anki-marker>{_base_rendered}</anki-marker>"

        #

        assert base_rendered == addon._marker.render(string=base_marked)
        assert base_unmarked == addon._marker.unmark(string=base_marked)

    def test_marked_with_tags(self) -> None:

        addon = AnkiMarker(config=self.config)

        tags_marked = "*abcd* <div><p><strong>abc</strong></p></div> *abcd*"
        tags_unmarked = "abcd <div><p><strong>abc</strong></p></div> abcd"
        _tags_rendered = " ".join(
            [
                '<span class="style0">abcd</span>',
                "<div><p><strong>abc</strong></p></div>",
                '<span class="style0">abcd</span>',
            ]
        )
        tags_rendered = f"<anki-marker>{_tags_rendered}</anki-marker>"

        #

        assert tags_rendered == addon._marker.render(string=tags_marked)
        assert tags_unmarked == addon._marker.unmark(string=tags_marked)

    def test_marked_entities(self) -> None:

        addon = AnkiMarker(config=self.config)

        entity_marked = "*abcd* *&amp;* *&#38;* *&#x26;* *abcd*"
        entity_unmarked = "abcd &amp; &#38; &#x26; abcd"
        _entity_rendered = " ".join(
            [
                '<span class="style0">abcd</span>',
                '<span class="style0">&amp;</span>',
                '<span class="style0">&#38;</span>',
                '<span class="style0">&#x26;</span>',
                '<span class="style0">abcd</span>',
            ]
        )
        entity_rendered = f"<anki-marker>{_entity_rendered}</anki-marker>"

        #

        assert entity_rendered == addon._marker.render(string=entity_marked)
        assert entity_unmarked == addon._marker.unmark(string=entity_marked)
