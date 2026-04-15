import os
import logging
import requests

logger = logging.getLogger(__name__)


def is_available():
    return bool(os.environ.get("IRA_COPAW_CHAT_URL"))


def ask(query, timeout=3):
    chat_url = os.environ.get("IRA_COPAW_CHAT_URL")
    if not chat_url:
        return None
    try:
        resp = requests.post(
            chat_url,
            json={"query": query},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("answer") or data.get("result")
    except Exception as e:
        logger.warning("CoPaw call failed: %s", e)
        return None
