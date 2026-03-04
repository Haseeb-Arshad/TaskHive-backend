"""Environment-based configuration for the TaskHive MCP server."""

from __future__ import annotations

import os


class MCPSettings:
    """Read MCP-specific settings from environment variables."""

    def __init__(self) -> None:
        self.api_key: str = os.getenv("TASKHIVE_API_KEY", "")
        self.base_url: str = os.getenv(
            "TASKHIVE_API_BASE_URL", "http://localhost:8000"
        )
        self.timeout: float = float(os.getenv("TASKHIVE_TIMEOUT", "30"))

    @property
    def api_base(self) -> str:
        """Base URL for the v1 REST API (e.g. http://localhost:8000/api/v1)."""
        return f"{self.base_url.rstrip('/')}/api/v1"

    @property
    def orchestrator_base(self) -> str:
        """Base URL for orchestrator endpoints."""
        return f"{self.base_url.rstrip('/')}/orchestrator"

    def validate(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "TASKHIVE_API_KEY environment variable is required. "
                "Register an agent at your TaskHive instance to obtain one."
            )


settings = MCPSettings()
