"""UI string bundle for frontend i18n."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UIStrings:
    app_title: str
    btn_new_chat: str
    nav_sessions: str
    session_default: str
    page_chat: str
    page_rag: str
    page_upload: str
    page_search: str
    page_settings: str
    chat_input: str
    chat_loading: str
    chat_stream_error: str
    chat_streaming_tool: str
    chat_no_session: str
    rag_no_session: str
    thinking_process: str
    agent_thinking: str
    react_thought: str
    react_action: str
    react_observation: str
    react_final_answer: str
    citation_sources: str
    upload_document: str
    upload_and_index: str
    upload_indexing: str
    upload_indexed: str
    search_query: str
    search_results_count: str
    search_button: str
    search_searching: str
    search_failed: str
    settings_title: str
    settings_language: str
    settings_language_zh: str
    settings_language_en: str
    settings_api_base_url: str
    settings_api_key: str
    settings_top_k: str
    settings_temperature: str
    settings_theme: str
    settings_theme_light: str
    settings_theme_dark: str
    settings_saved: str
    err_request_failed: str
    err_no_response: str

    def page_label(self, page_key: str) -> str:
        labels = {
            "chat": self.page_chat,
            "rag_chat": self.page_rag,
            "upload": self.page_upload,
            "search": self.page_search,
            "settings": self.page_settings,
        }
        return labels[page_key]

    def format_session_name(self, session_id: str) -> str:
        return self.session_default.format(id=session_id)

    def format_upload_indexed(self, filename: str, chunks: int) -> str:
        return self.upload_indexed.format(filename=filename, chunks=chunks)

    def format_search_failed(self, error: str) -> str:
        return self.search_failed.format(error=error)

    def format_chat_stream_error(self, error: str) -> str:
        return self.chat_stream_error.format(error=error)

    def format_chat_streaming_tool(self, tool_name: str) -> str:
        return self.chat_streaming_tool.format(name=tool_name)
