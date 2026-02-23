"""Test fixtures — starts the mock provider server and provides a test client."""

import multiprocessing
import os
import socket
import time

import httpx
import pytest
import uvicorn


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _run_mock_server(port: int) -> None:
    from mock_providers.server import app

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


def _run_router_server(port: int) -> None:
    from src.router import app

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


def _wait_for_server(url: str, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = httpx.get(f"{url}/health", timeout=1.0)
            if resp.status_code == 200:
                return
        except httpx.ConnectError:
            time.sleep(0.1)
    raise RuntimeError(f"Server at {url} did not start within {timeout}s")


@pytest.fixture(scope="session")
def mock_server_url():
    """Start mock provider server in a subprocess and return its base URL."""
    port = _find_free_port()
    proc = multiprocessing.Process(target=_run_mock_server, args=(port,), daemon=True)
    proc.start()

    url = f"http://127.0.0.1:{port}"
    _wait_for_server(url)

    yield url

    proc.kill()
    proc.join(timeout=2)


@pytest.fixture(scope="session")
def router_url(mock_server_url):
    """Start the candidate's router server and return its base URL.

    The router must be importable from src.router and expose a FastAPI `app`.
    The mock provider base URL is set via the MOCK_PROVIDER_URL env var.
    """
    os.environ["MOCK_PROVIDER_URL"] = mock_server_url

    port = _find_free_port()
    proc = multiprocessing.Process(target=_run_router_server, args=(port,), daemon=True)
    proc.start()

    url = f"http://127.0.0.1:{port}"
    _wait_for_server(url)

    yield url

    proc.kill()
    proc.join(timeout=2)
