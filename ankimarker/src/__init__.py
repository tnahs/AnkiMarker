import functools
import json
import pathlib
from typing import Any, Iterator, List, Optional, Tuple

from . import errors, marker


class AnkiMarker:

    name = "AnkiMarker"

    main_root = pathlib.Path(__file__).parent.parent
    user_root = main_root / "user_files"
    config_path = user_root / "styles.json"

    # Add-ons may expose their own web assets by utilizing
    # aqt.addons.AddonManager.setWebExports(). Web exports registered
    # in this manner may then be accessed under the `/_addons` subpath.
    #
    # via https://github.com/ankitects/anki/blob/3d7f643184cf9625293a397e1a73109659b77734/qt/aqt/webview.py#L132
    web_export_root = pathlib.Path("/_addons")
    main_css_path = web_export_root / main_root.name / "main.css"
    user_css_path = web_export_root / main_root.name / user_root.name / "styles.css"

    _config: dict = {}

    INVALID_CHARACTERS = """ & " ' > < \\ / ; """.split()

    def __init__(self, config: Optional[dict] = None) -> None:

        self._validate_config(config=config)

        self._marker = marker.Marker(addon=self)

    def _validate_config(self, config: Optional[dict] = None) -> None:

        # The primary reason for this block is to allow testing. Anki will
        # never instiate `<AnkiMarker>` with a `config` therefore this block
        # should *always* run when Anki is running.
        if config is None:
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
            except FileNotFoundError:
                raise errors.ConfigError("Missing `styles.json`.")
            except json.JSONDecodeError:
                raise errors.ConfigError("Cannot read `styles.json`.")

        if not config:
            raise errors.ConfigError("Nothing set in `styles.json`.")

        styles = config.get("styles", None)

        if styles is None:
            raise errors.ConfigError("Missing `styles` in `styles.json`.")

        for style in styles:

            name = style.get("name", None)
            markup = style.get("markup", None)
            classname = style.get("classname", None)

            if not all([name, markup, classname]):
                raise errors.ConfigError(
                    "All styles require: `name` `markup` and `classname`."
                )

            # via https://stackoverflow.com/a/14321721
            if markup != markup[0] * len(markup):
                raise errors.ConfigError(
                    "Style `markup` can only contain one kind of character."
                )

            if markup[0] in self.INVALID_CHARACTERS:
                raise errors.ConfigError(
                    f"Style `markup` contains invalid characters `{markup[0]}`"
                )

        self._config = config

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

    def setup(self) -> None:
        """ This function defines and connects the AnkiMarker to Anki. Hooks
        are prefixed with `hook__` and menu actions with `action__`.

        In both production and testing this function is run. However it's
        wrapped in a try/except block and passed if an `ImportError` is raised.
        """

        import anki
        import aqt

        # Append CSS Stylesheets

        def hook__append_css(
            web_content: aqt.webview.WebContent, context: Optional[Any]
        ) -> None:

            # Add-ons may expose their own web assets by utilizing
            # aqt.addons.AddonManager.setWebExports(). Web exports registered
            # in this manner may then be accessed under the `/_addons` subpath.
            #
            # E.g., to allow access to a `my-addon.js` and `my-addon.css`
            # residing in a "web" subfolder in your add-on package, first
            # register the corresponding web export:
            #
            #   > from aqt import mw
            #   > mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")
            #
            # via https://github.com/ankitects/anki/blob/3d7f643184cf9625293a397e1a73109659b77734/qt/aqt/webview.py#L132
            aqt.mw.addonManager.setWebExports(__name__, r".+\.css")

            web_content.css.extend(
                [str(self.main_css_path), str(self.user_css_path),]
            )

        aqt.gui_hooks.webview_will_set_content.append(hook__append_css)

        # Field Filters

        def hook__render_field(
            field_text: str,
            field_name: str,
            filter_name: str,
            context: anki.template.TemplateRenderContext,
        ) -> str:
            """ Fields prepended with "marked" ==> {{marked:FieldName}} will be
            filtered through this function. """

            if filter_name != "marked":
                return field_text

            return self._marker.render(string=field_text)

        def hook__unmark_field(
            field_text: str,
            field_name: str,
            filter_name: str,
            context: anki.template.TemplateRenderContext,
        ) -> str:
            """ Fields prepended with "unmarked" ==> {{unmarked:FieldName}}
            will be filtered through this function. """

            if filter_name != "unmarked":
                return field_text

            return self._marker.unmark(string=field_text)

        anki.hooks.field_filter.append(hook__render_field)
        anki.hooks.field_filter.append(hook__unmark_field)

        # Context Menus

        def hook__add_context_menu(
            editor_webview: aqt.editor.EditorWebView, menu: aqt.qt.QMenu
        ) -> None:

            menu.addSeparator()

            menu.addAction(
                "Unmark", functools.partial(action__unmark, editor=editor_webview),
            )

            for (name, markup, _) in self.styles:

                menu.addAction(
                    name,
                    functools.partial(
                        action__mark, editor=editor_webview, markup=markup
                    ),
                )

        aqt.gui_hooks.editor_will_show_context_menu.append(hook__add_context_menu)

        def action__unmark(editor: aqt.editor.EditorWebView) -> None:

            text = editor.selectedText()
            unmarked = self._marker.unmark(string=text)

            # Calls the native Javascript function instead of using Anki's
            # `setFormat()`. Replaces the selected text with unmarked
            # string.
            editor.eval(
                f"""
                document.execCommand("inserttext", false, "{unmarked}")
                """
            )

        def action__mark(editor: aqt.editor.EditorWebView, markup: str) -> None:

            text = editor.selectedText()
            marked = self._marker.mark(string=text, markup=markup)

            # Calls the native Javascript function instead of using Anki's
            # `setFormat()`. Replaces the selected text with marked string.
            editor.eval(
                f"""
                document.execCommand("inserttext", false, "{marked}")
                """
            )
