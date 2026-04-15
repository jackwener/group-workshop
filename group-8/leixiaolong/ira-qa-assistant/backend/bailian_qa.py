import os
import logging
import requests

logger = logging.getLogger(__name__)


def is_available():
    return bool(os.environ.get("DASHSCOPE_API_KEY"))


def ask(query, timeout=5):
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        return None
    try:
        resp = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "qwen-max",
                "input": {"prompt": query},
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        output = data.get("output", {})
        return output.get("text")
    except requests.exceptions.Timeout:
        logger.warning("Bailian call timed out")
        return None
    except requests.exceptions.HTTPError as e:
        logger.warning("Bailian HTTP error: %s", e)
        return None
    except Exception as e:
        logger.warning("Bailian call failed: %s", e)
        return None
