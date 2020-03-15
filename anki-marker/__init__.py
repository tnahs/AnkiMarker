import pathlib
from typing import Optional, Any

import anki
import aqt

from . import marker


class Defaults:

    addon_dir = pathlib.Path(__file__).parent
    main_css_path = addon_dir / "main.css"

    user_dir = addon_dir / "user_files"
    user_css_path = user_dir / "user.css"

    config = aqt.mw.addonManager.getConfig(__name__)


anki_marker = marker.AnkiMarker(config=Defaults.config)


def mark_field(
    field_text: str,
    field_name: str,
    filter_name: str,
    context: anki.template.TemplateRenderContext,
) -> str:
    """ Fields called with "marked" ==> {{marked:FieldName}} will be rendered
    with this HTML. """

    if filter_name != "marked":
        return field_text

    return anki_marker.mark(string=field_text)


anki.hooks.field_filter.append(mark_field)


def unmark_field(
    field_text: str,
    field_name: str,
    filter_name: str,
    context: anki.template.TemplateRenderContext,
) -> str:
    """ Fields called with "unmarked" ==> {{unmarked:FieldName}} will be
    rendered with this HTML. """

    if filter_name != "unmarked":
        return field_text

    return anki_marker.unmark(string=field_text)


anki.hooks.field_filter.append(unmark_field)


def append_css(web_content, context: Optional[Any]):
    web_content.css.append(Defaults.main_css_path)
    web_content.css.append(Defaults.user_css_path)


def legacy_append_css(html, card, context):

    try:
        with open(Defaults.main_css_path, encoding="utf-8") as f:
            main_css = f.read()
    except FileNotFoundError:
        main_css = ""

    try:
        with open(Defaults.user_css_path, encoding="utf-8") as f:
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
    """
    Traceback (most recent call last):
    File "aqt/addons.py", line 205, in loadAddons
    File "/Users/shant/Library/Application Support/Anki2/addons21/ankimarker/__init__.py", line 93, in <module>
        aqt.gui_hooks.webview_will_set_content(append_css)
    AttributeError: module 'aqt.gui_hooks' has no attribute 'webview_will_set_content'
    """
    anki.hooks.addHook("prepareQA", legacy_append_css)

