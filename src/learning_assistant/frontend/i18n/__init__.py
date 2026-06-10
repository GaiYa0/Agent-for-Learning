"""Frontend internationalization."""

from typing import Literal

from learning_assistant.frontend.i18n.locales.en import STRINGS as EN_STRINGS
from learning_assistant.frontend.i18n.locales.zh_CN import STRINGS as ZH_CN_STRINGS
from learning_assistant.frontend.i18n.strings import UIStrings

Language = Literal["zh-CN", "en"]
DEFAULT_LOCALE: Language = "zh-CN"
SUPPORTED_LANGUAGES: tuple[Language, ...] = ("zh-CN", "en")

PAGE_KEYS: tuple[str, ...] = ("chat", "rag_chat", "upload", "search", "settings")

_LOCALES: dict[str, UIStrings] = {
    "zh-CN": ZH_CN_STRINGS,
    "en": EN_STRINGS,
}


def get_strings(locale: str) -> UIStrings:
    """Return UI strings for the given locale, falling back to zh-CN."""
    return _LOCALES.get(locale, ZH_CN_STRINGS)


def language_option_labels(t: UIStrings) -> dict[Language, str]:
    """Human-readable labels for language selectbox."""
    return {
        "zh-CN": t.settings_language_zh,
        "en": t.settings_language_en,
    }
