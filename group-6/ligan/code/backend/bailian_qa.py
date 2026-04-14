import os

try:
    import dashscope
    from dashscope import Generation
    HAS_DASHSCOPE = True
except ImportError:
    HAS_DASHSCOPE = False


class BailianQA:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.configured = bool(self.api_key)

    def ask(self, query):
        if not self.configured or not HAS_DASHSCOPE:
            return None
        try:
            dashscope.api_key = self.api_key
            response = Generation.call(
                model="qwen-max",
                prompt=query,
                timeout=120,
            )
            if response and response.output:
                return {
                    "answer": response.output.text,
                    "llm_used": True,
                    "model": "qwen-max",
                    "answer_source": "bailian",
                }
            return None
        except Exception:
            return None
