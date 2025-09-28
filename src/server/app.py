from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import Body, Depends, FastAPI
from fastapi.responses import JSONResponse

from config.settings import get_settings
from models.jsonrpc import JsonRpcRequest, JsonRpcResponse, INVALID_REQUEST
from server.mcp_handler import handle_mcp
from server.security import verify_client_key


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp")

app = FastAPI(title="MyGemini MCP Server")


@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/mcp")
async def mcp_endpoint(
    payload: Dict[str, Any] = Body(...),
    client_key: str = Depends(verify_client_key),
):
    # Ensure we have a non-null id for all responses as per spec.
    request_id = payload.get("id", "invalid")
    try:
        req = JsonRpcRequest.model_validate(payload)
    except Exception as exc:  # noqa: BLE001
        resp = JsonRpcResponse.failure(request_id, INVALID_REQUEST, f"Invalid JSON-RPC request: {type(exc).__name__}")
        return JSONResponse(status_code=400, content=resp.model_dump())

    resp = await handle_mcp(req)
    return JSONResponse(content=resp.model_dump())
