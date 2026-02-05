"""WebSocket connection manager for realtime communication."""

import asyncio
from typing import Dict, Optional
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """
    Manages WebSocket connections for all active users.

    Supports multiple concurrent connections and broadcasting to all users
    or sending messages to specific users.
    """

    def __init__(self):
        """Initialize the connection manager."""
        # Store active connections: user_id -> WebSocket
        self.active_connections: Dict[UUID, WebSocket] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        """
        Register a new WebSocket connection for a user.

        Args:
            user_id: User's unique identifier.
            websocket: WebSocket connection instance.
        """
        async with self._lock:
            # If user is already connected, close old connection
            if user_id in self.active_connections:
                old_ws = self.active_connections[user_id]
                try:
                    await old_ws.close()
                except Exception:
                    pass

            self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: UUID) -> None:
        """
        Remove a WebSocket connection for a user.

        Args:
            user_id: User's unique identifier.
        """
        async with self._lock:
            if user_id in self.active_connections:
                del self.active_connections[user_id]

    async def send_to_user(self, user_id: UUID, message: dict) -> bool:
        """
        Send a message to a specific user.

        Args:
            user_id: Target user's unique identifier.
            message: JSON-serializable message dictionary.

        Returns:
            True if message was sent successfully, False otherwise.
        """
        websocket = self.active_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_json(message)
                return True
            except Exception:
                # Connection might be dead, remove it
                await self.disconnect(user_id)
                return False
        return False

    async def broadcast_to_all(
        self, message: dict, exclude: Optional[UUID] = None
    ) -> None:
        """
        Broadcast a message to all connected users.

        Args:
            message: JSON-serializable message dictionary.
            exclude: Optional user ID to exclude from broadcast.
        """
        # Get a copy of connection items to avoid runtime changes
        connections_copy = list(self.active_connections.items())

        for user_id, websocket in connections_copy:
            if exclude and user_id == exclude:
                continue

            try:
                await websocket.send_json(message)
            except Exception:
                # Connection is dead, remove it
                await self.disconnect(user_id)

    def get_connected_users(self) -> list[UUID]:
        """
        Get list of all connected user IDs.

        Returns:
            List of user IDs currently connected.
        """
        return list(self.active_connections.keys())

    def is_user_connected(self, user_id: UUID) -> bool:
        """
        Check if a user is currently connected.

        Args:
            user_id: User's unique identifier.

        Returns:
            True if user is connected, False otherwise.
        """
        return user_id in self.active_connections


# Global connection manager instance
manager = ConnectionManager()
