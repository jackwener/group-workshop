"""Bailian (百炼/DashScope) QA integration with graceful degradation."""

import os

try:
    import dashscope
    from dashscope import Generation
    HAS_DASHSCOPE = True
except ImportError:
    HAS_DASHSCOPE = False


class BailianQA:
    """T-025: Bailian/DashScope API integration. Returns None on failure."""

    def __init__(self):
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        self.configured = bool(self.api_key)

    def ask(self, query, session_id=None):
        """Call DashScope API. Returns dict on success, None on failure."""
        if not self.configured or not HAS_DASHSCOPE:
            return None

        try:
            dashscope.api_key = self.api_key
            response = Generation.call(
                model="qwen-turbo",
                prompt=query,
                timeout=120,
            )
            if response.status_code == 200:
                return {
                    "answer": response.output.text,
                    "model": "qwen-turbo",
                }
            return None
        except Exception:
            return None
