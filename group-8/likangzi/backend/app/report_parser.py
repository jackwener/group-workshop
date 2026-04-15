"""
研报解析模块 - 解析 PDF/HTML 研报文件，提取关键信息

支持提取：评级(rating)、目标价(target_price)、核心观点(key_points)、摘要(summary)、原文(raw_text)
"""

import re
import signal
import os


PARSE_TIMEOUT = 60  # 秒


def _extract_stock_codes(text):
    """
    从文本中提取股票代码，统一返回 SH600519/SZ000858 格式

    Args:
        text: 原始文本内容
    Returns:
        list: 去重后的股票代码列表
    """
    if not text:
        return []

    stock_codes = []
    seen = set()

    def add_code(prefix, digits):
        if not prefix or not digits or len(digits) != 6:
            return
        normalized = f"{prefix.upper()}{digits}"
        if normalized not in seen:
            seen.add(normalized)
            stock_codes.append(normalized)

    def infer_exchange(digits):
        if digits.startswith("6"):
            return "SH"
        if digits.startswith(("0", "3")):
            return "SZ"
        return None

    patterns = [
        (r'(?<![A-Za-z])(SH|SZ)(\d{6})(?!\d)', lambda match: add_code(match.group(1), match.group(2))),
        (r'(?<![A-Za-z])(\d{6})\.(SH|SZ)(?!\d)', lambda match: add_code(match.group(2), match.group(1))),
        (r'(?:股票代码|证券代码|代码)[：:]\s*(\d{6})(?!\d)', lambda match: add_code(infer_exchange(match.group(1)), match.group(1))),
        (r'(?:代码|股票代码|证券代码|TICKER|ticker)[^\dA-Za-z]{0,20}(\d{6})(?!\d)', lambda match: add_code(infer_exchange(match.group(1)), match.group(1))),
        (r'(?<![A-Za-z])(\d{6})(?!\d)[^\n]{0,20}(?:代码|股票代码|证券代码|TICKER|ticker)', lambda match: add_code(infer_exchange(match.group(1)), match.group(1))),
    ]

    for pattern, handler in patterns:
        for match in re.finditer(pattern, text):
            handler(match)

    return stock_codes


def _find_position_in_text(viewpoint, raw_text):
    """
    在原文中查找观点位置，并返回带上下文的信息

    Args:
        viewpoint: 观点文本
        raw_text: 原始全文
    Returns:
        dict: 包含 text, source_text, position
    """
    position = raw_text.find(viewpoint)
    if position == -1:
        return {"text": viewpoint, "source_text": "", "position": None}
    start = max(0, position - 200)
    end = min(len(raw_text), position + len(viewpoint) + 200)
    source_text = raw_text[start:end]
    return {"text": viewpoint, "source_text": source_text, "position": position}


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
    key_point_texts = []
    sentences = re.split(r'[。\n]', text)
    for s in sentences:
        s = s.strip()
        if len(s) > 10 and len(s) < 200:
            key_point_texts.append(s)
            if len(key_point_texts) >= 5:
                break

    key_points = [_find_position_in_text(viewpoint, text) for viewpoint in key_point_texts]

    # 摘要：取前 500 字符
    summary = text[:500].strip() if text else ""

    return {
        "rating": rating,
        "target_price": target_price,
        "key_points": key_points,
        "summary": summary,
    }


def normalize_v1_data(extracted_data):
    """将V1格式的extracted_data转换为V2格式，确保向后兼容"""
    if not extracted_data:
        return extracted_data

    # 补充 stock_codes 字段
    if "stock_codes" not in extracted_data:
        extracted_data["stock_codes"] = []

    # 转换 key_points 从 string[] 到 object[]
    if extracted_data.get("key_points") and isinstance(extracted_data["key_points"][0], str):
        extracted_data["key_points"] = [
            {"text": kp, "source_text": "", "position": None}
            for kp in extracted_data["key_points"]
        ]

    return extracted_data


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
            "extracted_data": { rating, target_price, key_points, stock_codes, summary, raw_text } | None,
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
        stock_codes = _extract_stock_codes(raw_text)
        
        extracted_data = {
            "rating": key_info["rating"],
            "target_price": key_info["target_price"],
            "key_points": key_info["key_points"],
            "stock_codes": stock_codes,
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
