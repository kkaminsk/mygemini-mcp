from __future__ import annotations

from functools import lru_cache
from typing import List, Optional, Union, Set

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Use env var names:
    - GEMINI_API_KEY
    - ALLOWED_CLIENT_KEYS (comma-separated or JSON list)
    - DEBUG (bool)
    - PRO_TIMEOUT, FLASH_TIMEOUT, FLASH_LITE_TIMEOUT, LEGACY_FLASH_TIMEOUT (seconds)
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MyGemini MCP Server"
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    allowed_client_keys: Union[str, List[str]] = Field(default_factory=list, alias="ALLOWED_CLIENT_KEYS")
    debug: bool = Field(default=False, alias="DEBUG")

    # Per-model timeouts (seconds)
    pro_timeout: int = Field(default=60, alias="PRO_TIMEOUT")
    flash_timeout: int = Field(default=20, alias="FLASH_TIMEOUT")
    flash_lite_timeout: int = Field(default=10, alias="FLASH_LITE_TIMEOUT")
    legacy_flash_timeout: int = Field(default=15, alias="LEGACY_FLASH_TIMEOUT")

    @property
    def allowed_keys(self) -> Set[str]:
        v = self.allowed_client_keys
        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",")]
            return {p for p in parts if p}
        elif isinstance(v, list):
            return {str(p).strip() for p in v if str(p).strip()}
        return set()


@lru_cache
def get_settings() -> Settings:
    return Settings()
