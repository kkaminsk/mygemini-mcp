from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from config.settings import get_settings


api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_client_key(api_key: Optional[str] = Depends(api_key_scheme)) -> str:
    """Verify that the provided API key is authorized.

    Returns the client key on success. Raises HTTP 401 otherwise.
    """
    settings = get_settings()

    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    if api_key not in settings.allowed_keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return api_key
