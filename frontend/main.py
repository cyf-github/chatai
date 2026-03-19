"""Frontend app entrypoint."""

from __future__ import annotations

import os

from frontend.gradio_app import build_app


def create_app():
    return build_app()


def main() -> None:
    app = create_app()
    host = os.environ.get("FRONTEND_HOST", "127.0.0.1")
    port = int(os.environ.get("FRONTEND_PORT", "7860"))
    app.launch(server_name=host, server_port=port)


if __name__ == "__main__":
    main()
