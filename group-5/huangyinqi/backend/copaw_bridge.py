"""CoPaw Bridge - HTTP bridge to CoPaw API with graceful degradation."""

import os
import requests


class CoPawBridge:
    """T-024: CoPaw API bridge. Returns None on failure for silent degradation."""

    def __init__(self):
        self.chat_url = os.environ.get("IRA_COPAW_CHAT_URL", "")
        self.configured = bool(self.chat_url)

    def ask(self, query, session_id=None):
        """Call CoPaw API. Returns dict on success, None on failure."""
        if not self.configured:
            return None

        try:
            response = requests.post(
                self.chat_url,
                json={"query": query, "session_id": session_id},
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "answer": data.get("answer", ""),
                "model": data.get("model", "copaw"),
            }
        except Exception:
            return None
