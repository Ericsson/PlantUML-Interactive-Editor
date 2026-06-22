import socket
import threading

import pytest
from plantuml_gui.app import app


def _get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    port = _get_free_port()
    thread = threading.Thread(
        target=app.run,
        kwargs={"host": "127.0.0.1", "port": port, "use_reloader": False},
        daemon=True,
    )
    thread.start()
    # Wait for server to be ready
    import time

    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.1)
    return f"http://127.0.0.1:{port}"


@pytest.fixture()
def app_url(live_server, page):
    page.goto(live_server)
    return live_server
