"""生成 IT 运维测试数据 SQL 脚本 — 设备资产、工单、设备流转记录"""

import random
from datetime import date, datetime, timedelta

random.seed(42)

lines: list[str] = []


def sql(s: str) -> None:
    lines.append(s)


def q(v: str) -> str:
    return f"'{v}'"


sql("-- IT 运维测试数据 —— 自动生成")
sql("-- 使用前请确保 it_assets / it_tickets / it_asset_history 表已创建")
sql("BEGIN;\n")

# 清空旧数据
for t in ["it_asset_history", "it_tickets", "it_assets"]:
    sql(f"DELETE FROM {t};")
sql("")

# 员工 ID 范围（与 HR 种子数据一致，共 20 人，id 1~20）
EMPLOYEE_IDS = list(range(1, 21))
# 部门 ID：2=技术部, 3=产品部, 4=人力资源部, 5=财务部, 6=法务部, 7=后端组, 8=前端组, 9=AI组, 10=测试组
# 员工-部门映射（简化版）
EMP_DEPT = {
    1: 7, 2: 7, 3: 8, 4: 9, 5: 3, 6: 4, 7: 5, 8: 6, 9: 2, 10: 7,
    11: 8, 12: 9, 13: 10, 14: 3, 15: 4, 16: 7, 17: 5, 18: 10, 19: 9, 20: 8,
}

now = datetime.now()

# ── 1. IT 资产（~30 条） ──────────────────────────────────────

ASSET_TYPES = ["laptop", "desktop", "monitor", "peripheral"]
BRANDS_BY_TYPE = {
    "laptop": [("Apple", "MacBook Pro 14"), ("Apple", "MacBook Air 13"), ("Lenovo", "ThinkPad X1 Carbon"), ("Lenovo", "ThinkPad E14"), ("Dell", "XPS 15")],
    "desktop": [("Dell", "OptiPlex 7090"), ("Lenovo", "ThinkCentre M70"), ("HP", "ProDesk 400")],
    "monitor": [("Dell", "U2723QE 27\""), ("LG", "27UL850 27\""), ("BenQ", "PD2705Q 27\""), ("AOC", "U2490VXE 24\"")],
    "peripheral": [("Logitech", "MX Keys + MX Master 3"), ("Apple", "Magic Keyboard + Trackpad"), ("Logitech", "C920 摄像头"), ("Jabra", "Evolve2 75 耳机")],
}

sql("-- IT 资产")
assets = []
asset_id = 0
assigned_employees: list[int] = []

for i in range(30):
    asset_id = i + 1
    atype = random.choice(ASSET_TYPES) if i >= 4 else ASSET_TYPES[i]  # 确保前 4 条覆盖各类型
    brand, model = random.choice(BRANDS_BY_TYPE[atype])
    purchase_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 700))
    warranty_expire = purchase_date + timedelta(days=365 * 3)

    # 状态分布：60% in_use, 20% idle, 10% maintenance, 10% scrapped
    r = random.random()
    if r < 0.6 and len(assigned_employees) < 20:
        status = "in_use"
        available = [e for e in EMPLOYEE_IDS if e not in assigned_employees]
        if available:
            emp_id = random.choice(available)
            assigned_employees.append(emp_id)
        else:
            status = "idle"
            emp_id = None
    elif r < 0.8:
        status = "idle"
        emp_id = None
    elif r < 0.9:
        status = "maintenance"
        emp_id = None
    else:
        status = "scrapped"
        emp_id = None

    emp_val = str(emp_id) if emp_id else "NULL"
    asset_no = f"IT-A-{asset_id:04d}"
    assets.append((asset_id, asset_no, atype, status, emp_id))

    sql(
        f"INSERT INTO it_assets (id, asset_no, type, brand, model_name, status, employee_id, purchase_date, warranty_expire, created_at, updated_at) "
        f"VALUES ({asset_id}, {q(asset_no)}, {q(atype)}, {q(brand)}, {q(model)}, {q(status)}, {emp_val}, "
        f"{q(str(purchase_date))}, {q(str(warranty_expire))}, {q(str(now))}, {q(str(now))});"
    )
sql("")

# ── 2. IT 工单（~60 条） ─────────────────────────────────────

TICKET_TYPES = ["repair", "password_reset", "software_install", "permission", "other"]
TICKET_STATUSES = ["open", "in_progress", "resolved", "closed"]
PRIORITIES = ["low", "medium", "high", "urgent"]

TICKET_TITLES = {
    "repair": ["笔记本无法开机", "显示器闪屏", "键盘按键失灵", "电池充不进电", "电脑运行卡顿", "USB 接口故障", "触控板不灵敏", "风扇噪音大"],
    "password_reset": ["邮箱密码忘记", "AD 账号被锁定", "VPN 密码重置", "系统登录密码过期"],
    "software_install": ["申请安装 Figma", "申请安装 Docker Desktop", "申请安装 Postman", "申请安装 VS Code 插件", "申请安装 Office 365"],
    "permission": ["申请 GitLab 仓库权限", "申请共享文件夹访问权限", "申请 Jira 管理权限", "申请 VPN 远程访问权限"],
    "other": ["会议室音视频设备故障", "网络打印机无法连接", "WiFi 信号弱", "工位网口不通"],
}

RESOLUTIONS = [
    "已更换硬件，问题解决", "已重装驱动，恢复正常", "已重置密码，请使用新密码登录",
    "已安装软件并配置完成", "已开通权限", "已清理系统垃圾，性能恢复",
    "已更换设备", "已修复网络连接", "已更新固件", "问题无法复现，持续观察",
]

sql("-- IT 工单")
for i in range(60):
    tid = i + 1
    ticket_no = f"IT-T-{tid:04d}"
    ttype = random.choice(TICKET_TYPES) if i >= 5 else TICKET_TYPES[i]
    title = random.choice(TICKET_TITLES[ttype])
    description = f"详细描述：{title}，影响正常办公"
    priority = random.choice(PRIORITIES)
    submitter_id = random.choice(EMPLOYEE_IDS)

    # 状态分布：20% open, 20% in_progress, 40% resolved, 20% closed
    r = random.random()
    if r < 0.2:
        status = "open"
        handler_id = None
        resolution = ""
        resolved_at = None
    elif r < 0.4:
        status = "in_progress"
        handler_id = 9  # 郑晓明作为 IT 管理员
        resolution = ""
        resolved_at = None
    elif r < 0.8:
        status = "resolved"
        handler_id = 9
        resolution = random.choice(RESOLUTIONS)
        created_offset = random.randint(1, 90)
        resolved_at = now - timedelta(days=created_offset) + timedelta(hours=random.randint(2, 48))
    else:
        status = "closed"
        handler_id = 9
        resolution = random.choice(RESOLUTIONS)
        created_offset = random.randint(30, 90)
        resolved_at = now - timedelta(days=created_offset) + timedelta(hours=random.randint(2, 48))

    # 工单创建时间：近 3 个月内随机
    created_at = now - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))

    handler_val = str(handler_id) if handler_id else "NULL"
    resolved_val = q(resolved_at.strftime("%Y-%m-%d %H:%M:%S")) if resolved_at else "NULL"

    sql(
        f"INSERT INTO it_tickets (id, ticket_no, type, title, description, status, priority, submitter_id, handler_id, resolution, resolved_at, created_at, updated_at) "
        f"VALUES ({tid}, {q(ticket_no)}, {q(ttype)}, {q(title)}, {q(description)}, {q(status)}, {q(priority)}, "
        f"{submitter_id}, {handler_val}, {q(resolution)}, {resolved_val}, "
        f"{q(created_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(created_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )
sql("")

# ── 3. 设备流转记录（~15 条） ─────────────────────────────────

sql("-- 设备流转记录")
for i in range(15):
    hid = i + 1
    # 从已分配的设备中选取
    assigned_assets = [(aid, eid) for aid, _, _, st, eid in assets if st == "in_use" and eid]
    if not assigned_assets:
        break
    asset_id_pick, emp_id_pick = random.choice(assigned_assets)

    if i < 10:
        # 分配记录
        action = "assign"
        from_emp = "NULL"
        to_emp = str(emp_id_pick)
        remark = "新员工入职设备分配"
    else:
        # 回收记录
        action = "reclaim"
        from_emp = str(emp_id_pick)
        to_emp = "NULL"
        remark = "员工离职设备回收"

    operated_at = now - timedelta(days=random.randint(10, 180))

    sql(
        f"INSERT INTO it_asset_history (id, asset_id, action, from_employee_id, to_employee_id, operated_by, remark, created_at, updated_at) "
        f"VALUES ({hid}, {asset_id_pick}, {q(action)}, {from_emp}, {to_emp}, 9, {q(remark)}, "
        f"{q(operated_at.strftime('%Y-%m-%d %H:%M:%S'))}, {q(operated_at.strftime('%Y-%m-%d %H:%M:%S'))});"
    )

sql("")
sql("COMMIT;")

# 输出到文件
output_path = "scripts/it_seed.sql"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"已生成 IT 测试数据脚本: {output_path}")
print(f"  - IT 资产: 30 条")
print(f"  - IT 工单: 60 条")
print(f"  - 设备流转记录: 15 条")
print(f"\n执行方式: sqlite3 data/mx_agent.db < {output_path}")
