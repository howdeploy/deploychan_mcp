"""Smoke-test the real ASGI app against the installed MCP SDK."""

import json


def test_mcp_app_initializes_and_lists_tools(seeded, monkeypatch):
    # Import the application, not just its SQL helpers: SDK API changes can
    # otherwise go unnoticed until uvicorn starts in a fresh deployment.
    from server import app as server_app
    from starlette.testclient import TestClient

    monkeypatch.setenv("DEPLOYCHAN_ALLOWED_HOSTS", "localhost")
    monkeypatch.setattr(server_app.config, "WEB_DIR", seeded["web_dir"])
    headers = {"Accept": "application/json, text/event-stream"}
    with TestClient(server_app.create_app(), base_url="http://localhost") as client:
        initialized = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "smoke-test", "version": "1.0"},
                },
            },
        )
        assert initialized.status_code == 200
        result = initialized.json()["result"]
        assert result["serverInfo"]["name"] == "deploychan"
        headers["MCP-Protocol-Version"] = result["protocolVersion"]

        listed = client.post(
            "/mcp",
            headers=headers,
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        assert listed.status_code == 200
        assert {tool["name"] for tool in listed.json()["result"]["tools"]} == {
            "search_knowledge", "get_item", "list_skills", "get_skill",
            "onboard", "next_step", "list_recommended",
        }

        called = client.post(
            "/mcp",
            headers=headers,
            json={
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "get_item", "arguments": {"item_id": "tailored-install"}},
            },
        )
        assert called.status_code == 200
        call_result = called.json()["result"]
        assert not call_result.get("isError", False)
        assert json.loads(call_result["content"][0]["text"])["id"] == "tailored-install"
