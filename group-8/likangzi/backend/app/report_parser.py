"""
研报解析模块 - 解析 PDF/HTML 研报文件，提取关键信息

支持提取：评级(rating)、目标价(target_price)、核心观点(key_points)、摘要(summary)、原文(raw_text)
"""

import re
import signal
import os


PARSE_TIMEOUT = 60  # 秒


def _extract_key_info(text):
    """
    从文本中提取关键信息：评级、目标价、核心观点
    
    Args:
        text: 原始文本内容
    Returns:
        dict 包含 rating, target_price, key_points, summary
    """
    # 评级提取
    rating = None
    rating_patterns = [
        r'评级[：:]\s*(买入|增持|持有|中性|减持|卖出|推荐|谨慎推荐|强烈推荐)',
        r'投资评级[：:]\s*(买入|增持|持有|中性|减持|卖出|推荐|谨慎推荐|强烈推荐)',
        r'(买入|增持|持有|中性|减持|卖出)\s*评级',
    ]
    for pattern in rating_patterns:
        match = re.search(pattern, text)
        if match:
            rating = match.group(1)
            break

    # 目标价提取
    target_price = None
    price_patterns = [
        r'目标价[：:]\s*(\d+\.?\d*)\s*元',
        r'目标价位[：:]\s*(\d+\.?\d*)\s*元',
        r'目标价\s*(\d+\.?\d*)',
    ]
    for pattern in price_patterns:
        match = re.search(pattern, text)
        if match:
            target_price = match.group(1)
            break

    # 核心观点提取（按句号/换行分割，取前 5 个有意义的句子）
    key_points = []
    sentences = re.split(r'[。\n]', text)
    for s in sentences:
        s = s.strip()
        if len(s) > 10 and len(s) < 200:
            key_points.append(s)
            if len(key_points) >= 5:
                break

    # 摘要：取前 500 字符
    summary = text[:500].strip() if text else ""

    return {
        "rating": rating,
        "target_price": target_price,
        "key_points": key_points,
        "summary": summary,
    }


def _parse_pdf(file_path):
    """
    使用 pdfplumber 解析 PDF 文件
    
    Args:
        file_path: PDF 文件路径
    Returns:
        提取的文本内容
    """
    import pdfplumber
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _parse_html(file_path):
    """
    使用 BeautifulSoup 解析 HTML 文件
    
    Args:
        file_path: HTML 文件路径
    Returns:
        提取的文本内容
    """
    from bs4 import BeautifulSoup
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    # 移除 script 和 style 标签
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def parse_report(file_path, file_type):
    """
    解析研报文件，提取关键信息
    
    Args:
        file_path: 文件路径
        file_type: 文件类型 ('pdf' 或 'html')
    Returns:
        dict: {
            "status": "parsed" | "failed",
            "extracted_data": { rating, target_price, key_points, summary, raw_text } | None,
            "error_message": str | None
        }
    """
    try:
        if not os.path.exists(file_path):
            return {
                "status": "failed",
                "extracted_data": None,
                "error_message": f"文件不存在: {file_path}"
            }

        # 根据文件类型选择解析器
        if file_type == "pdf":
            raw_text = _parse_pdf(file_path)
        elif file_type == "html":
            raw_text = _parse_html(file_path)
        else:
            return {
                "status": "failed",
                "extracted_data": None,
                "error_message": f"不支持的文件类型: {file_type}"
            }

        if not raw_text or not raw_text.strip():
            return {
                "status": "failed",
                "extracted_data": None,
                "error_message": "文件内容为空"
            }

        # 提取关键信息
        key_info = _extract_key_info(raw_text)
        
        extracted_data = {
            "rating": key_info["rating"],
            "target_price": key_info["target_price"],
            "key_points": key_info["key_points"],
            "summary": key_info["summary"],
            "raw_text": raw_text,
        }

        return {
            "status": "parsed",
            "extracted_data": extracted_data,
            "error_message": None,
        }

    except Exception as e:
        return {
            "status": "failed",
            "extracted_data": None,
            "error_message": str(e),
        }
