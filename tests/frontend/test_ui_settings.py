"""Tests for UISettings."""

from learning_assistant.frontend.config.ui_settings import UISettings


class TestUISettings:
    def test_defaults(self) -> None:
        s = UISettings()
        assert s.language == "zh-CN"
        assert s.api_base_url == "http://localhost:8000"
        assert s.default_top_k == 5
        assert s.default_temperature == 0.2
        assert s.theme == "light"
        assert s.max_history == 50

    def test_custom(self) -> None:
        s = UISettings(api_base_url="http://custom:9000", theme="dark")
        assert s.api_base_url == "http://custom:9000"
        assert s.theme == "dark"
