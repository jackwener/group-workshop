"""Report Service for PDF generation."""
import os
import io
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.models.report import Report
from app.dao.report_dao import ReportDAO
from app.dao.analysis_dao import AnalysisDAO
from app.utils.security import AuditLogger
from app.utils.errors import ReportNotFoundError


class ReportService:
    """Service for report generation and download."""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.report_dao = ReportDAO(data_dir)
        self.analysis_dao = AnalysisDAO(data_dir)
    
    def generate_report(self, analysis_id: str) -> Report:
        """
        Generate PDF report from analysis.
        
        Aligned with 06-功能规格说明.md §4.1 and 09-API接口规格.md §5.1
        """
        start_time = datetime.now()
        
        # Get analysis
        analysis = self.analysis_dao.get_analysis(analysis_id)
        if not analysis:
            raise ReportNotFoundError(f"Analysis {analysis_id} not found")
        
        # Generate PDF content
        pdf_content = self._generate_pdf(analysis)
        
        # Determine report type and title
        report_type = analysis.type
        if report_type == "stock":
            stock_code = analysis.output_data.get("stock_code", "")
            title = f"{stock_code} 股票分析报告"
        else:
            files = analysis.input_data.get("files", ["研报分析"])
            title = f"{files[0]} 分析报告"
        
        # Create report
        report = self.report_dao.create_report(
            analysis_id=analysis_id,
            session_id=analysis.session_id,
            title=title,
            report_type=report_type,
            content=analysis.output_data,
            pdf_content=pdf_content
        )
        
        # Audit log
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        AuditLogger.log("report.generate", report.id, "success", duration_ms=duration)
        
        return report
    
    def download_report(self, report_id: str, format: str = "pdf") -> tuple:
        """
        Get report for download.
        
        Returns: (content, content_type, filename)
        """
        report = self.report_dao.get_report(report_id)
        if not report:
            raise ReportNotFoundError(f"Report {report_id} not found")
        
        if format == "pdf":
            pdf_path = self.report_dao.get_report_pdf_path(report_id)
            if not pdf_path:
                # Regenerate if PDF missing
                report = self.generate_report(report.analysis_id)
                pdf_path = self.report_dao.get_report_pdf_path(report_id)
            
            with open(pdf_path, 'rb') as f:
                content = f.read()
            
            return (
                content,
                "application/pdf",
                f"report_{report_id}.pdf"
            )
        
        elif format == "json":
            content = self.report_dao.get_report_json(report_id)
            import json
            return (
                json.dumps(content, ensure_ascii=False, indent=2).encode('utf-8'),
                "application/json",
                f"report_{report_id}.json"
            )
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_pdf(self, analysis) -> bytes:
        """Generate PDF content from analysis."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Title
        if analysis.type == "stock":
            title = f"{analysis.output_data.get('stock_name', '')} ({analysis.output_data.get('stock_code', '')}) 分析报告"
        else:
            title = "研报分析报告"
        
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Generated time
        elements.append(Paragraph(
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.3 * inch))
        
        if analysis.type == "stock":
            elements.extend(self._build_stock_content(analysis, styles))
        else:
            elements.extend(self._build_report_content(analysis, styles))
        
        # Build PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
    
    def _build_stock_content(self, analysis, styles):
        """Build content for stock analysis report."""
        elements = []
        data = analysis.output_data
        
        # Summary section
        elements.append(Paragraph("分析摘要", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        
        summary_data = [
            ["综合评分", str(data.get('comprehensive_score', 'N/A'))],
            ["风险等级", data.get('risk_level', 'N/A')],
            ["投资建议", data.get('recommendation', 'N/A')],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Financial indicators
        elements.append(Paragraph("财务指标", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        
        indicators = data.get('financial_indicators', {})
        fin_data = [
            ["指标", "数值"],
            ["营收", str(indicators.get('revenue', 'N/A'))],
            ["净利润", str(indicators.get('profit', 'N/A'))],
            ["ROE", f"{indicators.get('roe', 'N/A')}%"],
            ["PE", str(indicators.get('pe', 'N/A'))],
            ["PB", str(indicators.get('pb', 'N/A'))],
        ]
        
        fin_table = Table(fin_data, colWidths=[2*inch, 3*inch])
        fin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(fin_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Report summary
        elements.append(Paragraph("研报摘要", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(data.get('report_summary', '无'), styles['Normal']))
        
        return elements
    
    def _build_report_content(self, analysis, styles):
        """Build content for report analysis."""
        elements = []
        reports = analysis.output_data.get('reports', [])
        
        for i, report in enumerate(reports, 1):
            elements.append(Paragraph(f"研报 {i}: {report.get('filename', '')}", styles['Heading2']))
            elements.append(Spacer(1, 0.1 * inch))
            
            elements.append(Paragraph(f"标题: {report.get('title', '')}", styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
            
            elements.append(Paragraph("摘要:", styles['Heading3']))
            elements.append(Paragraph(report.get('summary', ''), styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
            
            elements.append(Paragraph("核心观点:", styles['Heading3']))
            for point in report.get('key_points', []):
                elements.append(Paragraph(f"• {point}", styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
            
            elements.append(Paragraph("风险提示:", styles['Heading3']))
            for risk in report.get('risk_warnings', []):
                elements.append(Paragraph(f"• {risk}", styles['Normal']))
            
            elements.append(Spacer(1, 0.3 * inch))
        
        # Comparison section
        comparison = analysis.output_data.get('comparison')
        if comparison:
            elements.append(Paragraph("比对分析", styles['Heading2']))
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(Paragraph(f"相似度: {comparison.get('similarity', 'N/A')}", styles['Normal']))
            elements.append(Paragraph(f"观点一致性: {comparison.get('consistency', 'N/A')}", styles['Normal']))
        
        return elements
