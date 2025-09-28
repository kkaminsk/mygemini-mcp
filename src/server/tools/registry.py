from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Type

from pydantic import BaseModel


ToolHandler = Callable[[BaseModel], Awaitable[Dict[str, Any]]]


@dataclass
class ToolEntry:
    name: str
    description: str
    input_model: Type[BaseModel]
    handler: ToolHandler


_TOOLS: Dict[str, ToolEntry] = {}


def register_tool(name: str, description: str, input_model: Type[BaseModel], handler: ToolHandler) -> None:
    _TOOLS[name] = ToolEntry(name=name, description=description, input_model=input_model, handler=handler)


def list_tools() -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = []
    for entry in _TOOLS.values():
        tools.append(
            {
                "name": entry.name,
                "description": entry.description,
                "inputSchema": entry.input_model.model_json_schema(),
            }
        )
    return tools


async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    entry = _TOOLS.get(name)
    if not entry:
        raise ValueError(f"Tool not found: {name}")

    # Validate and coerce arguments using the Pydantic model
    params = entry.input_model.model_validate(arguments)
    result = await entry.handler(params)
    if not isinstance(result, dict) or "content" not in result:
        raise RuntimeError("Tool handler must return a dict with at least a 'content' field")
    return result


# Register built-in tools by importing their modules (side-effect registration)
from . import health  # noqa: E402,F401
from . import echo  # noqa: E402,F401
