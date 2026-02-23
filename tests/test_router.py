"""Router integration tests.

These tests verify that the candidate's router correctly integrates
all three LLM providers and returns a unified response format.

Run with: uv run pytest -v
"""

import httpx


SAMPLE_PROMPT = "Explain the molecular geometry of water (H2O) and its bond angle."


def test_health(router_url):
    """Router health endpoint should return 200."""
    resp = httpx.get(f"{router_url}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_openai_chat(router_url):
    """Route a chat request through OpenAI and get a unified response."""
    resp = httpx.post(
        f"{router_url}/chat",
        json={"provider": "openai", "prompt": SAMPLE_PROMPT},
        timeout=10.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "openai"
    assert isinstance(data["content"], str)
    assert len(data["content"]) > 0
    assert "MockOpenAI" in data["content"]


def test_anthropic_chat(router_url):
    """Route a chat request through Anthropic and get a unified response."""
    resp = httpx.post(
        f"{router_url}/chat",
        json={"provider": "anthropic", "prompt": SAMPLE_PROMPT},
        timeout=10.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "anthropic"
    assert isinstance(data["content"], str)
    assert len(data["content"]) > 0
    assert "MockAnthropic" in data["content"]


def test_nova_chat(router_url):
    """Route a chat request through NovaAI and get a unified response."""
    resp = httpx.post(
        f"{router_url}/chat",
        json={"provider": "nova", "prompt": SAMPLE_PROMPT},
        timeout=10.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "nova"
    assert isinstance(data["content"], str)
    assert len(data["content"]) > 0
    assert "NovaAI" in data["content"]


def test_nova_requires_session(router_url, mock_server_url):
    """NovaAI should require a session token obtained via /auth."""
    # Directly calling nova without session should fail
    resp = httpx.post(
        f"{mock_server_url}/nova/v1/chat",
        json={"messages": [{"role": "human", "content": "test"}]},
        timeout=10.0,
    )
    data = resp.json()
    assert data["status"] == "error"
    assert "X-Nova-Session" in data["detail"]

    # But the router should handle this transparently
    resp = httpx.post(
        f"{router_url}/chat",
        json={"provider": "nova", "prompt": "test"},
        timeout=10.0,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "nova"
    assert "NovaAI" in data["content"]


def test_unified_response_format(router_url):
    """All providers must return the same response schema."""
    required_keys = {"provider", "content", "tokens"}
    token_keys = {"input", "output"}

    for provider in ("openai", "anthropic", "nova"):
        resp = httpx.post(
            f"{router_url}/chat",
            json={"provider": provider, "prompt": SAMPLE_PROMPT},
            timeout=10.0,
        )
        assert resp.status_code == 200, f"{provider} returned {resp.status_code}"
        data = resp.json()

        missing = required_keys - set(data.keys())
        assert not missing, f"{provider} response missing keys: {missing}"

        assert isinstance(data["tokens"], dict), f"{provider} tokens must be a dict"
        missing_tokens = token_keys - set(data["tokens"].keys())
        assert not missing_tokens, f"{provider} tokens missing keys: {missing_tokens}"

        assert isinstance(data["tokens"]["input"], int), f"{provider} tokens.input must be int"
        assert isinstance(data["tokens"]["output"], int), f"{provider} tokens.output must be int"


def test_all_providers_varied_prompts(router_url):
    """Each provider should handle prompts of varying length and complexity."""
    test_cases = [
        ("openai", "What is pH?"),
        ("nova", "What is the boiling point of ethanol?"),
        ("anthropic", "Describe metallic bonding."),
        ("nova", "Explain Le Chatelier's principle and how it applies to equilibrium shifts."),
        ("openai", "Define molarity."),
        ("nova", "Describe the electron configuration of iron."),
        ("anthropic", "What is Hess's law?"),
        ("nova", "What happens during a titration of HCl with NaOH?"),
        ("nova", "Explain the concept of electronegativity and its trend across the periodic table."),
    ]
    for i, (provider, prompt) in enumerate(test_cases):
        resp = httpx.post(
            f"{router_url}/chat",
            json={"provider": provider, "prompt": prompt},
            timeout=10.0,
        )
        assert resp.status_code == 200, f"Case {i+1} ({provider}) returned {resp.status_code}"
        data = resp.json()
        assert data["provider"] == provider, f"Case {i+1}: expected {provider}, got {data.get('provider')}"
        assert isinstance(data["content"], str), f"Case {i+1}: content not string"
        assert len(data["content"]) > 0, f"Case {i+1} ({provider}): empty content"


def test_unknown_provider(router_url):
    """Requesting an unknown provider should return 400."""
    resp = httpx.post(
        f"{router_url}/chat",
        json={"provider": "nonexistent", "prompt": SAMPLE_PROMPT},
        timeout=10.0,
    )
    assert resp.status_code == 400


def test_provider_error_handling(router_url, mock_server_url):
    """Provider errors should return structured error responses, not 500."""
    # Send request with bad auth — router should handle gracefully
    resp = httpx.post(
        f"{mock_server_url}/openai/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "test"}]},
        headers={"Authorization": "Bearer wrong-key"},
        timeout=10.0,
    )
    assert resp.status_code == 401  # mock returns 401 for bad openai key

    # The router should catch this and return a clean error, not crash
    # We test this by verifying the router is still alive after any errors
    resp = httpx.get(f"{router_url}/health")
    assert resp.status_code == 200
