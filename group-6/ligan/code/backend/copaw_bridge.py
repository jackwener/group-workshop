import os
import requests


class CoPawBridge:
    def __init__(self):
        self.chat_url = os.getenv("IRA_COPAW_CHAT_URL")
        self.configured = bool(self.chat_url)

    def ask(self, query, session_id):
        if not self.configured:
            return None
        try:
            resp = requests.post(
                self.chat_url,
                json={"query": query, "session_id": session_id},
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "answer": data.get("answer", ""),
                "llm_used": True,
                "model": "copaw",
                "answer_source": "copaw",
            }
        except Exception:
            return None
