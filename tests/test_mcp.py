def test_tools_list(client):
    headers = {"X-API-Key": "dev-key-1"}
    payload = {"jsonrpc": "2.0", "id": "1", "method": "tools/list"}
    r = client.post("/mcp", headers=headers, json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "1"
    assert "tools" in body["result"]


def test_tools_call_echo(client):
    headers = {"X-API-Key": "dev-key-1"}
    payload = {
        "jsonrpc": "2.0",
        "id": "2",
        "method": "tools/call",
        "params": {"name": "echo", "arguments": {"text": "Hello MCP!"}},
    }
    r = client.post("/mcp", headers=headers, json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "2"
    assert body["result"]["content"].lower().find("hello mcp") >= 0
    assert isinstance(body["result"].get("structuredContent"), dict)
