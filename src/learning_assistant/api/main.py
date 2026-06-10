"""API entry point for uvicorn."""

import uvicorn

from learning_assistant.api.app import create_app
from learning_assistant.config.settings import get_settings


def main() -> None:
    settings = get_settings()
    app = create_app(title=settings.app_name, version=settings.app_version)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
