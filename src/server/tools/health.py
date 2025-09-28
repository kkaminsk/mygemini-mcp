from __future__ import annotations

import time
from pydantic import BaseModel

from .registry import register_tool


class HealthParams(BaseModel):
    """No parameters required for health check."""
    pass


_START = time.monotonic()


async def health_handler(_: HealthParams) -> dict:
    uptime = int(time.monotonic() - _START)
    structured = {"status": "ok", "uptime_seconds": uptime}
    return {"content": f"Service healthy. Uptime: {uptime}s", "structuredContent": structured}


# Register this tool at import time
register_tool(
    name="health_check",
    description="Report service health status and uptime in seconds",
    input_model=HealthParams,
    handler=health_handler,
)
