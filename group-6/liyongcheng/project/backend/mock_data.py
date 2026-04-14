"""Mock 数据生成脚本"""
import json
from pathlib import Path
from datetime import datetime, timezone

# 数据目录
data_dir = Path('./data')
data_dir.mkdir(parents=True, exist_ok=True)
reports_file = data_dir / 'reports.json'

# Mock 研报数据
mock_reports = [
    {
        "id": "rpt_a1b2c3d4e5f6",
        "title": "贵州茅台(600519)深度研究：品牌护城河深厚，长期价值凸显",
        "subject_name": "贵州茅台",
        "subject_code": "600519",
        "author": "张三",
        "rating": "买入",
        "trend": "positive",
        "target_price": 1850.00,
        "summary": "贵州茅台作为中国白酒行业龙头企业，拥有强大的品牌护城河和定价权。公司核心产品飞天茅台供不应求，渠道库存健康。预计2024-2026年EPS分别为58.2元、65.8元、73.5元，维持\"买入\"评级。",
        "file_path": "",
        "created_at": "2024-01-15T08:30:00Z",
        "updated_at": "2024-01-15T08:30:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_b2c3d4e5f6g7",
        "title": "宁德时代(300750)业绩点评：全球动力电池龙头地位稳固",
        "subject_name": "宁德时代",
        "subject_code": "300750",
        "author": "李四",
        "rating": "增持",
        "trend": "positive",
        "target_price": 220.00,
        "summary": "宁德时代2023年出货量继续领跑全球，市占率超35%。公司技术迭代加速，麒麟电池、神行电池等新品放量。海外市场拓展顺利，与多家国际车企达成战略合作。预计2024年净利润同比增长25%-30%。",
        "file_path": "",
        "created_at": "2024-01-20T10:15:00Z",
        "updated_at": "2024-01-20T10:15:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_c3d4e5f6g7h8",
        "title": "比亚迪(002594)调研报告：新能源汽车销量持续高增",
        "subject_name": "比亚迪",
        "subject_code": "002594",
        "author": "王五",
        "rating": "买入",
        "trend": "positive",
        "target_price": 280.00,
        "summary": "比亚迪2023年新能源汽车销量突破300万辆，同比增长超60%。公司垂直整合优势明显，成本控制能力强。高端品牌仰望、方程豹陆续交付，产品结构持续优化。预计2024年销量目标400万辆。",
        "file_path": "",
        "created_at": "2024-02-05T14:20:00Z",
        "updated_at": "2024-02-05T14:20:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_d4e5f6g7h8i9",
        "title": "腾讯控股(00700)四季度业绩前瞻：游戏业务回暖，广告复苏",
        "subject_name": "腾讯控股",
        "subject_code": "00700",
        "author": "赵六",
        "rating": "买入",
        "trend": "positive",
        "target_price": 380.00,
        "summary": "腾讯Q4游戏业务受益于新游上线，流水环比增长10%。广告业务随宏观经济复苏，视频号广告收入贡献提升。金融科技业务稳健增长，云服务亏损收窄。目标价380港元，维持\"买入\"评级。",
        "file_path": "",
        "created_at": "2024-02-10T09:45:00Z",
        "updated_at": "2024-02-10T09:45:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_e5f6g7h8i9j0",
        "title": "阿里巴巴(09988)战略调整点评：聚焦核心业务，提升运营效率",
        "subject_name": "阿里巴巴",
        "subject_code": "09988",
        "author": "钱七",
        "rating": "增持",
        "trend": "neutral",
        "target_price": 85.00,
        "summary": "阿里近期宣布组织架构调整，聚焦电商和云计算两大核心业务。淘宝天猫集团加大投入提升用户体验，阿里云保持盈利。国际业务、本地生活等板块独立运营，提升决策效率。预计FY2024收入同比增长8%。",
        "file_path": "",
        "created_at": "2024-02-15T11:30:00Z",
        "updated_at": "2024-02-15T11:30:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_f6g7h8i9j0k1",
        "title": "中国平安(601318)保险业务分析：寿险改革成效显现",
        "subject_name": "中国平安",
        "subject_code": "601318",
        "author": "孙八",
        "rating": "增持",
        "trend": "neutral",
        "target_price": 48.00,
        "summary": "平安寿险改革持续推进，代理人队伍质态改善，人均产能提升20%以上。财险业务综合成本率控制在98%以内，盈利能力稳健。银行、资管等业务协同发展。预计2024年NBV同比增长15%。",
        "file_path": "",
        "created_at": "2024-02-20T13:00:00Z",
        "updated_at": "2024-02-20T13:00:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_g7h8i9j0k1l2",
        "title": "美团(03690)本地生活业务深度报告：护城河加深，盈利改善",
        "subject_name": "美团",
        "subject_code": "03690",
        "author": "周九",
        "rating": "买入",
        "trend": "positive",
        "target_price": 120.00,
        "summary": "美团外卖业务市占率稳定在70%以上，单均盈利持续改善。到店酒旅业务复苏强劲，Q4收入同比增长40%。闪购业务快速增长，成为新的增长引擎。预计2024年实现全面盈利。",
        "file_path": "",
        "created_at": "2024-02-25T15:30:00Z",
        "updated_at": "2024-02-25T15:30:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_h8i9j0k1l2m3",
        "title": "招商银行(600036)零售银行业务分析：财富管理能力领先",
        "subject_name": "招商银行",
        "subject_code": "600036",
        "author": "吴十",
        "rating": "买入",
        "trend": "positive",
        "target_price": 42.00,
        "summary": "招行零售客户数突破2亿，AUM规模稳居股份行第一。财富管理业务手续费收入占比提升，轻资本转型成效显著。资产质量保持优良，不良率低于1%。目标价42元，维持\"买入\"评级。",
        "file_path": "",
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": "2024-03-01T10:00:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_i9j0k1l2m3n4",
        "title": "小米集团(01810)智能汽车业务点评：SU7发布在即，生态协同可期",
        "subject_name": "小米集团",
        "subject_code": "01810",
        "author": "郑一",
        "rating": "增持",
        "trend": "neutral",
        "target_price": 16.50,
        "summary": "小米首款汽车SU7将于3月底正式发布，定位中高端纯电轿车。公司手机业务全球市占率稳居前三，IoT生态持续扩展。汽车业务有望与现有生态形成协同，长期看好公司\"人车家\"战略。",
        "file_path": "",
        "created_at": "2024-03-05T09:15:00Z",
        "updated_at": "2024-03-05T09:15:00Z",
        "parse_status": "success"
    },
    {
        "id": "rpt_j0k1l2m3n4o5",
        "title": "中芯国际(00981)晶圆代工业务分析：国产替代加速，产能持续扩张",
        "subject_name": "中芯国际",
        "subject_code": "00981",
        "author": "冯二",
        "rating": "增持",
        "trend": "positive",
        "target_price": 28.00,
        "summary": "中芯国际作为国内晶圆代工龙头，受益于半导体国产替代加速。公司12英寸产能持续爬坡，成熟制程产能利用率回升。先进制程研发稳步推进，长期竞争力增强。预计2024年收入同比增长15%-20%。",
        "file_path": "",
        "created_at": "2024-03-10T11:45:00Z",
        "updated_at": "2024-03-10T11:45:00Z",
        "parse_status": "success"
    }
]

# 写入文件
with open(reports_file, 'w', encoding='utf-8') as f:
    json.dump(mock_reports, f, ensure_ascii=False, indent=2)

print(f"✅ Mock 数据已生成：{reports_file}")
print(f"📊 共生成 {len(mock_reports)} 条研报数据")
print("\n📈 数据概览：")
print(f"   - 买入评级：{sum(1 for r in mock_reports if r['rating'] == '买入')} 条")
print(f"   - 增持评级：{sum(1 for r in mock_reports if r['rating'] == '增持')} 条")
print(f"   - 看多趋势：{sum(1 for r in mock_reports if r['trend'] == 'positive')} 条")
print(f"   - 中性趋势：{sum(1 for r in mock_reports if r['trend'] == 'neutral')} 条")
