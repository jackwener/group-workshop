# T11 — 研报解析引擎

| 项 | 值 |
|---|---|
| 任务ID | T11 |
| 所属 WBS | W5 研报解析引擎 |
| 里程碑 | **S3** 研报功能 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T01（项目脚手架）, T03（Storage 研报 CRUD） |
| 并行关系 | 与 T08, T09, T10 并行；完成后解锁 T07（parse 端点） |
| 产出文件 | `backend/report_parser.py` |

## 1. 任务目标

实现 PDF/HTML 研报文件解析器，自动提取关键信息（标题、评级、目标价、核心观点、数据预测）。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `09` API | §10.6 | POST /parse 响应含 rating/target_price/core_views/data_forecast |
| `10` 数据模型 | §6 | ParseResult 实体字段定义 |
| `07` 非功能 | §1.1 | 研报解析延迟 < 5000ms |
| `07` 非功能 | §7 | 解析准确率 ≥ 85% |
| `05` 用户故事 | US-003 | AC-003-03：结果 MUST 包含标题、评级、目标价、核心观点 |

## 3. 核心接口

```python
class ReportParser:
    def parse(self, file_path: str, file_type: str) -> dict:
        """
        解析研报文件，返回：
        {
            "title": str,          # 提取的标题
            "rating": str,         # 买入/增持/中性/减持/卖出
            "target_price": str,   # 如 "50元"
            "core_views": list,    # 核心观点列表（≤5条）
            "data_forecast": dict  # 数据预测（营收增速、PE等）
        }
        """
    
    def _parse_pdf(self, file_path: str) -> str:
        """提取 PDF 文本内容"""
    
    def _parse_html(self, file_path: str) -> str:
        """提取 HTML 文本内容"""
    
    def _extract_rating(self, text: str) -> str | None:
        """从文本中提取评级（关键词匹配）"""
    
    def _extract_target_price(self, text: str) -> str | None:
        """从文本中提取目标价（正则匹配）"""
    
    def _extract_core_views(self, text: str) -> list:
        """从文本中提取核心观点（≤5条）"""
```

## 4. 推荐依赖

| 库 | 用途 | 说明 |
|----|------|------|
| `PyPDF2` / `pdfplumber` | PDF 文本提取 | 后者表格支持更好 |
| `beautifulsoup4` | HTML 解析 | 标准选择 |
| `re` | 正则匹配 | 目标价 / 评级关键词 |

## 5. 评级关键词映射

| 评级 | 匹配关键词 |
|------|-----------|
| 买入 | 买入、强烈推荐、强推 |
| 增持 | 增持、推荐 |
| 中性 | 中性、持有、观望 |
| 减持 | 减持、回避 |
| 卖出 | 卖出 |

## 6. 验收标准（AC）

| # | 验收条件 | 关联 TC |
|---|---------|---------|
| AC-01 | 解析 PDF 文件提取出标题 | TC-M01-054 |
| AC-02 | 正确识别评级关键词 | TC-M01-054 |
| AC-03 | 正确提取目标价（含单位） | TC-M01-054 |
| AC-04 | 提取核心观点 ≤ 5 条 | TC-M01-054 |
| AC-05 | 解析耗时 < 5000ms | TC-M01-055 |
| AC-06 | 解析失败返回明确错误（不崩溃） |  |
| AC-07 | HTML 格式文件同样可解析 |  |
