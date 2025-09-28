from __future__ import annotations

from typing import Any, Optional


class GeminiClient:
    def __init__(self, api_key: Optional[str]) -> None:
        self.api_key = api_key

    async def generate(self, model: str, prompt: str) -> Any:
        raise NotImplementedError("Gemini client integration will be implemented in a later phase")


def get_client(api_key: Optional[str]) -> GeminiClient:
    return GeminiClient(api_key)
