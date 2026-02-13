"""生成法务测试数据 SQL 脚本 — 合同模板、合同、审查记录"""

import json
import random
from datetime import date, datetime, timedelta

random.seed(88)

lines: list[str] = []


def sql(s: str) -> None:
    lines.append(s)


def q(v: str) -> str:
    return f"'{v.replace(chr(39), chr(39)+chr(39))}'"


sql("-- 法务测试数据 —— 自动生成")
sql("BEGIN;\n")

for t in ["contract_reviews", "contracts", "contract_templates"]:
    sql(f"DELETE FROM {t};")
sql("")

EMPLOYEE_IDS = list(range(1, 21))
EMP_DEPT = {
    1: 7, 2: 7, 3: 8, 4: 9, 5: 3, 6: 4, 7: 5, 8: 6, 9: 2, 10: 7,
    11: 8, 12: 9, 13: 10, 14: 3, 15: 4, 16: 7, 17: 5, 18: 10, 19: 9, 20: 8,
}
now = datetime.now()
today = date.today()

# ── 1. 合同模板（10 条） ──────────────────────────────────────

TEMPLATES = [
    ("标准劳动合同", "劳动合同", "适用于全职员工的标准劳动合同模板"),
    ("试用期劳动合同", "劳动合同", "含试用期条款的劳动合同模板"),
    ("兼职劳动合同", "劳动合同", "适用于兼职员工的简化劳动合同"),
    ("保密协议", "保密协议", "员工保密义务及竞业限制协议"),
    ("竞业限制协议", "保密协议", "离职后竞业限制专项协议"),
    ("标准采购合同", "采购合同", "通用商品或服务采购合同"),
    ("软件采购合同", "采购合同", "软件许可及技术服务采购合同"),
    ("销售合同", "销售合同", "产品或解决方案销售合同"),
    ("技术服务合同", "服务合同", "技术开发及咨询服务合同"),
    ("房屋租赁合同", "其他", "办公场地租赁合同"),
]

sql("-- 合同模板")
for i, (name, ctype, desc) in enumerate(TEMPLATES, 1):
    url = f"https://oa.maxi.com/legal/templates/{i}/download"
    sql(
        f"INSERT INTO contract_templates (id, name, type, description, file_url, created_at, updated_at) "
        f"VALUES ({i}, {q(name)}, {q(ctype)}, {q(desc)}, {q(url)}, {q(str(now))}, {q(str(now))});"
    )
sql("")

# ── 2. 合同记录（60 条） ─────────────────────────────────────

CONTRACT_TYPES = ["劳动合同", "保密协议", "采购合同", "销售合同", "服务合同", "其他"]
STATUSES = ["draft", "pending", "approved", "rejected", "returned", "expired", "terminated"]
PARTY_BS = [
    "张三", "李四", "王五", "赵六", "阿里云计算有限公司", "腾讯科技有限公司",
    "华为技术有限公司", "京东科技有限公司", "百度在线网络技术有限公司",
    "字节跳动有限公司", "美团科技有限公司", "小米科技有限公司",
    "北京优速快递有限公司", "上海数据科技有限公司", "深圳创新软件有限公司",
]

CONTENT_TEMPLATES = {
    "劳动合同": "本合同约定甲方聘用乙方为{position}，合同期限自{start}至{end}。基本工资{salary}元/月，试用期{trial}个月。工作地点为{city}。",
    "保密协议": "乙方在职期间及离职后{years}年内，不得向任何第三方披露甲方的商业秘密、技术秘密和经营信息。违反本协议，乙方须支付违约金{penalty}万元。",
    "采购合同": "甲方向乙方采购{product}，总金额{amount}元。交付期限为{days}个工作日。质保期{warranty}个月。付款方式：验收合格后{payment_days}个工作日内付款。",
    "销售合同": "甲方向乙方提供{product}服务/产品，合同总额{amount}元。服务期限自{start}至{end}。付款分{stages}期，首付{first_ratio}%。",
    "服务合同": "甲方委托乙方提供{service}服务，服务费{amount}元。服务期限{months}个月。乙方须按甲方要求提交工作成果并通过验收。",
    "其他": "本合同约定双方就{subject}事宜达成协议。合同金额{amount}元，有效期自{start}至{end}。",
}

KEY_TERMS_TEMPLATES = {
    "劳动合同": [
        {"term": "薪酬待遇", "detail": "基本工资+绩效奖金+五险一金"},
        {"term": "工作时间", "detail": "标准工时制，每周5天，每天8小时"},
        {"term": "解除条件", "detail": "提前30天书面通知"},
    ],
    "保密协议": [
        {"term": "保密范围", "detail": "技术秘密、经营秘密、客户信息"},
        {"term": "保密期限", "detail": "在职期间及离职后2年"},
        {"term": "违约责任", "detail": "违约金+赔偿实际损失"},
    ],
    "采购合同": [
        {"term": "交付标准", "detail": "符合国家标准及合同约定的技术规格"},
        {"term": "质保条款", "detail": "质保期内免费维修或更换"},
        {"term": "付款条件", "detail": "验收合格后付款"},
    ],
    "销售合同": [
        {"term": "产品/服务范围", "detail": "按合同附件约定的具体内容"},
        {"term": "付款方式", "detail": "分期付款，首付+尾款"},
        {"term": "违约责任", "detail": "逾期付款按日万分之五计算违约金"},
    ],
    "服务合同": [
        {"term": "服务内容", "detail": "按合同约定的服务范围和标准"},
        {"term": "验收标准", "detail": "甲方书面确认验收合格"},
        {"term": "知识产权", "detail": "服务成果知识产权归甲方所有"},
    ],
    "其他": [
        {"term": "合同标的", "detail": "按合同约定"},
        {"term": "有效期", "detail": "自签署之日起生效"},
    ],
}

sql("-- 合同记录")
for i in range(1, 61):
    contract_no = f"LEG-C-{i:04d}"
    ctype = random.choice(CONTRACT_TYPES)
    party_b = random.choice(PARTY_BS)
    emp_id = random.choice(EMPLOYEE_IDS)
    dept_id = EMP_DEPT.get(emp_id, 2)
    amount = round(random.uniform(5000, 500000), 2)

    start_offset = random.randint(-365, 30)
    start_date = today + timedelta(days=start_offset)
    duration = random.randint(180, 1095)
    end_date = start_date + timedelta(days=duration)

    # 根据日期和随机决定状态
    r = random.random()
    if end_date < today and r < 0.5:
        status = "expired"
    elif r < 0.15:
        status = "draft"
    elif r < 0.35:
        status = "pending"
    elif r < 0.7:
        status = "approved"
    elif r < 0.8:
        status = "rejected"
    elif r < 0.9:
        status = "returned"
    else:
        status = "terminated"

    title = f"{party_b} {ctype}"
    if ctype in ("劳动合同", "保密协议"):
        title = f"{party_b} {ctype}"
    else:
        title = f"与{party_b}的{ctype}"

    content = CONTENT_TEMPLATES.get(ctype, "").format(
        position="软件工程师", start=str(start_date), end=str(end_date),
        salary=random.randint(8000, 30000), trial=random.choice([3, 6]),
        city="北京", years=2, penalty=random.randint(10, 50),
        product="云计算服务", amount=amount, days=random.randint(10, 30),
        warranty=random.choice([6, 12, 24]), payment_days=random.choice([15, 30]),
        service="技术咨询", months=random.randint(6, 24),
        stages=random.choice([2, 3]), first_ratio=random.choice([30, 50]),
        subject="场地租赁",
    )

    key_terms = json.dumps(KEY_TERMS_TEMPLATES.get(ctype, []), ensure_ascii=False)

    created_at = now - timedelta(days=random.randint(0, 180))
    sql(
        f"INSERT INTO contracts (id, contract_no, title, type, party_a, party_b, amount, start_date, end_date, status, content, key_terms, submitted_by, department_id, created_at, updated_at) "
        f"VALUES ({i}, {q(contract_no)}, {q(title)}, {q(ctype)}, {q('马喜科技有限公司')}, {q(party_b)}, {amount}, "
        f"{q(str(start_date))}, {q(str(end_date))}, {q(status)}, {q(content)}, {q(key_terms)}, {emp_id}, {dept_id}, "
        f"{q(created_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )
sql("")

# ── 3. 审查记录（30 条） ─────────────────────────────────────

OPINIONS_APPROVED = [
    "条款合规，同意签署",
    "审查通过，无法律风险",
    "条款完整，建议签署",
    "已核实各项条款，通过",
    "合同内容合规，批准",
]
OPINIONS_RETURNED = [
    "违约条款不够明确，请补充",
    "付款条件建议调整为分期付款",
    "保密范围过窄，建议扩大",
    "缺少知识产权归属条款",
    "合同期限与付款周期不匹配，请核对",
]

sql("-- 审查记录")
review_id = 0
for i in range(1, 61):
    # 对 approved / rejected / returned / terminated 状态的合同生成审查记录
    r = random.random()
    if r > 0.5:
        continue
    review_id += 1
    if review_id > 30:
        break
    action = random.choice(["approved", "returned"])
    if action == "approved":
        opinion = random.choice(OPINIONS_APPROVED)
    else:
        opinion = random.choice(OPINIONS_RETURNED)
    reviewer_id = 9  # 郑晓明
    created_at = now - timedelta(days=random.randint(0, 90))
    sql(
        f"INSERT INTO contract_reviews (id, contract_id, reviewer_id, action, opinion, created_at, updated_at) "
        f"VALUES ({review_id}, {i}, {reviewer_id}, {q(action)}, {q(opinion)}, "
        f"{q(created_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )
sql("")

sql("COMMIT;")

output_path = "scripts/legal_seed.sql"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"已生成法务测试数据脚本: {output_path}")
print(f"  - 合同模板: 10 条")
print(f"  - 合同记录: 60 条")
print(f"  - 审查记录: {min(review_id, 30)} 条")
print(f"\n执行方式: sqlite3 data/mx_agent.db < {output_path}")
