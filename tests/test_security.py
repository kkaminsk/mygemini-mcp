def test_mcp_missing_api_key(client):
    payload = {"jsonrpc": "2.0", "id": "x", "method": "tools/list"}
    r = client.post("/mcp", json=payload)
    assert r.status_code == 401
    body = r.json()
    assert body["detail"].lower().find("missing api key") >= 0


def test_mcp_invalid_api_key(client):
    headers = {"X-API-Key": "bad-key"}
    payload = {"jsonrpc": "2.0", "id": "x", "method": "tools/list"}
    r = client.post("/mcp", headers=headers, json=payload)
    assert r.status_code == 401
    body = r.json()
    assert body["detail"].lower().find("invalid api key") >= 0
