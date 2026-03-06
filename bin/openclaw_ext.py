"""WikiOracle ↔ OpenClaw integration bridge.

This module provides the bridge between OpenClaw's multi-channel front-end
(Slack, Discord, Telegram) and WikiOracle's ``/chat`` endpoint.  It lives in
WikiOracle's ``bin/`` directory so that OpenClaw's own source files remain
unmodified — mirroring the ``nanochat_ext.py`` pattern.

Usage (from OpenClaw's adapter code)::

    from openclaw_ext import WikiOracleBridge
    bridge = WikiOracleBridge("http://localhost:5000")
    response = bridge.send("Hello!", channel_id="slack-general", user_id="u123")
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class WikiOracleBridge:
    """Bridge between OpenClaw channel adapters and WikiOracle server.

    Each bridge instance targets a single WikiOracle server URL and manages
    per-channel session state as files on disk.

    Parameters
    ----------
    server_url : str
        WikiOracle server URL (e.g. ``http://localhost:5000``).
    state_dir : str | None
        Directory for per-channel session state files.
        Defaults to ``~/.openclaw/sessions``.
    timeout : int
        HTTP request timeout in seconds.
    """

    def __init__(
        self,
        server_url: str = "http://localhost:5000",
        state_dir: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.server_url = server_url.rstrip("/")
        self.state_dir = Path(state_dir) if state_dir else Path.home() / ".openclaw" / "sessions"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout

    def _state_path(self, channel_id: str) -> Path:
        """Return the session state file path for a channel."""
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in channel_id)
        return self.state_dir / f"{safe_id}.json"

    def _load_session_state(self, channel_id: str) -> dict | None:
        """Load session state for a channel, or None if no session exists."""
        path = self._state_path(channel_id)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _save_session_state(self, channel_id: str, state: dict) -> None:
        """Save session state for a channel."""
        path = self._state_path(channel_id)
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def send(
        self,
        message: str,
        channel_id: str = "default",
        user_id: str = "openclaw-user",
        conversation_id: str | None = None,
    ) -> dict:
        """Send a message to WikiOracle and return the response.

        Parameters
        ----------
        message : str
            The user message to send.
        channel_id : str
            Channel identifier for session management.
        user_id : str
            User identifier for the message.
        conversation_id : str | None
            If provided, append to an existing conversation.

        Returns
        -------
        dict
            Response from WikiOracle with ``content`` and ``conversation_id``
            keys.
        """
        payload: dict = {
            "message": message,
            "username": user_id,
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id

        # Include session state if available (stateless mode)
        session = self._load_session_state(channel_id)
        if session:
            payload["state"] = session

        url = f"{self.server_url}/chat"
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers={"Content-Type": "application/json"})

        try:
            with urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except URLError as e:
            logger.error("Failed to reach WikiOracle at %s: %s", url, e)
            return {"content": f"Error: could not reach WikiOracle server ({e})", "error": True}
        except json.JSONDecodeError:
            return {"content": "Error: invalid response from WikiOracle", "error": True}

        # Save updated state if returned (stateless mode)
        if "state" in result:
            self._save_session_state(channel_id, result["state"])

        return result

    def health_check(self) -> bool:
        """Check if the WikiOracle server is reachable."""
        try:
            req = Request(f"{self.server_url}/health")
            with urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except (URLError, OSError):
            return False
