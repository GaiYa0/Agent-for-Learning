"""Settings page — configure UI and API parameters."""

from learning_assistant.frontend.config.ui_settings import UISettings
from learning_assistant.frontend.i18n import SUPPORTED_LANGUAGES, get_strings, language_option_labels
from learning_assistant.frontend.i18n.strings import UIStrings
from learning_assistant.frontend.services.api_client import APIClient


def render_settings_page(t: UIStrings) -> None:
    import streamlit as st

    settings: UISettings = st.session_state.setdefault("ui_settings", UISettings())

    st.subheader(t.settings_title)

    lang_labels = language_option_labels(t)
    lang_display = [lang_labels[code] for code in SUPPORTED_LANGUAGES]
    current_index = SUPPORTED_LANGUAGES.index(settings.language)
    selected_label = st.selectbox(
        t.settings_language,
        lang_display,
        index=current_index,
    )
    selected_language = SUPPORTED_LANGUAGES[lang_display.index(selected_label)]
    if selected_language != settings.language:
        settings.language = selected_language
        st.session_state["ui_settings"] = settings
        st.rerun()

    settings.api_base_url = st.text_input(
        t.settings_api_base_url, value=settings.api_base_url
    )
    settings.api_key = st.text_input(
        t.settings_api_key, value=settings.api_key, type="password"
    )
    settings.default_top_k = st.slider(
        t.settings_top_k, 1, 20, settings.default_top_k
    )
    settings.default_temperature = st.slider(
        t.settings_temperature, 0.0, 2.0, settings.default_temperature
    )
    theme_options = [("light", t.settings_theme_light), ("dark", t.settings_theme_dark)]
    theme_labels = [label for _, label in theme_options]
    theme_values = [value for value, _ in theme_options]
    theme_index = theme_values.index(settings.theme) if settings.theme in theme_values else 0
    selected_theme_label = st.selectbox(t.settings_theme, theme_labels, index=theme_index)
    settings.theme = theme_values[theme_labels.index(selected_theme_label)]

    st.session_state["ui_settings"] = settings
    api: APIClient | None = st.session_state.get("api_client")
    if api is not None:
        api.base_url = settings.api_base_url
        api.api_key = settings.api_key
    st.success(t.settings_saved)
