"""LoopBreaker Environment - Client

Provides a Python client for interacting with the LoopBreaker environment.
"""

from typing import Any
from contextlib import contextmanager

import httpx

from .models import LoopBreakerAction, LoopBreakerObservation, LoopBreakerState


class LoopBreakerEnvSync:
    """Synchronous client for the LoopBreaker environment."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        session_id: str = "default",
        timeout: float = 30.0,
    ):
        """Initialize the client.

        Args:
            base_url: Base URL of the LoopBreaker server
            session_id: Session identifier for this client
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.session_id = session_id
        self.timeout = timeout
        self._client: httpx.Client | None = None

    def __enter__(self):
        """Enter context manager."""
        self._client = httpx.Client(timeout=self.timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self._client:
            self._client.close()
            self._client = None

    @property
    def client(self) -> httpx.Client:
        """Get the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def reset(
        self,
        seed: int | None = None,
        episode_id: str | None = None,
        task_id: str | None = None,
    ) -> LoopBreakerObservation:
        """Reset the environment and start a new episode.

        Args:
            seed: Optional random seed
            episode_id: Optional episode identifier
            task_id: Optional specific task to use

        Returns:
            Initial observation
        """
        response = self.client.post(
            f"{self.base_url}/reset",
            json={
                "seed": seed,
                "episode_id": episode_id,
                "task_id": task_id,
                "session_id": self.session_id,
            },
        )
        response.raise_for_status()
        return LoopBreakerObservation(**response.json())

    def step(self, action: LoopBreakerAction) -> LoopBreakerObservation:
        """Execute an action.

        Args:
            action: The action to execute

        Returns:
            Resulting observation
        """
        response = self.client.post(
            f"{self.base_url}/step",
            json={
                "action": action.model_dump(),
                "session_id": self.session_id,
            },
        )
        response.raise_for_status()
        return LoopBreakerObservation(**response.json())

    def state(self) -> LoopBreakerState:
        """Get the current environment state.

        Returns:
            Current state
        """
        response = self.client.get(
            f"{self.base_url}/state",
            params={"session_id": self.session_id},
        )
        response.raise_for_status()
        return LoopBreakerState(**response.json())

    def health(self) -> dict[str, str]:
        """Check server health.

        Returns:
            Health status
        """
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def info(self) -> dict[str, Any]:
        """Get environment info.

        Returns:
            Environment information
        """
        response = self.client.get(f"{self.base_url}/info")
        response.raise_for_status()
        return response.json()

    def list_tasks(self) -> list[dict[str, Any]]:
        """List available tasks.

        Returns:
            List of task summaries
        """
        response = self.client.get(f"{self.base_url}/tasks")
        response.raise_for_status()
        return response.json()


class LoopBreakerEnv:
    """Async-first client for the LoopBreaker environment with sync wrapper."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        session_id: str = "default",
        timeout: float = 30.0,
    ):
        """Initialize the client.

        Args:
            base_url: Base URL of the LoopBreaker server
            session_id: Session identifier for this client
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.session_id = session_id
        self.timeout = timeout
        self._async_client: httpx.AsyncClient | None = None

    def sync(self) -> LoopBreakerEnvSync:
        """Get a synchronous wrapper for this client.

        Returns:
            Synchronous client wrapper
        """
        return LoopBreakerEnvSync(
            base_url=self.base_url,
            session_id=self.session_id,
            timeout=self.timeout,
        )

    async def __aenter__(self):
        """Enter async context manager."""
        self._async_client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get the async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=self.timeout)
        return self._async_client

    async def reset(
        self,
        seed: int | None = None,
        episode_id: str | None = None,
        task_id: str | None = None,
    ) -> LoopBreakerObservation:
        """Reset the environment and start a new episode.

        Args:
            seed: Optional random seed
            episode_id: Optional episode identifier
            task_id: Optional specific task to use

        Returns:
            Initial observation
        """
        response = await self.async_client.post(
            f"{self.base_url}/reset",
            json={
                "seed": seed,
                "episode_id": episode_id,
                "task_id": task_id,
                "session_id": self.session_id,
            },
        )
        response.raise_for_status()
        return LoopBreakerObservation(**response.json())

    async def step(self, action: LoopBreakerAction) -> LoopBreakerObservation:
        """Execute an action.

        Args:
            action: The action to execute

        Returns:
            Resulting observation
        """
        response = await self.async_client.post(
            f"{self.base_url}/step",
            json={
                "action": action.model_dump(),
                "session_id": self.session_id,
            },
        )
        response.raise_for_status()
        return LoopBreakerObservation(**response.json())

    async def state(self) -> LoopBreakerState:
        """Get the current environment state.

        Returns:
            Current state
        """
        response = await self.async_client.get(
            f"{self.base_url}/state",
            params={"session_id": self.session_id},
        )
        response.raise_for_status()
        return LoopBreakerState(**response.json())

    async def health(self) -> dict[str, str]:
        """Check server health.

        Returns:
            Health status
        """
        response = await self.async_client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def info(self) -> dict[str, Any]:
        """Get environment info.

        Returns:
            Environment information
        """
        response = await self.async_client.get(f"{self.base_url}/info")
        response.raise_for_status()
        return response.json()
