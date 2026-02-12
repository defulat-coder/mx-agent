"""生成 HR 测试数据 SQL 脚本"""

import random
from datetime import date, time, timedelta

random.seed(42)

lines: list[str] = []


def sql(s: str) -> None:
    lines.append(s)


def q(v: str) -> str:
    return f"'{v}'"


# ── 建表（如果用 alembic 已建则跳过） ─────────────────────────
sql("-- HR 测试数据 —— 自动生成，覆盖 10 张表")
sql("-- 使用前请确保表已通过 SQLAlchemy metadata.create_all 或 alembic 创建")
sql("BEGIN;\n")

# ── 清空旧数据 ──────────────────────────────────────────────
for t in [
    "employment_histories", "performance_reviews",
    "overtime_records", "leave_requests", "leave_balances",
    "attendance_records", "social_insurance_records", "salary_records",
    "employees", "departments",
]:
    sql(f"DELETE FROM {t};")
sql("")

# ── 1. departments ──────────────────────────────────────────
departments = [
    (1, "马喜集团", None),
    (2, "技术部", 1),
    (3, "产品部", 1),
    (4, "人力资源部", 1),
    (5, "财务部", 1),
    (6, "法务部", 1),
    (7, "后端组", 2),
    (8, "前端组", 2),
    (9, "AI 组", 2),
    (10, "测试组", 2),
]

sql("-- departments")
for did, name, pid in departments:
    parent = str(pid) if pid else "NULL"
    sql(
        f"INSERT INTO departments (id, name, parent_id, manager_id) "
        f"VALUES ({did}, {q(name)}, {parent}, NULL);"
    )
sql("")

# ── 2. employees ────────────────────────────────────────────
employees_raw = [
    # id, name, no,     dept_id, position,       level,  hire_date,     status,    email,                phone
    (1,  "张三",  "XM0001", 7,  "高级后端工程师",    "P7",  "2021-03-15", "在职",  "zhangsan@ximalaya.com",  "13800000001"),
    (2,  "李四",  "XM0002", 7,  "后端工程师",       "P5",  "2022-07-01", "在职",  "lisi@ximalaya.com",      "13800000002"),
    (3,  "王五",  "XM0003", 8,  "前端工程师",       "P6",  "2021-09-01", "在职",  "wangwu@ximalaya.com",    "13800000003"),
    (4,  "赵六",  "XM0004", 9,  "算法工程师",       "P7",  "2020-06-15", "在职",  "zhaoliu@ximalaya.com",   "13800000004"),
    (5,  "钱七",  "XM0005", 3,  "产品经理",         "P6",  "2022-01-10", "在职",  "qianqi@ximalaya.com",    "13800000005"),
    (6,  "孙八",  "XM0006", 4,  "HRBP",            "P6",  "2021-04-20", "在职",  "sunba@ximalaya.com",     "13800000006"),
    (7,  "周九",  "XM0007", 5,  "财务主管",         "P7",  "2019-08-01", "在职",  "zhoujiu@ximalaya.com",   "13800000007"),
    (8,  "吴十",  "XM0008", 6,  "法务顾问",         "P6",  "2023-02-15", "在职",  "wushi@ximalaya.com",     "13800000008"),
    (9,  "郑晓明", "XM0009", 2,  "技术总监",        "P9",  "2018-03-01", "在职",  "zhengxm@ximalaya.com",   "13800000009"),
    (10, "陈小红", "XM0010", 7,  "后端工程师",       "P5",  "2024-06-01", "试用期", "chenxh@ximalaya.com",    "13800000010"),
    (11, "林志强", "XM0011", 8,  "前端工程师",       "P5",  "2023-09-01", "在职",  "linzq@ximalaya.com",     "13800000011"),
    (12, "黄丽丽", "XM0012", 9,  "NLP 工程师",      "P6",  "2022-11-01", "在职",  "huangll@ximalaya.com",   "13800000012"),
    (13, "刘伟",   "XM0013", 10, "测试工程师",       "P5",  "2023-04-01", "在职",  "liuwei@ximalaya.com",    "13800000013"),
    (14, "杨芳",   "XM0014", 3,  "产品经理",        "P5",  "2024-01-15", "在职",  "yangfang@ximalaya.com",  "13800000014"),
    (15, "何涛",   "XM0015", 4,  "招聘专员",        "P4",  "2024-03-01", "在职",  "hetao@ximalaya.com",     "13800000015"),
    (16, "马骏",   "XM0016", 7,  "后端工程师",       "P6",  "2021-11-01", "在职",  "majun@ximalaya.com",     "13800000016"),
    (17, "许晴",   "XM0017", 5,  "会计",            "P5",  "2022-05-01", "在职",  "xuqing@ximalaya.com",    "13800000017"),
    (18, "高峰",   "XM0018", 10, "测试主管",        "P7",  "2020-01-15", "在职",  "gaofeng@ximalaya.com",   "13800000018"),
    (19, "罗敏",   "XM0019", 9,  "算法实习生",      "P3",  "2025-09-01", "试用期", "luomin@ximalaya.com",    "13800000019"),
    (20, "谢强",   "XM0020", 8,  "前端组长",        "P7",  "2020-05-01", "在职",  "xieqiang@ximalaya.com",  "13800000020"),
]

sql("-- employees")
for eid, name, no, did, pos, lv, hd, st, email, phone in employees_raw:
    sql(
        f"INSERT INTO employees (id, name, employee_no, department_id, position, level, hire_date, status, email, phone) "
        f"VALUES ({eid}, {q(name)}, {q(no)}, {did}, {q(pos)}, {q(lv)}, {q(hd)}, {q(st)}, {q(email)}, {q(phone)});"
    )
sql("")

# 回填部门 manager_id
manager_map = {2: 9, 3: 5, 4: 6, 5: 7, 6: 8, 7: 1, 8: 20, 9: 4, 10: 18}
sql("-- 回填部门负责人")
for dept_id, mgr_id in manager_map.items():
    sql(f"UPDATE departments SET manager_id = {mgr_id} WHERE id = {dept_id};")
sql("")

# ── 3. salary_records（6 个月 × 20 人 = 120 条） ────────────
sql("-- salary_records (2025-09 ~ 2026-02)")
# 各职级基本工资档
base_by_level = {
    "P3": 6000, "P4": 10000, "P5": 15000, "P6": 22000,
    "P7": 30000, "P9": 50000,
}
months = ["2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02"]

for eid, name, _, _, _, lv, _, st, _, _ in employees_raw:
    base = base_by_level.get(lv, 15000)
    for ym in months:
        bonus = round(random.uniform(0, base * 0.3), 2)
        allowance = round(random.choice([800, 1000, 1200, 1500, 2000]), 2)
        deduction = round(random.choice([0, 0, 0, 100, 200, 300]), 2)
        si = round(base * 0.105, 2)  # 养老8%+医疗2%+失业0.5%
        hf = round(base * 0.07, 2)   # 公积金7%
        gross = base + bonus + allowance - deduction
        tax = round(max(0, (gross - si - hf - 5000) * 0.1 - 210), 2)
        net = round(gross - si - hf - tax, 2)
        sql(
            f"INSERT INTO salary_records (employee_id, year_month, base_salary, bonus, allowance, deduction, social_insurance, housing_fund, tax, net_salary) "
            f"VALUES ({eid}, {q(ym)}, {base}, {bonus}, {allowance}, {deduction}, {si}, {hf}, {tax}, {net});"
        )
sql("")

# ── 4. social_insurance_records（6 个月 × 20 人 = 120 条） ──
sql("-- social_insurance_records (2025-09 ~ 2026-02)")
for eid, name, _, _, _, lv, _, st, _, _ in employees_raw:
    base = base_by_level.get(lv, 15000)
    for ym in months:
        pension_p = round(base * 0.08, 2)
        medical_p = round(base * 0.02, 2)
        unemp_p = round(base * 0.005, 2)
        hf_p = round(base * 0.07, 2)
        pension_c = round(base * 0.16, 2)
        medical_c = round(base * 0.095, 2)
        unemp_c = round(base * 0.005, 2)
        injury_c = round(base * 0.004, 2)
        maternity_c = round(base * 0.008, 2)
        hf_c = round(base * 0.07, 2)
        sql(
            f"INSERT INTO social_insurance_records (employee_id, year_month, "
            f"pension, medical, unemployment, housing_fund, "
            f"pension_company, medical_company, unemployment_company, injury_company, maternity_company, housing_fund_company) "
            f"VALUES ({eid}, {q(ym)}, "
            f"{pension_p}, {medical_p}, {unemp_p}, {hf_p}, "
            f"{pension_c}, {medical_c}, {unemp_c}, {injury_c}, {maternity_c}, {hf_c});"
        )
sql("")

# ── 5. attendance_records（工作日 × 20 人，3 个月） ──────────
sql("-- attendance_records (2025-12 ~ 2026-02)")


def workdays_in_range(start: date, end: date) -> list[date]:
    """返回工作日列表（排除周末）"""
    days = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


att_months = [
    (date(2025, 12, 1), date(2025, 12, 31)),
    (date(2026, 1, 1), date(2026, 1, 31)),
    (date(2026, 2, 1), date(2026, 2, 11)),  # 到今天
]

normal_in = time(9, 0)
normal_out = time(18, 0)

for start, end in att_months:
    wdays = workdays_in_range(start, end)
    for eid, *_ in employees_raw:
        for d in wdays:
            r = random.random()
            if r < 0.85:
                ci = time(8, random.randint(40, 59))
                co = time(18, random.randint(0, 30))
                status = "正常"
                remark = ""
            elif r < 0.92:
                ci = time(9, random.randint(5, 30))
                co = time(18, random.randint(0, 20))
                status = "迟到"
                remark = random.choice(["地铁延误", "堵车", ""])
            elif r < 0.96:
                ci = time(8, random.randint(50, 59))
                co = time(17, random.randint(0, 45))
                status = "早退"
                remark = random.choice(["身体不适", "家中急事", ""])
            elif r < 0.98:
                ci = time(8, random.randint(50, 59))
                co = None
                status = "缺卡"
                remark = "忘记打卡"
            else:
                ci = time(9, random.randint(0, 30))
                co = time(18, random.randint(0, 30))
                status = "外勤"
                remark = "客户拜访"

            ci_str = q(ci.strftime("%H:%M:%S"))
            co_str = q(co.strftime("%H:%M:%S")) if co else "NULL"
            sql(
                f"INSERT INTO attendance_records (employee_id, date, check_in, check_out, status, remark) "
                f"VALUES ({eid}, {q(d.isoformat())}, {ci_str}, {co_str}, {q(status)}, {q(remark)});"
            )
sql("")

# ── 6. leave_balances（2026 年，每人 4 种假期） ──────────────
sql("-- leave_balances (2026)")
for eid, name, _, _, _, lv, hd, st, _, _ in employees_raw:
    # 年假天数按工龄
    hire = date.fromisoformat(hd)
    years = (date(2026, 1, 1) - hire).days / 365
    annual = 5 if years < 2 else (10 if years < 5 else 15)
    annual_used = round(random.uniform(0, min(annual, 3)), 1)

    for lt, total, used in [
        ("年假", annual, annual_used),
        ("调休", round(random.uniform(1, 5), 1), round(random.uniform(0, 2), 1)),
        ("病假", 10, round(random.uniform(0, 2), 1)),
        ("事假", 5, round(random.uniform(0, 1), 1)),
    ]:
        remaining = round(total - used, 1)
        sql(
            f"INSERT INTO leave_balances (employee_id, year, leave_type, total_days, used_days, remaining_days) "
            f"VALUES ({eid}, 2026, {q(lt)}, {total}, {used}, {remaining});"
        )
sql("")

# ── 7. leave_requests ───────────────────────────────────────
sql("-- leave_requests")
leave_data = [
    (1,  "年假",  "2025-12-25", "2025-12-26", 2.0, "圣诞节休息",     "已通过"),
    (1,  "年假",  "2026-02-16", "2026-02-17", 2.0, "个人事务",       "待审批"),
    (2,  "事假",  "2025-10-08", "2025-10-08", 1.0, "搬家",           "已通过"),
    (2,  "病假",  "2026-01-13", "2026-01-14", 2.0, "感冒发烧",       "已通过"),
    (3,  "年假",  "2025-12-30", "2026-01-02", 3.0, "元旦假期",       "已通过"),
    (4,  "调休",  "2026-01-20", "2026-01-20", 1.0, "调休",           "已通过"),
    (5,  "年假",  "2026-01-27", "2026-01-31", 5.0, "春节假期",       "已通过"),
    (5,  "病假",  "2026-02-05", "2026-02-05", 1.0, "肠胃不适",       "已通过"),
    (6,  "年假",  "2025-11-11", "2025-11-12", 2.0, "双十一",         "已通过"),
    (7,  "事假",  "2025-12-15", "2025-12-15", 1.0, "家中有事",       "已通过"),
    (8,  "年假",  "2026-02-09", "2026-02-10", 2.0, "陪家人",         "已通过"),
    (9,  "调休",  "2025-10-20", "2025-10-20", 1.0, "调休",           "已通过"),
    (10, "病假",  "2026-01-06", "2026-01-07", 2.0, "感冒",           "已通过"),
    (11, "年假",  "2025-12-23", "2025-12-24", 2.0, "回老家",         "已通过"),
    (12, "事假",  "2026-02-03", "2026-02-03", 1.0, "办证件",         "已通过"),
    (13, "年假",  "2025-11-25", "2025-11-28", 4.0, "旅游",           "已通过"),
    (14, "调休",  "2026-01-15", "2026-01-15", 1.0, "调休",           "已通过"),
    (15, "病假",  "2025-12-10", "2025-12-11", 2.0, "牙疼看医生",     "已通过"),
    (16, "年假",  "2026-02-16", "2026-02-20", 5.0, "春节后休息",     "待审批"),
    (17, "事假",  "2026-01-22", "2026-01-22", 1.0, "处理私事",       "已通过"),
    (18, "年假",  "2025-10-01", "2025-10-07", 5.0, "国庆旅游",       "已通过"),
    (19, "病假",  "2026-02-06", "2026-02-07", 2.0, "身体不适",       "已通过"),
    (20, "年假",  "2025-12-29", "2025-12-31", 3.0, "跨年休假",       "已通过"),
    (20, "调休",  "2026-02-11", "2026-02-11", 1.0, "调休",           "待审批"),
    (1,  "调休",  "2025-11-05", "2025-11-05", 1.0, "补休",           "已通过"),
    (3,  "病假",  "2025-10-15", "2025-10-15", 1.0, "头疼",           "已通过"),
    (4,  "年假",  "2025-09-22", "2025-09-26", 5.0, "中秋国庆",       "已通过"),
    (6,  "事假",  "2026-01-08", "2026-01-08", 1.0, "去银行",         "已通过"),
    (9,  "年假",  "2025-12-22", "2025-12-26", 5.0, "年终休假",       "已通过"),
    (12, "年假",  "2026-01-27", "2026-01-31", 5.0, "春节假期",       "已通过"),
]

for eid, lt, sd, ed, days, reason, status in leave_data:
    sql(
        f"INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, days, reason, status) "
        f"VALUES ({eid}, {q(lt)}, {q(sd)}, {q(ed)}, {days}, {q(reason)}, {q(status)});"
    )
sql("")

# ── 8. overtime_records ─────────────────────────────────────
sql("-- overtime_records")
overtime_data = [
    (1,  "2025-12-05", "19:00", "22:00", 3.0, "工作日", "已通过"),
    (1,  "2025-12-20", "10:00", "17:00", 7.0, "周末",   "已通过"),
    (1,  "2026-01-10", "19:00", "21:30", 2.5, "工作日", "已通过"),
    (1,  "2026-02-05", "19:00", "22:00", 3.0, "工作日", "已通过"),
    (2,  "2025-12-12", "19:00", "21:00", 2.0, "工作日", "已通过"),
    (2,  "2026-01-18", "09:00", "18:00", 9.0, "周末",   "已通过"),
    (3,  "2025-12-15", "19:00", "22:30", 3.5, "工作日", "已通过"),
    (4,  "2025-12-06", "10:00", "18:00", 8.0, "周末",   "已通过"),
    (4,  "2026-01-04", "10:00", "16:00", 6.0, "周末",   "已通过"),
    (4,  "2026-02-08", "10:00", "15:00", 5.0, "周末",   "已通过"),
    (5,  "2026-01-15", "19:00", "21:00", 2.0, "工作日", "已通过"),
    (9,  "2025-12-13", "10:00", "20:00", 10.0, "周末",  "已通过"),
    (9,  "2025-12-14", "10:00", "18:00", 8.0, "周末",   "已通过"),
    (9,  "2026-01-11", "10:00", "18:00", 8.0, "周末",   "已通过"),
    (9,  "2026-02-01", "10:00", "14:00", 4.0, "节假日", "已通过"),
    (10, "2026-01-08", "19:00", "22:00", 3.0, "工作日", "已通过"),
    (11, "2025-12-22", "19:00", "21:00", 2.0, "工作日", "已通过"),
    (12, "2026-01-05", "10:00", "16:00", 6.0, "周末",   "已通过"),
    (13, "2025-12-28", "10:00", "14:00", 4.0, "周末",   "已通过"),
    (16, "2025-12-10", "19:00", "23:00", 4.0, "工作日", "已通过"),
    (16, "2026-01-20", "19:00", "22:00", 3.0, "工作日", "已通过"),
    (16, "2026-02-07", "10:00", "18:00", 8.0, "周末",   "待审批"),
    (18, "2025-12-07", "10:00", "17:00", 7.0, "周末",   "已通过"),
    (18, "2026-01-25", "10:00", "16:00", 6.0, "周末",   "已通过"),
    (20, "2025-12-19", "19:00", "22:30", 3.5, "工作日", "已通过"),
    (20, "2026-01-12", "09:00", "18:00", 9.0, "周末",   "已通过"),
    (20, "2026-02-09", "10:00", "15:00", 5.0, "周末",   "待审批"),
]

for eid, d, st, et, hrs, tp, status in overtime_data:
    sql(
        f"INSERT INTO overtime_records (employee_id, date, start_time, end_time, hours, type, status) "
        f"VALUES ({eid}, {q(d)}, {q(st + ':00')}, {q(et + ':00')}, {hrs}, {q(tp)}, {q(status)});"
    )
sql("")

# ── 9. performance_reviews（每人 2~4 期考评） ────────────────
sql("-- performance_reviews")
ratings = ["A", "B+", "B", "B", "B+", "C"]
reviewers_by_dept = {
    7: "张三", 8: "谢强", 9: "赵六", 10: "高峰",
    2: "郑晓明", 3: "钱七", 4: "孙八", 5: "周九", 6: "吴十",
}
perf_data: list[tuple[int, int, str, str, int, str, str]] = []

for eid, name, _, did, _, lv, hd, st, _, _ in employees_raw:
    hire = date.fromisoformat(hd)
    reviewer = reviewers_by_dept.get(did, "郑晓明")
    # 不给自己写考评
    if name == reviewer:
        reviewer = "郑晓明" if name != "郑晓明" else "张三"
    start_year = max(hire.year, 2023)
    for yr in range(start_year, 2026):
        for half in ["上半年", "下半年"]:
            if yr == hire.year and half == "上半年" and hire.month > 6:
                continue
            rating = random.choice(ratings)
            score_map = {"A": (90, 100), "B+": (80, 89), "B": (70, 79), "C": (60, 69), "D": (40, 59)}
            lo, hi = score_map[rating]
            score = random.randint(lo, hi)
            comments = {
                "A": "表现优异，超额完成目标",
                "B+": "表现良好，较好完成工作",
                "B": "表现合格，完成既定目标",
                "C": "有待提高，部分目标未达成",
                "D": "表现不佳，需要改进",
            }
            perf_data.append((eid, yr, half, rating, score, reviewer, comments[rating]))

for eid, yr, half, rating, score, reviewer, comment in perf_data:
    sql(
        f"INSERT INTO performance_reviews (employee_id, year, half, rating, score, reviewer, comment) "
        f"VALUES ({eid}, {yr}, {q(half)}, {q(rating)}, {score}, {q(reviewer)}, {q(comment)});"
    )
sql("")

# ── 10. employment_histories（每人至少入职记录，部分有晋升/调岗） ─
sql("-- employment_histories")
dept_name_map = {d[0]: d[1] for d in departments}
hist_data: list[tuple[int, str, str | None, str, str, str, str, str]] = []

for eid, name, _, did, pos, lv, hd, st, _, _ in employees_raw:
    dept_name = dept_name_map.get(did, "")
    hire = date.fromisoformat(hd)

    if eid == 1:
        hist_data.append((eid, "2021-03-15", "2021-09-14", "后端组", "后端工程师", "P5", "入职", ""))
        hist_data.append((eid, "2021-09-15", "2023-03-14", "后端组", "后端工程师", "P5", "转正", ""))
        hist_data.append((eid, "2023-03-15", None, "后端组", "高级后端工程师", "P7", "晋升", "年度晋升"))
    elif eid == 9:
        hist_data.append((eid, "2018-03-01", "2018-08-31", "技术部", "高级工程师", "P7", "入职", ""))
        hist_data.append((eid, "2018-09-01", "2020-12-31", "技术部", "技术经理", "P8", "晋升", ""))
        hist_data.append((eid, "2021-01-01", None, "技术部", "技术总监", "P9", "晋升", "升任技术总监"))
    elif eid == 4:
        hist_data.append((eid, "2020-06-15", "2020-12-14", "AI 组", "算法工程师", "P5", "入职", ""))
        hist_data.append((eid, "2020-12-15", "2022-06-14", "AI 组", "算法工程师", "P5", "转正", ""))
        hist_data.append((eid, "2022-06-15", None, "AI 组", "算法工程师", "P7", "晋升", ""))
    elif eid == 20:
        hist_data.append((eid, "2020-05-01", "2020-10-31", "前端组", "前端工程师", "P5", "入职", ""))
        hist_data.append((eid, "2020-11-01", "2022-04-30", "前端组", "前端工程师", "P5", "转正", ""))
        hist_data.append((eid, "2022-05-01", None, "前端组", "前端组长", "P7", "晋升", "升任前端组长"))
    elif eid == 16:
        hist_data.append((eid, "2021-11-01", "2022-04-30", "后端组", "后端工程师", "P5", "入职", ""))
        hist_data.append((eid, "2022-05-01", "2024-05-31", "后端组", "后端工程师", "P5", "转正", ""))
        hist_data.append((eid, "2024-06-01", None, "后端组", "后端工程师", "P6", "晋升", ""))
    elif st == "试用期":
        hist_data.append((eid, hd, None, dept_name, pos, lv, "入职", "试用期"))
    else:
        trial_end = (hire + timedelta(days=180)).isoformat()
        hist_data.append((eid, hd, trial_end, dept_name, pos, lv, "入职", ""))
        hist_data.append((eid, trial_end, None, dept_name, pos, lv, "转正", ""))

for eid, sd, ed, dept, pos, lv, ct, remark in hist_data:
    ed_val = q(ed) if ed else "NULL"
    sql(
        f"INSERT INTO employment_histories (employee_id, start_date, end_date, department, position, level, change_type, remark) "
        f"VALUES ({eid}, {q(sd)}, {ed_val}, {q(dept)}, {q(pos)}, {q(lv)}, {q(ct)}, {q(remark)});"
    )
sql("")

sql("\nCOMMIT;")

# ── 输出 ────────────────────────────────────────────────────
output = "\n".join(lines)
with open("scripts/seed.sql", "w", encoding="utf-8") as f:
    f.write(output)

total_att = sum(
    len(workdays_in_range(s, e)) * len(employees_raw)
    for s, e in att_months
)
print(f"已生成 scripts/seed.sql")
print(f"  departments:              {len(departments)}")
print(f"  employees:                {len(employees_raw)}")
print(f"  salary_records:           {len(employees_raw) * len(months)}")
print(f"  social_insurance_records: {len(employees_raw) * len(months)}")
print(f"  attendance_records:       ~{total_att}")
print(f"  leave_balances:           {len(employees_raw) * 4}")
print(f"  leave_requests:           {len(leave_data)}")
print(f"  overtime_records:         {len(overtime_data)}")
print(f"  performance_reviews:      {len(perf_data)}")
print(f"  employment_histories:     {len(hist_data)}")
