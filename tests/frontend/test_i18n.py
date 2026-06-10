"""Tests for frontend i18n."""

from learning_assistant.frontend.i18n import (
    DEFAULT_LOCALE,
    SUPPORTED_LANGUAGES,
    get_strings,
    language_option_labels,
)


class TestGetStrings:
    def test_default_locale_is_zh_cn(self) -> None:
        assert DEFAULT_LOCALE == "zh-CN"

    def test_zh_cn_strings(self) -> None:
        t = get_strings("zh-CN")
        assert t.btn_new_chat == "新建对话"
        assert t.page_rag == "RAG 对话"
        assert t.app_title == "Learning Assistant"

    def test_en_strings(self) -> None:
        t = get_strings("en")
        assert t.btn_new_chat == "New Chat"
        assert t.page_chat == "Chat"

    def test_unknown_locale_falls_back_to_zh_cn(self) -> None:
        t = get_strings("fr")
        assert t.btn_new_chat == "新建对话"

    def test_page_label(self) -> None:
        t = get_strings("en")
        assert t.page_label("rag_chat") == "RAG Chat"
        assert t.page_label("chat") == "Chat"

    def test_format_helpers(self) -> None:
        t = get_strings("zh-CN")
        assert t.format_session_name("abc123") == "会话 abc123"
        assert "test.pdf" in t.format_upload_indexed("test.pdf", 3)

    def test_supported_languages(self) -> None:
        assert "zh-CN" in SUPPORTED_LANGUAGES
        assert "en" in SUPPORTED_LANGUAGES

    def test_language_option_labels(self) -> None:
        t = get_strings("zh-CN")
        labels = language_option_labels(t)
        assert labels["zh-CN"] == "简体中文"
        assert labels["en"] == "English"
