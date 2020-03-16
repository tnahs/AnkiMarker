import json
import pathlib
from typing import Any, Iterator, List, Optional, Tuple

from . import marker, errors


class Addon:

    name = "AnkiMarker"

    main_root = pathlib.Path(__file__).parent.parent
    main_config = main_root / "config.json"
    main_css_path = main_root / "main.css"

    user_root = main_root / "user_files"
    user_css_path = user_root / "user.css"

    _config: dict = {}

    INVALID_CHARACTERS = """ & " ' > < \\ / """.split()

    def __init__(self, config: Optional[dict] = None) -> None:

        self._validate_config(config=config)

        self._marker = marker.Marker(addon=self)

    def _validate_config(self, config: Optional[dict] = None):

        if config is None:
            try:
                with open(self.main_config, "r") as f:
                    config = json.load(f)
            except FileNotFoundError:
                raise errors.ConfigError("Missing `config.json`.")

        if not config:
            raise errors.ConfigError("No configuration set.")

        styles = config.get("styles", [])

        if not styles:
            raise errors.ConfigError("No `styles` in `config.json`.")

        for style in styles:

            name = style.get("name", None)
            markup = style.get("markup", None)
            classname = style.get("classname", None)

            if not all([name, markup, classname]):
                raise errors.ConfigError(
                    "All styles require: `name` `markup` and `classname`."
                )

            # TODO: Write test for this...
            # via https://stackoverflow.com/a/14321721
            if markup != markup[0] * len(markup):
                raise errors.ConfigError(
                    "Style `markup` can contain one kind of character."
                )

            # TODO: Write test for this...
            if markup[0] in self.INVALID_CHARACTERS:
                raise errors.ConfigError(
                    f"Style `markup` contains invalid characters `{markup[0]}`"
                )

        self._config = config

    @property
    def add_context_menu(self) -> bool:
        return self._config.get("add_context_menu", True)

    @property
    def parent_classnames(self) -> List[str]:
        return self._config.get("parent_classnames", [])

    @property
    def styles(self) -> Iterator[Tuple[str, str, str]]:

        styles = self._config.get("styles", [])

        for style in styles:

            name = style.get("name", None)
            markup = style.get("markup", None)
            classname = style.get("classname", None)

            yield (name, markup, classname)

    def setup(self):
        # TODO: Document this...

        try:
            import anki
            import aqt
        except ImportError:
            return

        def append_css(web_content, context: Optional[Any]):
            web_content.css.append(self.main_css_path)
            web_content.css.append(self.user_css_path)

        def legacy_append_css(html, card, context):

            try:
                with open(self.main_css_path, encoding="utf-8") as f:
                    main_css = f.read()
            except FileNotFoundError:
                main_css = ""

            try:
                with open(self.user_css_path, encoding="utf-8") as f:
                    user_css = f.read()
            except FileNotFoundError:
                user_css = ""

            markup = f"""

                <style>{main_css}{user_css}</style>

                {html}

            """

            return markup

        try:
            aqt.gui_hooks.webview_will_set_content(append_css)
        except AttributeError:
            # Traceback (most recent call last):
            # File "aqt/addons.py", line 205, in loadAddons
            # File "~/Library/Application Support/Anki2/addons21/ankimarker/__init__.py", line 93, in <module>
            #     aqt.gui_hooks.webview_will_set_content(append_css)
            # AttributeError: module 'aqt.gui_hooks' has no attribute 'webview_will_set_content'
            anki.hooks.addHook("prepareQA", legacy_append_css)

        def mark_field(
            field_text: str,
            field_name: str,
            filter_name: str,
            context: anki.template.TemplateRenderContext,
        ) -> str:
            """ Fields called with "marked" ==> {{marked:FieldName}} will be
            rendered with this HTML. """

            if filter_name != "marked":
                return field_text

            return self._marker.mark(string=field_text)

        anki.hooks.field_filter.append(mark_field)

        def unmark_field(
            field_text: str,
            field_name: str,
            filter_name: str,
            context: anki.template.TemplateRenderContext,
        ) -> str:
            """ Fields called with "unmarked" ==> {{unmarked:FieldName}} will
            be rendered with this HTML. """

            if filter_name != "unmarked":
                return field_text

            return self._marker.unmark(string=field_text)

        anki.hooks.field_filter.append(unmark_field)

        if self.add_context_menu:

            def add_context_menu(
                editor_webview: aqt.editor.EditorWebView, menu: aqt.qt.QMenu
            ):

                menu.addSeparator()

                for (name, markup, _) in self.styles:

                    menu.addAction(
                        name,
                        lambda markup=markup: editor_webview.eval(
                            f"wrap('{markup}', '{markup}');"
                        ),
                    )

            aqt.gui_hooks.editor_will_show_context_menu.append(add_context_menu)
