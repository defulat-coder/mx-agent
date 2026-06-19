"""生成财务测试数据 SQL 脚本 — 报销单、明细、预算、应收应付"""

import random
from datetime import date, datetime, timedelta

random.seed(66)

lines: list[str] = []


def sql(s: str) -> None:
    lines.append(s)


def q(v: str) -> str:
    return f"'{v}'"


sql("-- 财务测试数据 —— 自动生成")
sql("BEGIN;\n")

for t in ["budget_usages", "reimbursement_items", "reimbursements", "budgets", "payables", "receivables"]:
    sql(f"DELETE FROM {t};")
sql("")

EMPLOYEE_IDS = list(range(1, 21))
EMP_DEPT = {
    1: 7, 2: 7, 3: 8, 4: 9, 5: 3, 6: 4, 7: 5, 8: 6, 9: 2, 10: 7,
    11: 8, 12: 9, 13: 10, 14: 3, 15: 4, 16: 7, 17: 5, 18: 10, 19: 9, 20: 8,
}
DEPT_IDS = [2, 3, 4, 5, 6, 7, 8, 9, 10]
now = datetime.now()
today = date.today()
current_year = today.year

# ── 1. 报销单（20 条） ──────────────────────────────────────

REIMB_TYPES = ["差旅", "餐费", "交通", "办公", "招待", "其他"]
STATUSES = ["pending", "approved", "rejected", "returned", "paid"]

sql("-- 报销单")
for i in range(20):
    rid = i + 1
    reimb_no = f"FIN-R-{rid:04d}"
    emp_id = random.choice(EMPLOYEE_IDS)
    dept_id = EMP_DEPT.get(emp_id, 2)
    rtype = random.choice(REIMB_TYPES)
    amount = round(random.uniform(100, 5000), 2)

    r = random.random()
    if r < 0.3:
        status = "pending"
        reviewer_id = "NULL"
        review_remark = ""
        reviewed_at = "NULL"
    elif r < 0.6:
        status = "approved"
        reviewer_id = "9"
        review_remark = "审核通过"
        reviewed_at = q((now - timedelta(days=random.randint(1, 20))).strftime("%Y-%m-%d %H:%M:%S"))
    elif r < 0.75:
        status = "paid"
        reviewer_id = "9"
        review_remark = "已付款"
        reviewed_at = q((now - timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d %H:%M:%S"))
    elif r < 0.9:
        status = "rejected"
        reviewer_id = "9"
        review_remark = "发票不合规，请重新提交"
        reviewed_at = q((now - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d %H:%M:%S"))
    else:
        status = "returned"
        reviewer_id = "9"
        review_remark = "金额有误，请核对后重新提交"
        reviewed_at = q((now - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S"))

    created_at = now - timedelta(days=random.randint(0, 60))
    sql(
        f"INSERT INTO reimbursements (id, reimbursement_no, employee_id, type, amount, status, reviewer_id, review_remark, reviewed_at, department_id, created_at, updated_at) "
        f"VALUES ({rid}, {q(reimb_no)}, {emp_id}, {q(rtype)}, {amount}, {q(status)}, {reviewer_id}, {q(review_remark)}, {reviewed_at}, "
        f"{dept_id}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )
sql("")

# ── 2. 报销明细（40 条） ─────────────────────────────────────

ITEM_DESCS = {
    "差旅": ["北京-上海机票", "酒店住宿 2 晚", "市内出租车", "高铁票"],
    "餐费": ["团队聚餐", "加班餐", "客户午餐"],
    "交通": ["打车费用", "地铁月卡", "油费"],
    "办公": ["专业书籍", "软件订阅", "会议白板"],
    "招待": ["客户晚宴", "商务茶歇", "礼品采购"],
    "其他": ["快递费", "通讯费", "杂项"],
}
CATEGORIES = ["差旅", "餐费", "交通", "办公", "招待", "其他"]

sql("-- 报销明细")
item_id = 0
for reimb_id in range(1, 21):
    num_items = random.randint(1, 3)
    for _ in range(num_items):
        item_id += 1
        if item_id > 40:
            break
        cat = random.choice(CATEGORIES)
        desc = random.choice(ITEM_DESCS.get(cat, ["其他费用"]))
        amount = round(random.uniform(50, 2000), 2)
        exp_date = today - timedelta(days=random.randint(1, 60))
        sql(
            f"INSERT INTO reimbursement_items (id, reimbursement_id, description, amount, expense_date, category, created_at, updated_at) "
            f"VALUES ({item_id}, {reimb_id}, {q(desc)}, {amount}, {q(str(exp_date))}, {q(cat)}, {q(str(now))}, {q(str(now))});"
        )
    if item_id > 40:
        break
sql("")

# ── 3. 预算（10 条） ────────────────────────────────────────

sql("-- 部门预算")
for i, dept_id in enumerate(DEPT_IDS, 1):
    if i > 10:
        break
    total = round(random.uniform(100000, 500000), 2)
    used = round(random.uniform(total * 0.3, total * 0.95), 2)
    sql(
        f"INSERT INTO budgets (id, department_id, year, total_amount, used_amount, status, created_at, updated_at) "
        f"VALUES ({i}, {dept_id}, {current_year}, {total}, {used}, 'active', {q(str(now))}, {q(str(now))});"
    )
sql("")

# ── 4. 预算使用记录（15 条） ──────────────────────────────────

sql("-- 预算使用记录")
for i in range(1, 16):
    budget_id = random.randint(1, min(10, len(DEPT_IDS)))
    amount = round(random.uniform(500, 10000), 2)
    cat = random.choice(CATEGORIES)
    desc = f"费用支出-{cat}"
    used_date = today - timedelta(days=random.randint(0, 60))
    reimb_id = random.randint(1, 20) if random.random() > 0.3 else "NULL"
    sql(
        f"INSERT INTO budget_usages (id, budget_id, reimbursement_id, amount, category, description, used_date, created_at, updated_at) "
        f"VALUES ({i}, {budget_id}, {reimb_id}, {amount}, {q(cat)}, {q(desc)}, {q(str(used_date))}, {q(str(now))}, {q(str(now))});"
    )
sql("")

# ── 5. 应付款（10 条） ──────────────────────────────────────

VENDORS = ["阿里云", "腾讯云", "华为云", "京东企业购", "得力办公", "中国电信", "中国移动", "顺丰速运", "前程无忧", "智联招聘"]
sql("-- 应付款")
for i in range(1, 11):
    payable_no = f"FIN-P-{i:04d}"
    vendor = VENDORS[i - 1]
    amount = round(random.uniform(5000, 50000), 2)
    due_date = today + timedelta(days=random.randint(-30, 60))
    if due_date < today:
        status = random.choice(["paid", "overdue"])
    else:
        status = random.choice(["pending", "pending", "paid"])
    desc = f"{vendor}服务费用"
    sql(
        f"INSERT INTO payables (id, payable_no, vendor, amount, due_date, status, description, created_at, updated_at) "
        f"VALUES ({i}, {q(payable_no)}, {q(vendor)}, {amount}, {q(str(due_date))}, {q(status)}, {q(desc)}, {q(str(now))}, {q(str(now))});"
    )
sql("")

# ── 6. 应收款（5 条） ───────────────────────────────────────

CUSTOMERS = ["客户A公司", "客户B集团", "客户C科技", "客户D传媒", "客户E咨询"]
sql("-- 应收款")
for i in range(1, 6):
    recv_no = f"FIN-AR-{i:04d}"
    customer = CUSTOMERS[i - 1]
    amount = round(random.uniform(10000, 100000), 2)
    due_date = today + timedelta(days=random.randint(-15, 45))
    if due_date < today:
        status = random.choice(["received", "overdue"])
    else:
        status = "pending"
    desc = f"{customer}项目款"
    sql(
        f"INSERT INTO receivables (id, receivable_no, customer, amount, due_date, status, description, created_at, updated_at) "
        f"VALUES ({i}, {q(recv_no)}, {q(customer)}, {amount}, {q(str(due_date))}, {q(status)}, {q(desc)}, {q(str(now))}, {q(str(now))});"
    )

sql("")
sql("COMMIT;")

output_path = "scripts/finance_seed.sql"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"已生成财务测试数据脚本: {output_path}")
print(f"  - 报销单: 20 条")
print(f"  - 报销明细: {min(item_id, 40)} 条")
print(f"  - 预算: {min(10, len(DEPT_IDS))} 条")
print(f"  - 预算使用: 15 条")
print(f"  - 应付款: 10 条")
print(f"  - 应收款: 5 条")
print(f"\n执行方式: sqlite3 data/mx_agent.db < {output_path}")
