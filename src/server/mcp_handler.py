from __future__ import annotations

import logging
from typing import Any, Dict

from models.jsonrpc import (
    JsonRpcRequest,
    JsonRpcResponse,
    METHOD_NOT_FOUND,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from server.tools.registry import list_tools, call_tool

logger = logging.getLogger(__name__)


async def handle_mcp(req: JsonRpcRequest) -> JsonRpcResponse:
    """Handle JSON-RPC 2.0 MCP methods: tools/list and tools/call.

    Returns a JsonRpcResponse with either result or error populated.
    """
    try:
        if req.method == "tools/list":
            tools = list_tools()
            return JsonRpcResponse.success(req.id, {"tools": tools})

        if req.method == "tools/call":
            if not isinstance(req.params, dict):
                return JsonRpcResponse.failure(req.id, INVALID_PARAMS, "Expected params object with 'name' and 'arguments'")

            name = req.params.get("name")
            arguments = req.params.get("arguments", {})
            if not isinstance(name, str) or not isinstance(arguments, dict):
                return JsonRpcResponse.failure(req.id, INVALID_PARAMS, "Invalid 'name' or 'arguments' types")

            result = await call_tool(name, arguments)
            return JsonRpcResponse.success(req.id, result)

        return JsonRpcResponse.failure(req.id, METHOD_NOT_FOUND, f"Unknown method: {req.method}")

    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled MCP error: %s", exc)
        return JsonRpcResponse.failure(
            req.id,
            INTERNAL_ERROR,
            "Internal server error",
            {"exception": type(exc).__name__, "message": str(exc)},
        )
