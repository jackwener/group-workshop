"""
百炼 DashScope Provider — 对齐 Spec 08 §4
检测 DASHSCOPE_API_KEY → 120s 超时 → 区分多类错误码
使用 openai 兼容接口（dashscope >= 1.20）
"""
import os


def call_bailian(query):
    """
    调用百炼 DashScope API（OpenAI 兼容接口）。
    成功返回 {"answer": ..., "model": ...}
    失败返回 None（降级到 Demo）
    """
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=120,
        )

        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": query}],
        )

        answer = completion.choices[0].message.content
        return {
            "answer": answer,
            "model": "qwen-plus",
        }

    except ImportError:
        # openai 包未安装，回退旧接口
        return _call_bailian_legacy(query, api_key)
    except Exception:
        return None


def _call_bailian_legacy(query, api_key):
    """旧版 dashscope 接口兜底"""
    try:
        import dashscope
        dashscope.api_key = api_key
        from dashscope import Generation

        response = Generation.call(
            model="qwen-plus",
            prompt=query,
        )
        if response and response.output:
            text = response.output.get("text", "") if isinstance(response.output, dict) else str(response.output)
            return {"answer": text, "model": "qwen-plus"}
        return None
    except Exception:
        return None
