from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import Body, Depends, FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import uuid
import structlog

from config.settings import get_settings
from models.jsonrpc import JsonRpcRequest, JsonRpcResponse, INVALID_REQUEST
from server.mcp_handler import handle_mcp
from server.security import verify_client_key


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp")
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
slog = structlog.get_logger("mcp")

app = FastAPI(title="MyGemini MCP Server")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = rid
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response

app.add_middleware(RequestIDMiddleware)

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

    slog.bind(request_id=request_id).info("mcp_request", method=getattr(req, "method", ""))
    resp = await handle_mcp(req)
    return JSONResponse(content=resp.model_dump())
