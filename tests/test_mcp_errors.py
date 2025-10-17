import pytest

METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INVALID_REQUEST = -32600


def _headers():
    return {"X-API-Key": "dev-key-1"}


def test_unknown_method_returns_method_not_found(client):
    payload = {"jsonrpc": "2.0", "id": "10", "method": "does/not/exist"}
    r = client.post("/mcp", headers=_headers(), json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["error"]["code"] == METHOD_NOT_FOUND


def test_tools_call_invalid_params_types(client):
    # name wrong type, arguments wrong type
    payload = {
        "jsonrpc": "2.0",
        "id": "11",
        "method": "tools/call",
        "params": {"name": 123, "arguments": []},
    }
    r = client.post("/mcp", headers=_headers(), json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["error"]["code"] == INVALID_PARAMS


def test_invalid_jsonrpc_request_schema_returns_400(client):
    # Missing jsonrpc field
    payload = {"id": "12", "method": "tools/list"}
    r = client.post("/mcp", headers=_headers(), json=payload)
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == INVALID_REQUEST
