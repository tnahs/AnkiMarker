from __future__ import annotations

import functools

import anki
import anki.hooks
import aqt
import aqt.gui_hooks
import aqt.utils
from anki.template import TemplateRenderContext
from aqt.browser.previewer import BrowserPreviewer
from aqt.clayout import CardLayout
from aqt.editor import EditorWebView
from aqt.qt.qt6 import QMenu
from aqt.reviewer import Reviewer
from aqt.webview import WebContent

from .config import Config
from .helpers import Defaults, InvalidMarkup, Key, escape_quotes, show_info
from .processor import Processor


class AnkiMarker:
    def __init__(self) -> None:
        self._config = Config()
        self._processor = Processor(markers=self._config.markers)

    def setup(self) -> None:

        if aqt.mw is None:
            return

        # Add-ons may expose their own web assets by utilizing
        # aqt.addons.AddonManager.setWebExports(). Web exports registered in this
        # manner may then be accessed under the `/_addons` subpath.
        #
        # E.g., to allow access to a `my-addon.js` and `my-addon.css` residing in a
        # "web" subfolder in your add-on package, first register the corresponding
        # web export:
        #
        # > from aqt import mw
        # > mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")

        aqt.mw.addonManager.setWebExports(__name__, r".+\.css")

        # Append CSS Stylesheets

        # The following functions are nested to prevent the need for declaring `self` as
        # the first argument in order to maintain the correct function signature while
        # still being able to access `self`.

        def hook__append_css(web_content: WebContent, context: object | None) -> None:
            """Appends marker CSS to web views."""

            # The context can be from any of these three web views.
            if not isinstance(context, (CardLayout, BrowserPreviewer, Reviewer)):
                return

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
            """Fields prepended with 'marked' i.e. {{marked:FieldName}} will be filtered
            through this function."""

            if filter_name != Key.MARKED:
                return field_text

            try:
                return self._processor.render(string=field_text)
            except InvalidMarkup:
                return f"{Defaults.NAME}: Field contains invalid markup."

        def hook__unmark_field(
            field_text: str,
            field_name: str,
            filter_name: str,
            context: TemplateRenderContext,
        ) -> str:
            """Fields prepended with 'unmarked' i.e. {{unmarked:FieldName}} will be
            filtered through this function."""

            if filter_name != Key.UNMARKED:
                return field_text

            try:
                return self._processor.unmark(string=field_text)
            except InvalidMarkup:
                return f"{Defaults.NAME}: Field contains invalid markup."

        anki.hooks.field_filter.append(hook__render_field)
        anki.hooks.field_filter.append(hook__unmark_field)

        # Context Menus

        def hook__append_context_menu(editor: EditorWebView, menu: QMenu) -> None:
            """Appends marker actions to the editor context-menu."""

            menu.addSeparator()
            menu.addAction(
                "Unmark",
                functools.partial(
                    context_action__unmark,
                    editor=editor,
                ),
            )

            for marker in self._config.markers:

                menu.addAction(
                    marker.name,
                    functools.partial(
                        context_action__mark,
                        editor=editor,
                        markup=marker.markup,
                    ),
                )

        aqt.gui_hooks.editor_will_show_context_menu.append(hook__append_context_menu)

        def context_action__mark(editor: EditorWebView, markup: str) -> None:
            """Marks the selected text within the editor."""

            string = editor.selectedText()

            try:
                string = self._processor.mark(string=string, markup=markup)
            except InvalidMarkup:
                show_info("Selection cannot contain line-breaks or HTML.")
                return

            # Escape quotes to prevent breaking the command string below.
            string = escape_quotes(string=string)

            # Replaces the selected string with marked string.
            editor.eval(f"document.execCommand('inserttext', false, '{string}')")

        def context_action__unmark(editor: EditorWebView) -> None:
            """Unmarks the selected text within the editor."""

            string = editor.selectedText()

            try:
                string = self._processor.unmark(string=string)
            except InvalidMarkup:
                show_info("Selection cannot contain line-breaks or HTML.")
                return

            # Escape quotes to prevent breaking the command string below.
            string = escape_quotes(string=string)

            # Replaces the selected text with unmarked string.
            editor.eval(f"document.execCommand('inserttext', false, '{string}')")
