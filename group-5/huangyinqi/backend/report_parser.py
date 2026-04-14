"""Report Parser - Extract structured data from PDF/HTML reports."""

import re
import os


class ReportParser:
    """T-046/047/048: Parse PDF and HTML reports, extract title/rating/target_price/core_views."""

    def parse_pdf(self, file_path):
        """Parse PDF file and extract four key elements."""
        text = self._extract_pdf_text(file_path)
        return self._extract_elements(text, os.path.basename(file_path))

    def parse_html(self, file_path):
        """Parse HTML file and extract four key elements."""
        text = self._extract_html_text(file_path)
        return self._extract_elements(text, os.path.basename(file_path))

    @staticmethod
    def _extract_pdf_text(file_path):
        """Extract text from PDF using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts)
        except ImportError:
            # Fallback: read as binary and try basic extraction
            with open(file_path, "rb") as f:
                content = f.read()
            # Simple text extraction from PDF bytes
            text = content.decode("latin-1", errors="ignore")
            return text
        except Exception:
            return ""

    @staticmethod
    def _extract_html_text(file_path):
        """Extract text from HTML file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="gbk", errors="ignore") as f:
                html_content = f.read()

        # Remove HTML tags
        text = re.sub(r"<script[^>]*>.*?</script>", "", html_content, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_elements(self, text, filename=""):
        """Extract title, rating, target_price, core_views from text."""
        title = self._extract_title(text, filename)
        rating = self._extract_rating(text)
        target_price = self._extract_target_price(text)
        core_views = self._extract_core_views(text)

        return {
            "title": title,
            "rating": rating,
            "target_price": target_price,
            "core_views": core_views,
            "full_content": text[:10000] if text else "",
        }

    @staticmethod
    def _extract_title(text, filename=""):
        """Extract report title."""
        # Try to find title from first meaningful line
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if lines:
            first_line = lines[0][:100]
            if len(first_line) > 1:
                return first_line

        # Fallback to filename
        if filename:
            name = filename.rsplit(".", 1)[0]
            return name
        return "未知标题"

    @staticmethod
    def _extract_rating(text):
        """Extract rating from text."""
        patterns = [
            r"(?:投资)?评级[：:]\s*([^\n,，。]{1,10})",
            r"(?:买入|增持|中性|减持|卖出|推荐|谨慎推荐|强烈推荐|优于大市|落后大市)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1) if match.lastindex else match.group(0)
        return "未知"

    @staticmethod
    def _extract_target_price(text):
        """Extract target price from text."""
        patterns = [
            r"目标价[：:]\s*([\d.]+)\s*元",
            r"目标价[：:]\s*([\d.]+)",
            r"目标价\s*([\d.]+)\s*元",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}元"
        return "未知"

    @staticmethod
    def _extract_core_views(text):
        """Extract core views from text."""
        views = []
        patterns = [
            r"核心观点[：:]\s*(.+?)(?:\n\n|\Z)",
            r"投资要点[：:]\s*(.+?)(?:\n\n|\Z)",
            r"摘要[：:]\s*(.+?)(?:\n\n|\Z)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                view_text = match.group(1).strip()
                # Split by numbered items or bullet points
                items = re.split(r"[\d]+[.、)）]|[•·▪]", view_text)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 5:
                        views.append(item[:200])
                break

        if not views:
            # Fallback: take first few sentences as views
            sentences = re.split(r"[。！？]", text[:2000])
            for s in sentences[:3]:
                s = s.strip()
                if s and len(s) > 10:
                    views.append(s[:200])

        return views[:5]
