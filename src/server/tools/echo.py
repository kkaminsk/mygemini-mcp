from __future__ import annotations

from pydantic import BaseModel, Field

from .registry import register_tool


class EchoParams(BaseModel):
    text: str = Field(..., description="Text to echo back")


async def echo_handler(params: EchoParams) -> dict:
    return {"content": params.text, "structuredContent": {"text": params.text}}


# Register this tool at import time
register_tool(
    name="echo",
    description="Echoes back the provided text (useful for testing)",
    input_model=EchoParams,
    handler=echo_handler,
)
