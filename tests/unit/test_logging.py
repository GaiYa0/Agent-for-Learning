"""Tests for logging configuration."""

import logging

import pytest

from learning_assistant.config.logging import setup_logging


class TestSetupLogging:
    def test_configures_root_logger_level(self) -> None:
        setup_logging("DEBUG")
        assert logging.getLogger().level == logging.DEBUG

    def test_clears_previous_handlers(self) -> None:
        setup_logging("INFO")
        handler_count_before = len(logging.getLogger().handlers)
        setup_logging("DEBUG")
        # Should not accumulate handlers
        assert len(logging.getLogger().handlers) <= handler_count_before + 1

    def test_has_stream_handler(self) -> None:
        setup_logging("INFO")
        root = logging.getLogger()
        stream_handlers = [
            h for h in root.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(stream_handlers) >= 1

    def test_all_levels_work(self) -> None:
        for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            setup_logging(level)  # type: ignore[arg-type]
            assert logging.getLogger().level == getattr(logging, level)

    def test_default_level_is_info(self) -> None:
        setup_logging()
        assert logging.getLogger().level == logging.INFO

    def test_idempotent(self) -> None:
        setup_logging("INFO")
        setup_logging("INFO")
        root = logging.getLogger()
        assert len(root.handlers) == 1

    def test_setup_logging_invalid_level_raises(self) -> None:
        with pytest.raises(ValueError, match="log level must be one of"):
            setup_logging("INVALID")  # type: ignore[arg-type]
