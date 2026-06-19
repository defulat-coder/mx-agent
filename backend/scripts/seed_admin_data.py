"""生成行政管理测试数据 SQL 脚本 — 会议室、预订、办公用品、申领、快递、访客"""

import json
import random
from datetime import date, datetime, timedelta

random.seed(88)

lines: list[str] = []


def sql(s: str) -> None:
    lines.append(s)


def q(v: str) -> str:
    return f"'{v}'"


sql("-- 行政管理测试数据 —— 自动生成")
sql("-- 使用前请确保 meeting_rooms / room_bookings / office_supplies / supply_requests / expresses / visitors 表已创建")
sql("BEGIN;\n")

for t in ["visitors", "expresses", "supply_requests", "office_supplies", "room_bookings", "meeting_rooms"]:
    sql(f"DELETE FROM {t};")
sql("")

EMPLOYEE_IDS = list(range(1, 21))
now = datetime.now()
today = date.today()

# ── 1. 会议室（10 条） ──────────────────────────────────────

ROOMS = [
    ("朝阳厅", "3F", 20, "投影仪、白板、视频会议系统、麦克风"),
    ("望京厅", "3F", 16, "投影仪、白板、视频会议系统"),
    ("国贸厅", "5F", 12, "投影仪、白板、视频会议系统"),
    ("三里屯", "5F", 10, "投影仪、白板"),
    ("中关村", "7F", 8, "电视屏幕、白板"),
    ("西二旗", "7F", 8, "电视屏幕、白板"),
    ("上地厅", "9F", 6, "电视屏幕、白板"),
    ("亦庄厅", "9F", 6, "电视屏幕"),
    ("洽谈室A", "3F", 4, "白板"),
    ("洽谈室B", "5F", 4, "白板"),
]

sql("-- 会议室")
for i, (name, floor, cap, equip) in enumerate(ROOMS, 1):
    status = "maintenance" if i == 8 else "available"
    sql(
        f"INSERT INTO meeting_rooms (id, name, floor, capacity, equipment, status, created_at, updated_at) "
        f"VALUES ({i}, {q(name)}, {q(floor)}, {cap}, {q(equip)}, {q(status)}, {q(str(now))}, {q(str(now))});"
    )
sql("")

# ── 2. 会议室预订（30 条） ──────────────────────────────────

sql("-- 会议室预订")
MEETING_TITLES = [
    "周例会", "技术评审", "需求讨论", "项目复盘", "1v1 面谈", "客户演示",
    "培训分享", "头脑风暴", "面试", "全员大会", "产品评审", "设计评审",
    "Sprint 规划", "Code Review", "架构讨论",
]

for i in range(30):
    bid = i + 1
    room_id = random.randint(1, 10)
    emp_id = random.choice(EMPLOYEE_IDS)
    title = random.choice(MEETING_TITLES)

    day_offset = random.randint(-14, 7)
    book_date = today + timedelta(days=day_offset)
    hour = random.choice([9, 10, 11, 13, 14, 15, 16])
    minute = random.choice([0, 30])
    start = datetime(book_date.year, book_date.month, book_date.day, hour, minute)
    duration_slots = random.choice([1, 2, 3, 4])
    end = start + timedelta(minutes=30 * duration_slots)

    if day_offset < -3:
        status = random.choice(["completed", "completed", "cancelled"])
    elif day_offset < 0:
        status = "completed"
    else:
        status = random.choice(["active", "active", "active", "cancelled"])

    created_at = start - timedelta(days=random.randint(1, 5))
    sql(
        f"INSERT INTO room_bookings (id, room_id, employee_id, title, start_time, end_time, status, created_at, updated_at) "
        f"VALUES ({bid}, {room_id}, {emp_id}, {q(title)}, {q(start.strftime('%Y-%m-%d %H:%M:%S'))}, "
        f"{q(end.strftime('%Y-%m-%d %H:%M:%S'))}, {q(status)}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )
sql("")

# ── 3. 办公用品（15 条） ────────────────────────────────────

SUPPLIES = [
    ("A4 纸", "耗材", 200, "包"),
    ("签字笔（黑）", "文具", 500, "支"),
    ("签字笔（蓝）", "文具", 300, "支"),
    ("签字笔（红）", "文具", 100, "支"),
    ("笔记本", "文具", 150, "本"),
    ("便利贴", "文具", 200, "本"),
    ("文件夹", "文具", 100, "个"),
    ("订书机", "文具", 30, "个"),
    ("订书针", "耗材", 100, "盒"),
    ("白板笔", "耗材", 80, "支"),
    ("垃圾袋", "清洁", 500, "卷"),
    ("抽纸", "清洁", 300, "包"),
    ("洗手液", "清洁", 50, "瓶"),
    ("墨盒（黑）", "耗材", 20, "个"),
    ("USB-C 线", "耗材", 40, "条"),
]

sql("-- 办公用品")
for i, (name, cat, stock, unit) in enumerate(SUPPLIES, 1):
    sql(
        f"INSERT INTO office_supplies (id, name, category, stock, unit, created_at, updated_at) "
        f"VALUES ({i}, {q(name)}, {q(cat)}, {stock}, {q(unit)}, {q(str(now))}, {q(str(now))});"
    )
sql("")

# ── 4. 申领单（15 条） ─────────────────────────────────────

sql("-- 申领单")
SUPPLY_ITEMS_POOL = [
    [{"name": "A4 纸", "quantity": 2}, {"name": "签字笔（黑）", "quantity": 5}],
    [{"name": "笔记本", "quantity": 1}],
    [{"name": "便利贴", "quantity": 3}, {"name": "签字笔（蓝）", "quantity": 2}],
    [{"name": "文件夹", "quantity": 5}],
    [{"name": "白板笔", "quantity": 4}],
    [{"name": "订书机", "quantity": 1}, {"name": "订书针", "quantity": 2}],
    [{"name": "抽纸", "quantity": 5}],
    [{"name": "USB-C 线", "quantity": 1}],
    [{"name": "墨盒（黑）", "quantity": 2}],
    [{"name": "垃圾袋", "quantity": 3}, {"name": "洗手液", "quantity": 1}],
]

for i in range(15):
    rid = i + 1
    emp_id = random.choice(EMPLOYEE_IDS)
    items = json.dumps(random.choice(SUPPLY_ITEMS_POOL), ensure_ascii=False)
    r = random.random()
    if r < 0.4:
        status = "pending"
        approved_by = "NULL"
        remark = ""
    elif r < 0.8:
        status = "approved"
        approved_by = "9"
        remark = "已审批通过"
    else:
        status = "rejected"
        approved_by = "9"
        remark = "库存不足，请下月申领"

    created_at = now - timedelta(days=random.randint(0, 30))
    items_escaped = items.replace("'", "''")
    sql(
        f"INSERT INTO supply_requests (id, employee_id, items, status, approved_by, remark, created_at, updated_at) "
        f"VALUES ({rid}, {emp_id}, {q(items_escaped)}, {q(status)}, {approved_by}, {q(remark)}, "
        f"{q(created_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )
sql("")

# ── 5. 快递（15 条） ───────────────────────────────────────

COURIERS = ["顺丰", "中通", "圆通", "韵达", "京东", "EMS"]
sql("-- 快递")
for i in range(15):
    eid = i + 1
    tracking_no = f"SF{random.randint(100000000000, 999999999999)}" if i % 2 == 0 else f"ZT{random.randint(10000000000, 99999999999)}"
    etype = "receive" if i < 10 else "send"
    emp_id = random.choice(EMPLOYEE_IDS)
    courier = random.choice(COURIERS)

    r = random.random()
    if r < 0.4:
        status = "pending"
        received_at = "NULL"
    elif r < 0.8:
        status = "picked_up"
        received_at = q((now - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d %H:%M:%S"))
    else:
        status = "sent"
        received_at = "NULL"

    remark = "请尽快领取" if status == "pending" and etype == "receive" else ""
    created_at = now - timedelta(days=random.randint(0, 30))
    sql(
        f"INSERT INTO expresses (id, tracking_no, type, employee_id, courier, status, received_at, remark, created_at, updated_at) "
        f"VALUES ({eid}, {q(tracking_no)}, {q(etype)}, {emp_id}, {q(courier)}, {q(status)}, {received_at}, {q(remark)}, "
        f"{q(created_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )
sql("")

# ── 6. 访客（15 条） ───────────────────────────────────────

VISITOR_NAMES = ["王建国", "李明华", "刘思远", "陈志强", "张伟", "赵丽", "杨洁", "黄磊", "周涛", "吴芳",
                 "林小林", "马超", "孙学文", "朱凯", "何雨婷"]
COMPANIES = ["腾讯", "阿里巴巴", "字节跳动", "美团", "京东", "百度", "华为", "小米", "网易", "滴滴",
             "个人来访", "", "合作方A", "供应商B", "客户C"]
PURPOSES = ["商务拜访", "技术交流", "合同签署", "面试", "参观考察", "项目对接", "培训讲座", "审计检查"]

sql("-- 访客")
for i in range(15):
    vid = i + 1
    vname = VISITOR_NAMES[i]
    company = random.choice(COMPANIES)
    phone = f"138{random.randint(10000000, 99999999)}"
    host_id = random.choice(EMPLOYEE_IDS)
    vdate = today + timedelta(days=random.randint(-10, 10))
    vtime = random.choice(["09:00-10:00", "10:00-11:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"])
    purpose = random.choice(PURPOSES)

    r = random.random()
    if vdate < today:
        status = random.choice(["checked_out", "checked_out", "cancelled"])
    elif vdate == today:
        status = random.choice(["pending", "checked_in"])
    else:
        status = random.choice(["pending", "pending", "cancelled"])

    created_at = now - timedelta(days=max(0, (today - vdate).days + random.randint(1, 3)))
    sql(
        f"INSERT INTO visitors (id, visitor_name, company, phone, host_id, visit_date, visit_time, purpose, status, created_at, updated_at) "
        f"VALUES ({vid}, {q(vname)}, {q(company)}, {q(phone)}, {host_id}, {q(str(vdate))}, {q(vtime)}, {q(purpose)}, {q(status)}, "
        f"{q(created_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )

sql("")
sql("COMMIT;")

output_path = "scripts/admin_seed.sql"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"已生成行政测试数据脚本: {output_path}")
print(f"  - 会议室: 10 条")
print(f"  - 预订: 30 条")
print(f"  - 办公用品: 15 条")
print(f"  - 申领单: 15 条")
print(f"  - 快递: 15 条")
print(f"  - 访客: 15 条")
print(f"\n执行方式: sqlite3 data/mx_agent.db < {output_path}")
