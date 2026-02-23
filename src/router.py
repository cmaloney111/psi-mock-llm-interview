"""LLM Router

Your task: Build a unified router that forwards chat requests to
OpenAI, Anthropic, or NovaAI and returns a consistent response format.

The mock provider server must be running (see README.md for setup).
Provider base URL is available via the MOCK_PROVIDER_URL env var.

Run the router: uv run uvicorn src.router:app --port 8000
Run the tests:  uv run pytest -v
"""

import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="LLM Router")

# Provider API keys
API_KEYS = {
    "openai": "sk-test-openai-key-123",
    "anthropic": "ant-test-anthropic-key-456",
    "nova": "nova-test-key-789",
}


def _base_url() -> str:
    """Mock provider server base URL (set by test fixtures or env)."""
    return os.environ.get("MOCK_PROVIDER_URL", "http://127.0.0.1:9876")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat():
    # TODO: Implement provider routing
    #
    # Expected request body:
    #   {"provider": "openai" | "anthropic" | "nova", "prompt": "..."}
    #
    # Expected response format (unified across all providers):
    #   {"provider": "...", "content": "...", "tokens": {"input": N, "output": N}}
    #
    raise NotImplementedError("Router not implemented yet")


@app.get("/", response_class=HTMLResponse)
async def ui():
    # TODO: Build a simple demo page for Nexus Labs
    # - Provider selector dropdown (OpenAI, Anthropic, NovaAI)
    # - Text input for the prompt
    # - Submit button
    # - Response display area
    return "<h1>LLM Router</h1><p>Demo UI not implemented yet.</p>"
