import functools
from typing import Any, Optional

import anki
import anki.hooks
import aqt
import aqt.gui_hooks
import aqt.utils
from anki.template import TemplateRenderContext
from aqt.clayout import CardLayout
from aqt.editor import EditorWebView
from aqt.previewer import BrowserPreviewer
from aqt.reviewer import Reviewer
from aqt.webview import WebContent
from PyQt5.QtWidgets import QMenu

from .config import Config
from .helpers import Defaults, E_Filter, InvalidMarkup
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

            if not isinstance(context, (CardLayout, BrowserPreviewer, Reviewer)):
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
            """Fields prepended with 'marked' --> {{marked:FieldName}} will be
            filtered through this function."""

            if filter_name != E_Filter.MARKED.value:
                return field_text

            try:
                return self.__marker.render(string=field_text)
            except InvalidMarkup:
                aqt.utils.showInfo(
                    # TODO: Better error message.
                    f"{Defaults.NAME}: Field '{field_name}' contains invalid markup."
                )
                return field_text

        def hook__unmark_field(
            field_text: str,
            field_name: str,
            filter_name: str,
            context: TemplateRenderContext,
        ) -> str:
            """Fields prepended with 'unmarked' --> {{unmarked:FieldName}} will
            be filtered through this function."""

            if filter_name != E_Filter.UNMARKED.value:
                return field_text

            try:
                return self.__marker.unmark(string=field_text)
            except InvalidMarkup:
                aqt.utils.showInfo(
                    # TODO: Better error message.
                    f"{Defaults.NAME}: Field '{field_name}' contains invalid markup."
                )
                return field_text

        anki.hooks.field_filter.append(hook__render_field)
        anki.hooks.field_filter.append(hook__unmark_field)

        # Context Menus

        def hook__add_context_menu(editor: EditorWebView, menu: QMenu) -> None:

            menu.addSeparator()
            menu.addAction(
                "Unmark",
                functools.partial(
                    action_context__unmark,
                    editor=editor,
                ),
            )

            for style in self.config.styles:

                menu.addAction(
                    style.name,
                    functools.partial(
                        action_context__mark,
                        editor=editor,
                        markup=style.markup,
                    ),
                )

        aqt.gui_hooks.editor_will_show_context_menu.append(hook__add_context_menu)

        def action_context__mark(editor: EditorWebView, markup: str) -> None:

            selection = editor.selectedText()

            try:
                string = self.__marker.mark(string=selection, markup=markup)
            except InvalidMarkup:
                # TODO: Better error message.
                aqt.utils.showInfo("Selection contains invalid markup.")
                return

            # Replaces the selected string with marked string.
            editor.eval(f"document.execCommand('inserttext', false, '{string}')")

        def action_context__unmark(editor: EditorWebView) -> None:

            selection = editor.selectedText()

            try:
                string = self.__marker.unmark(string=selection)
            except InvalidMarkup:
                # TODO: Better error message.
                aqt.utils.showInfo("Selection contains invalid markup.")
                return

            # Replaces the selected text with unmarked string.
            editor.eval(f"document.execCommand('inserttext', false, '{string}')")
