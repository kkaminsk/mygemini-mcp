from __future__ import annotations

from typing import Any, Optional, Union, Literal

from pydantic import BaseModel, Field


# Standard JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class ErrorObject(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: Union[str, int] = Field(..., description="Unique request identifier (string or integer; non-null)")
    method: str
    params: Optional[Union[dict, list]] = None


class JsonRpcResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[ErrorObject] = None

    @classmethod
    def success(cls, id: Union[str, int], result: Any) -> "JsonRpcResponse":
        return cls(id=id, result=result)

    @classmethod
    def failure(
        cls, id: Union[str, int], code: int, message: str, data: Optional[Any] = None
    ) -> "JsonRpcResponse":
        return cls(id=id, error=ErrorObject(code=code, message=message, data=data))
