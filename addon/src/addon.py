import functools
from typing import Any, Optional

import anki
import anki.hooks
import aqt
import aqt.gui_hooks
from anki.template import TemplateRenderContext
from aqt.clayout import CardLayout
from aqt.editor import EditorWebView
from aqt.reviewer import Reviewer
from aqt.webview import WebContent
from PyQt5.QtWidgets import QMenu

from .config import Config
from .helpers import Defaults, E_Filter
from .marker import Marker


class AnkiMarker:
    def __init__(self) -> None:

        self.__config = Config()
        self.__marker = Marker(styles=self.config.styles)

    @property
    def config(self) -> Config:
        return self.__config

    def setup(self) -> None:

        # Append CSS Stylesheets

        def hook__append_css(web_content: WebContent, context: Optional[Any]) -> None:

            if not isinstance(context, (CardLayout, Reviewer)):
                return

            # Add-ons may expose their own web assets by utilizing
            # aqt.addons.AddonManager.setWebExports(). Web exports registered
            # in this manner may then be accessed under the `/_addons` subpath.
            #
            # E.g., to allow access to a `my-addon.js` and `my-addon.css` residing
            # in a "web" subfolder in your add-on package, first register the
            # corresponding web export:
            #
            # > from aqt import mw
            # > mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")

            aqt.mw.addonManager.setWebExports(__name__, r".+\.css")  # type: ignore

            web_content.css.extend(
                [
                    str(Defaults.MAIN_CSS),
                    str(Defaults.MARKERS_CSS),
                ]
            )

        aqt.gui_hooks.webview_will_set_content.append(hook__append_css)

        # Field Filters

        def hook__render_field(
            field_text: str,
            field_name: str,
            filter_name: str,
            context: TemplateRenderContext,
        ) -> str:
            """Fields prepended with "marked" --> {{marked:FieldName}} will be
            filtered through this function."""

            if filter_name != E_Filter.MARKED.value:
                return field_text

            return self.__marker.render(string=field_text)

        def hook__unmark_field(
            field_text: str,
            field_name: str,
            filter_name: str,
            context: TemplateRenderContext,
        ) -> str:
            """Fields prepended with "unmarked" --> {{unmarked:FieldName}} will
            be filtered through this function."""

            if filter_name != E_Filter.UNMARKED.value:
                return field_text

            return self.__marker.unmark(string=field_text)

        anki.hooks.field_filter.append(hook__render_field)
        anki.hooks.field_filter.append(hook__unmark_field)

        # Context Menus

        def hook__add_context_menu(editor: EditorWebView, menu: QMenu) -> None:

            menu.addSeparator()
            menu.addAction(
                "Unmark",
                functools.partial(action__unmark, editor=editor),
            )

            for style in self.config.styles:

                menu.addAction(
                    style.name,
                    functools.partial(action__mark, editor=editor, markup=style.markup),
                )

        aqt.gui_hooks.editor_will_show_context_menu.append(hook__add_context_menu)

        def action__unmark(editor: EditorWebView) -> None:

            text = editor.selectedText()
            text = self.__marker.unmark(string=text)

            # Replaces the selected text with unmarked string.
            editor.eval(
                f"""
                document.execCommand("inserttext", false, "{text}")
                """
            )

        def action__mark(editor: EditorWebView, markup: str) -> None:

            text = editor.selectedText()
            text = self.__marker.mark(string=text, markup=markup)

            # Replaces the selected text with marked string.
            editor.eval(
                f"""
                document.execCommand("inserttext", false, "{text}")
                """
            )
