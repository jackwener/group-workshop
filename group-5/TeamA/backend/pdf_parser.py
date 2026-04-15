"""
PDF/Word 文件解析引擎 — 对齐 Spec 08 §2 File Parser 层
"""


class PDFParser:
    """文件解析器（PDF/Word 文本提取）"""

    def parse(self, file_path, file_type):
        """
        解析文件，返回解析结果
        对齐 Spec 10 §7：解析超时 30s → parse_status=failed
        """
        # TODO: 实现真实 PDF/Word 解析
        # 可选库：PyPDF2, pdfplumber, python-docx
        try:
            if file_type == "pdf":
                return self._parse_pdf(file_path)
            elif file_type in ("doc", "docx"):
                return self._parse_word(file_path)
            return None
        except Exception as e:
            return {"error": str(e)}

    def _parse_pdf(self, file_path):
        """PDF 解析 stub"""
        # TODO: 使用 pdfplumber 或 PyPDF2 实现
        return {
            "title": "研报标题（待解析）",
            "content": "PDF 内容提取待实现",
            "pages": 0,
        }

    def _parse_word(self, file_path):
        """Word 解析 stub"""
        # TODO: 使用 python-docx 实现
        return {
            "title": "研报标题（待解析）",
            "content": "Word 内容提取待实现",
            "pages": 0,
        }


# 单例
pdf_parser = PDFParser()
