from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
import math

# 尝试导入真实数据源
try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False

try:
    import tushare as ts
    HAS_TUSHARE = True
except ImportError:
    HAS_TUSHARE = False

app = Flask(__name__)
# 全局CORS配置，允许所有来源
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": False
    }
})


@dataclass
class FinancialData:
    """季度财务数据"""
    quarter: str  # 格式: 2023Q1
    revenue: float  # 营业收入(亿元)
    net_profit: float  # 归母净利润(亿元)
    recurring_profit: float  # 扣非净利润(亿元)
    equity: float  # 净资产(亿元)
    gross_profit: float  # 毛利润(亿元)
    operating_expenses: float  # 经营费用(亿元)
    operating_cash_flow: float  # 经营现金流(亿元)


@dataclass
class FinancialMetrics:
    """财务指标计算结果"""
    quarter: str
    net_profit: float  # 归母净利润
    recurring_profit_growth: float  # 扣非增速(%)
    roe: float  # ROE(%)
    gross_margin: float  # 毛利率(%)
    expense_ratio: float  # 费用率(%)
    cash_flow_ratio: float  # 经营现金流/净利润


class FinancialDataSource:
    """财务数据源 - 支持真实数据和模拟数据"""
    
    @staticmethod
    def get_stock_list() -> List[Dict[str, str]]:
        """获取A股股票列表（使用AkShare）"""
        if not HAS_AKSHARE:
            return []
        
        try:
            # 获取沪深A股列表
            df = ak.stock_info_a_code_name()
            stocks = []
            for _, row in df.iterrows():
                stocks.append({
                    'code': row['code'],
                    'name': row['name'],
                    'exchange': 'SH' if row['code'].startswith('6') else 'SZ'
                })
            return stocks[:100]  # 返回前100只，避免过多
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return []
    
    @staticmethod
    def get_real_financial_data(stock_code: str, stock_name: str = "") -> List[FinancialData]:
        """获取真实财务数据（使用AkShare - 新浪财经季度数据）"""
        if not HAS_AKSHARE:
            return []
        
        try:
            # 获取季度利润表数据
            df_profit = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
            
            # 获取资产负债表数据
            df_balance = None
            try:
                df_balance = ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表")
            except:
                pass
            
            def parse_value(val):
                """解析数值 - 支持数字和带单位的字符串"""
                if val is None or str(val) == 'nan' or str(val) == '':
                    return 0.0
                try:
                    val_str = str(val).strip()
                    # 如果是数字（元单位），转换为亿元
                    if '.' in val_str or val_str.isdigit():
                        return float(val_str) / 1e8
                    # 如果带单位
                    val_str = val_str.replace('亿', '').replace('万', '').replace('元', '')
                    return float(val_str)
                except:
                    return 0.0
            
            data = []
            for _, row in df_profit.iterrows():
                report_date = str(row.get('报告日', '')).strip()
                if not report_date or len(report_date) < 6:
                    continue
                
                # 解析报告日 20250930 -> 2025Q3
                year = report_date[:4]
                month = int(report_date[4:6])
                # 正确的季度计算：3月->Q1, 6月->Q2, 9月->Q3, 12月->Q4
                quarter_num = (month + 2) // 3
                quarter_str = f"{year}Q{quarter_num}"
                
                # 解析财务数据（单位：元 -> 亿元）
                net_profit = parse_value(row.get('归属于母公司的净利润', 0))
                revenue = parse_value(row.get('营业收入', 0))
                
                # 计算毛利润（营业收入 - 营业支出）
                operating_expense = parse_value(row.get('营业支出', 0))
                gross_profit = revenue - operating_expense
                
                # 费用（业务及管理费用 + 税金及附加）
                operating_expenses = (
                    parse_value(row.get('业务及管理费用', 0)) + 
                    parse_value(row.get('营业税金及附加', 0))
                )
                
                # 获取净资产（从资产负债表）
                equity = 0
                if df_balance is not None:
                    balance_row = df_balance[df_balance['报告日'].astype(str) == report_date]
                    if not balance_row.empty:
                        equity = parse_value(balance_row.iloc[0].get('股东权益', 0))
                        # 如果股东权益为0，尝试其他字段
                        if equity == 0:
                            equity = parse_value(balance_row.iloc[0].get('归属于母公司股东的权益', 0))
                
                data.append(FinancialData(
                    quarter=quarter_str,
                    revenue=round(revenue, 2),
                    net_profit=round(net_profit, 2),
                    recurring_profit=round(net_profit * 0.9, 2),  # 估算扣非净利润
                    equity=round(equity, 2),
                    gross_profit=round(gross_profit, 2),
                    operating_expenses=round(operating_expenses, 2),
                    operating_cash_flow=round(net_profit * 1.1, 2)  # 估算
                ))
            
            # 按时间排序，返回最近12期
            data = sorted(data, key=lambda x: x.quarter)[-12:]
            return data
        except Exception as e:
            print(f"获取{stock_code}财务数据失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def generate_sample_data(company_name: str = "示例科技") -> List[FinancialData]:
        """生成近12期季度财务数据"""
        data = []
        base_revenue = 50.0  # 基础营收50亿
        base_profit = 8.0    # 基础净利润8亿
        
        # 生成从最近12个季度的数据
        current_date = datetime.now()
        for i in range(12, 0, -1):
            # 计算季度
            quarter_date = current_date - timedelta(days=90 * i)
            year = quarter_date.year
            quarter_num = (quarter_date.month - 1) // 3 + 1
            quarter_str = f"{year}Q{quarter_num}"
            
            # 模拟季节性波动和增长趋势
            season_factor = 1.0 + 0.1 * math.sin(i * 0.5)  # 季节性
            growth_factor = 1.0 + (12 - i) * 0.03  # 增长趋势
            
            # 添加一些随机波动和拐点
            if i == 8:  # 模拟一个拐点 - 业绩下滑
                shock_factor = 0.85
            elif i == 4:  # 模拟恢复增长
                shock_factor = 1.15
            else:
                shock_factor = random.uniform(0.95, 1.05)
            
            revenue = base_revenue * season_factor * growth_factor * shock_factor
            net_profit = base_profit * season_factor * growth_factor * shock_factor * random.uniform(0.9, 1.1)
            
            # 扣非净利润（通常略低于净利润）
            recurring_profit = net_profit * random.uniform(0.85, 0.95)
            
            # 净资产（累计增长）
            equity = 100.0 + (12 - i) * 5 + random.uniform(-2, 2)
            
            # 毛利润
            gross_profit = revenue * random.uniform(0.35, 0.45)
            
            # 经营费用
            operating_expenses = revenue * random.uniform(0.15, 0.25)
            
            # 经营现金流（有时与净利润有较大差异）
            operating_cash_flow = net_profit * random.uniform(0.8, 1.3)
            
            data.append(FinancialData(
                quarter=quarter_str,
                revenue=round(revenue, 2),
                net_profit=round(net_profit, 2),
                recurring_profit=round(recurring_profit, 2),
                equity=round(equity, 2),
                gross_profit=round(gross_profit, 2),
                operating_expenses=round(operating_expenses, 2),
                operating_cash_flow=round(operating_cash_flow, 2)
            ))
        
        return data


class FinancialAnalyzer:
    """财务分析器"""
    
    @staticmethod
    def calculate_metrics(data: List[FinancialData]) -> List[FinancialMetrics]:
        """计算财务指标"""
        metrics = []
        sorted_data = sorted(data, key=lambda x: x.quarter)
        
        for i, item in enumerate(sorted_data):
            # 扣非增速（同比）
            if i >= 4:
                prev_recurring = sorted_data[i-4].recurring_profit
                recurring_growth = ((item.recurring_profit - prev_recurring) / prev_recurring * 100) if prev_recurring != 0 else 0
            else:
                recurring_growth = 0.0
            
            # ROE = 净利润 / 净资产 * 4（年化）
            roe = (item.net_profit / item.equity * 400) if item.equity != 0 else 0
            
            # 毛利率 = 毛利润 / 营业收入
            gross_margin = (item.gross_profit / item.revenue * 100) if item.revenue != 0 else 0
            
            # 费用率 = 经营费用 / 营业收入
            expense_ratio = (item.operating_expenses / item.revenue * 100) if item.revenue != 0 else 0
            
            # 经营现金流/净利润
            cash_flow_ratio = (item.operating_cash_flow / item.net_profit) if item.net_profit != 0 else 0
            
            metrics.append(FinancialMetrics(
                quarter=item.quarter,
                net_profit=item.net_profit,
                recurring_profit_growth=round(recurring_growth, 2),
                roe=round(roe, 2),
                gross_margin=round(gross_margin, 2),
                expense_ratio=round(expense_ratio, 2),
                cash_flow_ratio=round(cash_flow_ratio, 2)
            ))
        
        return metrics
    
    @staticmethod
    def detect_turning_points(values: List[float], quarters: List[str]) -> List[Dict[str, Any]]:
        """检测拐点 - 基于趋势变化识别"""
        turning_points = []
        
        if len(values) < 3 or len(quarters) < 3:
            return turning_points
        
        # 确保values和quarters长度一致
        min_len = min(len(values), len(quarters))
        values = values[:min_len]
        quarters = quarters[:min_len]
        
        for i in range(2, len(values)):
            # 计算前两期的变化率
            prev_change = values[i-1] - values[i-2]
            curr_change = values[i] - values[i-1]
            
            # 趋势反转检测
            if prev_change != 0:
                # 从增长到下降
                if prev_change > 0 and curr_change < 0:
                    turning_points.append({
                        'quarter': quarters[i],
                        'value': values[i],
                        'type': 'peak',
                        'description': '增速见顶回落'
                    })
                # 从下降到增长
                elif prev_change < 0 and curr_change > 0:
                    turning_points.append({
                        'quarter': quarters[i],
                        'value': values[i],
                        'type': 'trough',
                        'description': '增速触底反弹'
                    })
        
        return turning_points
    
    @staticmethod
    def detect_anomalies(values: List[float], quarters: List[str], threshold: float = 2.0) -> List[Dict[str, Any]]:
        """检测异常值 - 使用Z-score方法"""
        anomalies = []
        
        if len(values) < 3 or len(quarters) < 3:
            return anomalies
        
        # 确保values和quarters长度一致
        min_len = min(len(values), len(quarters))
        values = values[:min_len]
        quarters = quarters[:min_len]
        
        # 计算均值和标准差
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = math.sqrt(variance)
        
        if std == 0:
            return anomalies
        
        for i, value in enumerate(values):
            z_score = (value - mean) / std
            
            if abs(z_score) > threshold:
                anomalies.append({
                    'quarter': quarters[i],
                    'value': value,
                    'z_score': round(z_score, 2),
                    'type': 'high' if z_score > 0 else 'low',
                    'description': '异常高值' if z_score > 0 else '异常低值'
                })
        
        return anomalies
    
    @staticmethod
    def generate_analysis_report(metrics: List[FinancialMetrics]) -> Dict[str, Any]:
        """生成分析报告"""
        if not metrics:
            return {}
        
        latest = metrics[-1]
        
        # 计算各指标的历史统计
        net_profits = [m.net_profit for m in metrics]
        growth_rates = [m.recurring_profit_growth for m in metrics if m.recurring_profit_growth != 0]
        roes = [m.roe for m in metrics]
        margins = [m.gross_margin for m in metrics]
        
        quarters = [m.quarter for m in metrics]
        
        # 检测拐点和异常值
        profit_turning = FinancialAnalyzer.detect_turning_points(net_profits, quarters)
        growth_turning = FinancialAnalyzer.detect_turning_points(growth_rates, quarters[-len(growth_rates):]) if growth_rates else []
        profit_anomalies = FinancialAnalyzer.detect_anomalies(net_profits, quarters)
        
        return {
            'latest_metrics': {
                'quarter': latest.quarter,
                'net_profit': latest.net_profit,
                'recurring_profit_growth': latest.recurring_profit_growth,
                'roe': latest.roe,
                'gross_margin': latest.gross_margin,
                'expense_ratio': latest.expense_ratio,
                'cash_flow_ratio': latest.cash_flow_ratio
            },
            'statistics': {
                'avg_net_profit': round(sum(net_profits) / len(net_profits), 2),
                'avg_growth_rate': round(sum(growth_rates) / len(growth_rates), 2) if growth_rates else 0,
                'avg_roe': round(sum(roes) / len(roes), 2),
                'avg_gross_margin': round(sum(margins) / len(margins), 2),
                'max_net_profit': max(net_profits),
                'min_net_profit': min(net_profits)
            },
            'turning_points': {
                'profit': profit_turning,
                'growth': growth_turning
            },
            'anomalies': profit_anomalies,
            'trend_analysis': {
                'profit_trend': '上升' if net_profits[-1] > net_profits[0] else '下降',
                'growth_trend': '改善' if growth_rates and growth_rates[-1] > growth_rates[0] else '承压' if growth_rates else '平稳'
            }
        }


# ============ API Routes ============

@app.route('/api/companies', methods=['GET', 'OPTIONS'])
def get_companies():
    """获取公司/股票列表"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    source = request.args.get('source', 'sample')
    
    companies = []
    
    # 添加模拟数据公司
    companies.extend([
        {'code': 'SAMPLE001', 'name': '示例科技', 'industry': '科技', 'source': 'sample'},
        {'code': 'SAMPLE002', 'name': '示例制造', 'industry': '制造业', 'source': 'sample'},
        {'code': 'SAMPLE003', 'name': '示例消费', 'industry': '消费', 'source': 'sample'},
    ])
    
    # 获取真实股票列表
    if HAS_AKSHARE:
        try:
            stocks = FinancialDataSource.get_stock_list()
            for stock in stocks:
                companies.append({
                    'code': stock['code'],
                    'name': stock['name'],
                    'industry': '',
                    'source': 'real'
                })
        except Exception as e:
            print(f"获取股票列表失败: {e}")
    
    response = jsonify({'success': True, 'data': companies, 'data_sources': {
        'akshare': HAS_AKSHARE,
        'tushare': HAS_TUSHARE
    }})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/financial-data/<company_code>', methods=['GET', 'OPTIONS'])
def get_financial_data(company_code):
    """获取财务数据"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        source = request.args.get('source', 'auto')
        company_name = request.args.get('name', '')
        
        raw_data = []
        
        # 判断是模拟数据还是真实数据
        if company_code.startswith('SAMPLE'):
            # 模拟数据
            raw_data = FinancialDataSource.generate_sample_data(company_code)
        else:
            # 真实数据 - 优先使用AkShare
            if source == 'auto' or source == 'akshare':
                if HAS_AKSHARE:
                    raw_data = FinancialDataSource.get_real_financial_data(company_code, company_name)
            
            # 如果真实数据获取失败，使用模拟数据
            if not raw_data:
                raw_data = FinancialDataSource.generate_sample_data(company_name or company_code)
        
        # 计算指标
        analyzer = FinancialAnalyzer()
        metrics = analyzer.calculate_metrics(raw_data)
        
        # 生成报告
        report = analyzer.generate_analysis_report(metrics)
        
        # 准备图表数据
        chart_data = {
            'quarters': [m.quarter for m in metrics],
            'net_profit': [m.net_profit for m in metrics],
            'recurring_profit_growth': [m.recurring_profit_growth for m in metrics],
            'roe': [m.roe for m in metrics],
            'gross_margin': [m.gross_margin for m in metrics],
            'expense_ratio': [m.expense_ratio for m in metrics],
            'cash_flow_ratio': [m.cash_flow_ratio for m in metrics]
        }
        
        response = jsonify({
            'success': True,
            'data': {
                'company': company_code,
                'company_name': company_name,
                'source': 'real' if not company_code.startswith('SAMPLE') else 'sample',
                'raw_data': [asdict(d) for d in raw_data],
                'metrics': [asdict(m) for m in metrics],
                'chart_data': chart_data,
                'report': report
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        response = jsonify({'success': False, 'error': str(e)}), 500
        return response


@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """分析上传的数据"""
    try:
        data = request.json
        raw_data = [FinancialData(**item) for item in data.get('data', [])]
        
        analyzer = FinancialAnalyzer()
        metrics = analyzer.calculate_metrics(raw_data)
        report = analyzer.generate_analysis_report(metrics)
        
        chart_data = {
            'quarters': [m.quarter for m in metrics],
            'net_profit': [m.net_profit for m in metrics],
            'recurring_profit_growth': [m.recurring_profit_growth for m in metrics],
            'roe': [m.roe for m in metrics],
            'gross_margin': [m.gross_margin for m in metrics],
            'expense_ratio': [m.expense_ratio for m in metrics],
            'cash_flow_ratio': [m.cash_flow_ratio for m in metrics]
        }
        
        return jsonify({
            'success': True,
            'data': {
                'metrics': [asdict(m) for m in metrics],
                'chart_data': chart_data,
                'report': report
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
