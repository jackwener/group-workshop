"""
PDF/Word 文件解析模块
"""
import os
import re
from typing import Dict, Optional, Callable


def parse_pdf(file_path: str, progress_callback: Optional[Callable[[int], None]] = None) -> Dict:
    """
    解析 PDF 文件
    
    Args:
        file_path: PDF 文件路径
        progress_callback: 进度回调函数，参数为 0-100 的整数
    
    Returns:
        解析结果字典
    """
    try:
        import fitz  # PyMuPDF
        
        if progress_callback:
            progress_callback(10)
        
        doc = fitz.open(file_path)
        
        # 提取文本
        text_content = []
        total_pages = len(doc)
        
        for i, page in enumerate(doc):
            text_content.append(page.get_text())
            if progress_callback:
                progress = 10 + int((i + 1) / total_pages * 60)
                progress_callback(min(progress, 70))
        
        full_text = "\n".join(text_content)
        
        if progress_callback:
            progress_callback(80)
        
        # 提取关键信息
        result = extract_key_info(full_text)
        
        if progress_callback:
            progress_callback(100)
        
        doc.close()
        
        return {
            "success": True,
            "title": result.get("title", "未知标题"),
            "rating": result.get("rating"),
            "core_views": result.get("core_views", []),
            "text_preview": full_text[:2000] if full_text else "",
            "page_count": total_pages
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "PyMuPDF 未安装"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def parse_word(file_path: str, progress_callback: Optional[Callable[[int], None]] = None) -> Dict:
    """
    解析 Word 文件
    
    Args:
        file_path: Word 文件路径
        progress_callback: 进度回调函数
    
    Returns:
        解析结果字典
    """
    try:
        from docx import Document
        
        if progress_callback:
            progress_callback(10)
        
        doc = Document(file_path)
        
        if progress_callback:
            progress_callback(30)
        
        # 提取段落文本
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        if progress_callback:
            progress_callback(60)
        
        full_text = "\n".join(paragraphs)
        
        if progress_callback:
            progress_callback(80)
        
        # 提取关键信息
        result = extract_key_info(full_text)
        
        if progress_callback:
            progress_callback(100)
        
        return {
            "success": True,
            "title": result.get("title", "未知标题"),
            "rating": result.get("rating"),
            "core_views": result.get("core_views", []),
            "text_preview": full_text[:2000] if full_text else "",
            "paragraph_count": len(paragraphs)
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "python-docx 未安装"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def extract_key_info(text: str) -> Dict:
    """
    从研报文本中提取关键信息
    
    Args:
        text: 研报全文
    
    Returns:
        关键信息字典
    """
    result = {
        "title": None,
        "rating": None,
        "core_views": []
    }
    
    lines = text.split('\n')
    
    # 提取标题（通常是前几行非空且较长的文本）
    for line in lines[:10]:
        line = line.strip()
        if len(line) > 10 and len(line) < 100:
            result["title"] = line
            break
    
    if not result["title"]:
        result["title"] = "研报分析"
    
    # 提取评级（匹配常见评级模式）
    rating_patterns = [
        r'评级[：:]\s*(买入|增持|持有|减持|卖出|强烈推荐|推荐|中性|回避)',
        r'(买入|增持|持有|减持|卖出)[级\s]*评级',
        r'投资评级[：:]\s*(\S+)',
    ]
    
    for pattern in rating_patterns:
        match = re.search(pattern, text)
        if match:
            result["rating"] = match.group(1)
            break
    
    # 提取核心观点（查找"核心观点"、"投资要点"等关键词后的内容）
    view_patterns = [
        r'核心观点[：:](.+?)(?=\n\n|\n[^\s]|$)',
        r'投资要点[：:](.+?)(?=\n\n|\n[^\s]|$)',
        r'主要观点[：:](.+?)(?=\n\n|\n[^\s]|$)',
    ]
    
    for pattern in view_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # 分割成列表（按数字或项目符号）
            views = re.split(r'\n\s*(?:\d+[.．、]|[-•·])\s*', content)
            result["core_views"] = [v.strip() for v in views if len(v.strip()) > 5][:5]
            break
    
    return result


def parse_file(file_path: str, file_type: str, progress_callback: Optional[Callable[[int], None]] = None) -> Dict:
    """
    统一文件解析入口
    
    Args:
        file_path: 文件路径
        file_type: 文件类型（pdf/doc/docx）
        progress_callback: 进度回调函数
    
    Returns:
        解析结果字典
    """
    file_type = file_type.lower()
    
    if file_type == 'pdf':
        return parse_pdf(file_path, progress_callback)
    elif file_type in ['doc', 'docx']:
        return parse_word(file_path, progress_callback)
    else:
        return {
            "success": False,
            "error": f"不支持的文件类型: {file_type}"
        }
