# LLM Router Challenge

## Customer Brief

**Nexus Labs** is a computational chemistry startup that uses three LLM providers for their research workflows. They want a **unified router API** and a **simple demo page** where their researchers can select a provider, type a prompt, and see the response.

They have a call scheduled Friday afternoon to see the demo. Your job: **make all tests pass and build the UI.**

## Setup

```bash
# Install dependencies
uv sync

# Start the mock provider server (keep this running in a separate terminal)
uv run python -m mock_providers.server

# Run the tests (most will fail — that's your starting point)
uv run pytest -v

# Start your router (once you've implemented it)
uv run uvicorn src.router:app --port 8000 --reload
```

## What You're Building

A FastAPI service in `src/router.py` that:

1. **`POST /chat`** — Accepts `{"provider": "openai"|"anthropic"|"nova", "prompt": "..."}` and returns a unified response:
   ```json
   {"provider": "openai", "content": "The response text...", "tokens": {"input": 42, "output": 15}}
   ```

2. **`GET /`** — A simple HTML demo page with a provider dropdown, prompt text area, submit button, and response display.

3. **`GET /health`** — Already implemented.

## Provider API Docs

### OpenAI

Standard chat completions API.

- **Endpoint:** `{base}/openai/v1/chat/completions`
- **Auth:** `Authorization: Bearer {api_key}`
- **Body:** `{"model": "gpt-4o", "messages": [{"role": "user", "content": "..."}]}`
- **Response:** `{"choices": [{"message": {"content": "..."}}], "usage": {"prompt_tokens": N, "completion_tokens": N}}`

### Anthropic

Standard messages API.

- **Endpoint:** `{base}/anthropic/v1/messages`
- **Auth:** `x-api-key: {api_key}`
- **Body:** `{"model": "claude-sonnet-4", "max_tokens": 1024, "messages": [{"role": "user", "content": "..."}]}`
- **Response:** `{"content": [{"text": "..."}], "usage": {"input_tokens": N, "output_tokens": N}}`

### NovaAI

NovaAI offers an OpenAI-compatible chat API. They are a newer provider — their documentation may not be fully up to date.

- **Endpoint:** `{base}/nova/v1/chat/completions`
- **Auth:** `Authorization: Bearer {api_key}`
- **Body:** `{"model": "nova-large-1", "messages": [{"role": "user", "content": "..."}]}`
- **Response:** `{"choices": [{"message": {"content": "..."}}], "usage": {"prompt_tokens": N, "completion_tokens": N}}`

## Files

| File | Description |
|------|-------------|
| `src/router.py` | **Your workspace.** Implement the router here. |
| `mock_providers/server.pyc` | Mock LLM providers (compiled). **Do not read or modify.** Treat as a black-box API — like a real third-party service. |
| `tests/test_router.py` | Integration tests. **Do not modify.** |
| `tests/conftest.py` | Test fixtures (starts servers automatically). **Do not modify.** |

## API Keys (for mock providers)

```
OpenAI:    sk-test-openai-key-123
Anthropic: ant-test-anthropic-key-456
NovaAI:    nova-test-key-789
```

These are pre-configured in `src/router.py` in the `PROVIDER_CONFIGS` dict.

## Demo UI (GET /)

The Nexus Labs team specifically asked for a demo page they can show their researchers. Build it at `GET /`. It should have:

- A **provider dropdown** (OpenAI, Anthropic, NovaAI)
- A **prompt text area** where researchers type their chemistry question
- A **submit button** that calls your `POST /chat` endpoint
- A **response area** showing the response text, which provider handled it, and token usage
- It should look presentable — this is going on a customer call

No framework required — inline HTML/CSS/JS is fine. But it needs to actually work (submit a real request to your router and display the result).

## Rules

- Use any tools you want (Claude Code, Cursor, ChatGPT, etc.)
- Only modify `src/router.py` (and add files in `src/` if needed)
- **Do not read or modify** `mock_providers/`, test files, or conftest — treat the mock server as a black-box third-party API
- **Goal: all 8 tests green + a working demo UI at `GET /`**
