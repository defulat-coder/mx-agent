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
sql("-- HR 测试数据 —— 自动生成，覆盖 14 张表")
sql("-- 使用前请确保表已通过 SQLAlchemy metadata.create_all 或 alembic 创建")
sql("BEGIN;\n")

# ── 清空旧数据 ──────────────────────────────────────────────
for t in [
    "certificates", "project_experiences", "educations", "skills",
    "development_plans", "talent_reviews", "trainings",
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
    (1,  "张三",  "MX0001", 7,  "高级后端工程师",    "P7",  "2021-03-15", "在职",  "zhangsan@maxi.com",  "13800000001"),
    (2,  "李四",  "MX0002", 7,  "后端工程师",       "P5",  "2022-07-01", "在职",  "lisi@maxi.com",      "13800000002"),
    (3,  "王五",  "MX0003", 8,  "前端工程师",       "P6",  "2021-09-01", "在职",  "wangwu@maxi.com",    "13800000003"),
    (4,  "赵六",  "MX0004", 9,  "算法工程师",       "P7",  "2020-06-15", "在职",  "zhaoliu@maxi.com",   "13800000004"),
    (5,  "钱七",  "MX0005", 3,  "产品经理",         "P6",  "2022-01-10", "在职",  "qianqi@maxi.com",    "13800000005"),
    (6,  "孙八",  "MX0006", 4,  "HRBP",            "P6",  "2021-04-20", "在职",  "sunba@maxi.com",     "13800000006"),
    (7,  "周九",  "MX0007", 5,  "财务主管",         "P7",  "2019-08-01", "在职",  "zhoujiu@maxi.com",   "13800000007"),
    (8,  "吴十",  "MX0008", 6,  "法务顾问",         "P6",  "2023-02-15", "在职",  "wushi@maxi.com",     "13800000008"),
    (9,  "郑晓明", "MX0009", 2,  "技术总监",        "P9",  "2018-03-01", "在职",  "zhengxm@maxi.com",   "13800000009"),
    (10, "陈小红", "MX0010", 7,  "后端工程师",       "P5",  "2024-06-01", "试用期", "chenxh@maxi.com",    "13800000010"),
    (11, "林志强", "MX0011", 8,  "前端工程师",       "P5",  "2023-09-01", "在职",  "linzq@maxi.com",     "13800000011"),
    (12, "黄丽丽", "MX0012", 9,  "NLP 工程师",      "P6",  "2022-11-01", "在职",  "huangll@maxi.com",   "13800000012"),
    (13, "刘伟",   "MX0013", 10, "测试工程师",       "P5",  "2023-04-01", "在职",  "liuwei@maxi.com",    "13800000013"),
    (14, "杨芳",   "MX0014", 3,  "产品经理",        "P5",  "2024-01-15", "在职",  "yangfang@maxi.com",  "13800000014"),
    (15, "何涛",   "MX0015", 4,  "招聘专员",        "P4",  "2024-03-01", "在职",  "hetao@maxi.com",     "13800000015"),
    (16, "马骏",   "MX0016", 7,  "后端工程师",       "P6",  "2021-11-01", "在职",  "majun@maxi.com",     "13800000016"),
    (17, "许晴",   "MX0017", 5,  "会计",            "P5",  "2022-05-01", "在职",  "xuqing@maxi.com",    "13800000017"),
    (18, "高峰",   "MX0018", 10, "测试主管",        "P7",  "2020-01-15", "在职",  "gaofeng@maxi.com",   "13800000018"),
    (19, "罗敏",   "MX0019", 9,  "算法实习生",      "P3",  "2025-09-01", "试用期", "luomin@maxi.com",    "13800000019"),
    (20, "谢强",   "MX0020", 8,  "前端组长",        "P7",  "2020-05-01", "在职",  "xieqiang@maxi.com",  "13800000020"),
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

# ── 11. trainings（培训记录/计划） ─────────────────────────────
sql("-- trainings")

training_courses = [
    # (course_name, category, hours, provider, has_exam)
    ("Python 高级编程", "专业技能", 16, "内训-张三", True),
    ("微服务架构实践", "专业技能", 24, "极客时间", True),
    ("React 前端开发", "专业技能", 20, "内训-谢强", True),
    ("大模型应用开发", "专业技能", 32, "智谱AI学院", True),
    ("测试自动化框架", "专业技能", 16, "内训-高峰", True),
    ("产品需求分析", "专业技能", 12, "产品学院", False),
    ("沟通与协作", "通用素质", 8, "内训-孙八", False),
    ("时间管理", "通用素质", 4, "得到APP", False),
    ("职业规划与发展", "通用素质", 6, "内训-孙八", False),
    ("高效演讲技巧", "通用素质", 8, "外训-演讲力", False),
    ("团队管理基础", "管理能力", 16, "混沌学园", True),
    ("OKR 目标管理", "管理能力", 8, "内训-郑晓明", False),
    ("技术团队领导力", "管理能力", 12, "外训-领导力学院", False),
    ("信息安全意识", "合规必修", 4, "内训-安全组", True),
    ("数据隐私保护", "合规必修", 4, "内训-法务部", True),
    ("反舞弊合规培训", "合规必修", 2, "内训-法务部", True),
    ("消防安全培训", "合规必修", 2, "行政部", False),
]

training_statuses = ["已完成", "已完成", "已完成", "进行中", "待开始", "未通过"]
training_records: list[tuple] = []

for eid, name, _, did, pos, lv, hd, st, _, _ in employees_raw:
    # 每人 3-6 条培训记录
    n_courses = random.randint(3, 6)
    selected = random.sample(training_courses, min(n_courses, len(training_courses)))
    for course_name, category, hours, provider, has_exam in selected:
        status = random.choice(training_statuses)
        score = None
        completed_dt = None
        deadline_dt = None
        # 指派人：合规必修由 HR 指派，其他随机
        assigned = "孙八" if category == "合规必修" else ("" if random.random() > 0.4 else reviewers_by_dept.get(did, "郑晓明"))

        if status == "已完成":
            completed_dt = date(2025, random.randint(1, 12), random.randint(1, 28)).isoformat()
            deadline_dt = completed_dt
            if has_exam:
                score = random.randint(60, 100)
        elif status == "未通过":
            completed_dt = date(2025, random.randint(6, 12), random.randint(1, 28)).isoformat()
            deadline_dt = completed_dt
            if has_exam:
                score = random.randint(30, 59)
        elif status == "进行中":
            deadline_dt = date(2026, random.randint(3, 6), random.randint(1, 28)).isoformat()
        else:  # 待开始
            deadline_dt = date(2026, random.randint(4, 9), random.randint(1, 28)).isoformat()

        training_records.append((eid, course_name, category, hours, score, status, provider, assigned, deadline_dt, completed_dt))

for eid, cn, cat, hrs, sc, st, prov, ab, dl, cd in training_records:
    sc_val = str(sc) if sc is not None else "NULL"
    dl_val = q(dl) if dl else "NULL"
    cd_val = q(cd) if cd else "NULL"
    sql(
        f"INSERT INTO trainings (employee_id, course_name, category, hours, score, status, provider, assigned_by, deadline, completed_date) "
        f"VALUES ({eid}, {q(cn)}, {q(cat)}, {hrs}, {sc_val}, {q(st)}, {q(prov)}, {q(ab)}, {dl_val}, {cd_val});"
    )
sql("")

# ── 12. talent_reviews（人才盘点九宫格） ──────────────────────
sql("-- talent_reviews")

# 绩效评级 → 绩效维度映射
perf_rating_to_dim = {"A": "高", "B+": "高", "B": "中", "C": "低", "D": "低"}

# 九宫格位置映射
nine_grid_map = {
    ("高", "高"): "明星", ("高", "中"): "骨干", ("高", "低"): "专家",
    ("中", "高"): "潜力股", ("中", "中"): "中坚", ("中", "低"): "守成者",
    ("低", "高"): "待雕琢", ("低", "中"): "待观察", ("低", "低"): "淘汰区",
}

# 收集每人最近一次绩效评级
latest_perf: dict[int, str] = {}
for eid, yr, half, rating, score, reviewer, comment in perf_data:
    key = (yr, 0 if half == "上半年" else 1)
    if eid not in latest_perf or key > latest_perf.get(f"{eid}_key", (0, 0)):  # type: ignore
        latest_perf[eid] = rating
        latest_perf[f"{eid}_key"] = key  # type: ignore

talent_review_records: list[tuple] = []
for eid, name, _, did, pos, lv, hd, st, _, _ in employees_raw:
    hire = date.fromisoformat(hd)
    if hire.year > 2025:
        continue  # 太新的员工不参与盘点

    rating = latest_perf.get(eid, "B")
    performance = perf_rating_to_dim.get(rating, "中")
    # 潜力根据职级和随机因素
    if lv in ("P7", "P8", "P9"):
        potential = random.choice(["高", "高", "中"])
    elif lv in ("P5", "P6"):
        potential = random.choice(["高", "中", "中", "低"])
    else:
        potential = random.choice(["中", "低", "低"])

    nine_grid = nine_grid_map[(performance, potential)]

    # 标签
    if nine_grid == "明星":
        tag = random.choice(["高潜", "继任候选"])
    elif nine_grid in ("骨干", "潜力股"):
        tag = random.choice(["高潜", "关键岗位", "普通"])
    elif nine_grid == "专家":
        tag = "关键岗位"
    else:
        tag = "普通"

    reviewer = reviewers_by_dept.get(did, "郑晓明")
    if name == reviewer:
        reviewer = "郑晓明" if name != "郑晓明" else "张三"

    comments_map = {
        "明星": "综合表现优秀，建议重点培养",
        "骨干": "业务能力扎实，是团队核心",
        "潜力股": "有较大成长空间，建议加强历练",
        "中坚": "表现稳定，完成本职工作",
        "专家": "专业能力突出，建议拓展管理能力",
        "守成者": "完成基本工作，建议激发活力",
        "待雕琢": "潜力不错但绩效待提升，需辅导",
        "待观察": "表现一般，需要关注",
        "淘汰区": "绩效和潜力均需改善，考虑转岗",
    }

    for review_year in [2024, 2025]:
        talent_review_records.append((
            eid, review_year, performance, potential, nine_grid, tag,
            reviewer, comments_map.get(nine_grid, ""),
        ))

for eid, ry, perf, pot, ng, tag, rev, cmt in talent_review_records:
    sql(
        f"INSERT INTO talent_reviews (employee_id, review_year, performance, potential, nine_grid_pos, tag, reviewer, comment) "
        f"VALUES ({eid}, {ry}, {q(perf)}, {q(pot)}, {q(ng)}, {q(tag)}, {q(rev)}, {q(cmt)});"
    )
sql("")

# ── 13. development_plans（个人发展计划 IDP） ─────────────────
sql("-- development_plans")

idp_goals = [
    ("掌握 Kubernetes 容器编排", "技术深耕", "完成 CKA 认证课程；在项目中实践 K8s 部署"),
    ("系统学习分布式架构", "技术深耕", "阅读《DDIA》；完成微服务改造项目一个"),
    ("提升大模型应用能力", "技术深耕", "完成 RAG 项目实战；掌握 Agent 框架"),
    ("转型技术管理", "管理转型", "参加管理培训；带领小团队完成一个项目"),
    ("从后端拓展全栈能力", "跨领域拓展", "学习 React/Vue；独立完成一个前端项目"),
    ("掌握产品数据分析", "跨领域拓展", "学习 SQL + 数据分析；完成数据看板项目"),
    ("考取 PMP 证书", "专业认证", "报名 PMP 培训班；每周刷题 5 小时"),
    ("考取 CPA 证书", "专业认证", "参加 CPA 辅导班；完成模考 3 次"),
    ("提升英语商务沟通", "跨领域拓展", "报名商务英语课程；每周英语角 1 次"),
    ("深入学习 NLP 技术", "技术深耕", "阅读 3 篇顶会论文；复现一个开源模型"),
]

idp_statuses = ["进行中", "进行中", "进行中", "已完成", "已放弃"]
idp_records: list[tuple] = []

for eid, name, _, did, pos, lv, hd, st, _, _ in employees_raw:
    hire = date.fromisoformat(hd)
    if hire.year > 2025:
        continue
    # 每人 1-2 个 IDP
    n_plans = random.randint(1, 2)
    selected_goals = random.sample(idp_goals, n_plans)
    for goal, category, actions in selected_goals:
        status = random.choice(idp_statuses)
        if status == "已完成":
            progress = 100
        elif status == "已放弃":
            progress = random.randint(10, 40)
        else:
            progress = random.randint(20, 85)
        dl = date(2026, random.randint(6, 12), random.randint(1, 28))
        idp_records.append((eid, 2026, goal, category, actions, status, progress, dl.isoformat()))

for eid, py, goal, cat, acts, st, prog, dl in idp_records:
    sql(
        f"INSERT INTO development_plans (employee_id, plan_year, goal, category, actions, status, progress, deadline) "
        f"VALUES ({eid}, {py}, {q(goal)}, {q(cat)}, {q(acts)}, {q(st)}, {prog}, {q(dl)});"
    )
sql("")

# ── 14. skills（技能标签） ─────────────────────────────────────
sql("-- skills")

skill_pool = [
    # (name, category, levels)
    ("Python", "技术", ["中级", "高级", "专家"]),
    ("Java", "技术", ["初级", "中级", "高级"]),
    ("Go", "技术", ["初级", "中级"]),
    ("JavaScript", "技术", ["中级", "高级"]),
    ("TypeScript", "技术", ["中级", "高级"]),
    ("React", "技术", ["中级", "高级"]),
    ("Vue", "技术", ["初级", "中级"]),
    ("SQL", "技术", ["中级", "高级"]),
    ("Docker", "技术", ["中级", "高级"]),
    ("Kubernetes", "技术", ["初级", "中级"]),
    ("机器学习", "技术", ["中级", "高级", "专家"]),
    ("NLP", "技术", ["中级", "高级"]),
    ("大模型应用", "技术", ["初级", "中级", "高级"]),
    ("测试自动化", "技术", ["中级", "高级"]),
    ("性能测试", "技术", ["初级", "中级"]),
    ("项目管理", "管理", ["初级", "中级", "高级"]),
    ("团队管理", "管理", ["初级", "中级"]),
    ("OKR", "管理", ["中级", "高级"]),
    ("需求分析", "业务", ["中级", "高级"]),
    ("数据分析", "业务", ["初级", "中级", "高级"]),
    ("财务分析", "业务", ["中级", "高级"]),
    ("法律合规", "业务", ["中级", "高级"]),
    ("沟通表达", "通用", ["中级", "高级"]),
    ("演讲汇报", "通用", ["初级", "中级"]),
    ("英语", "通用", ["初级", "中级", "高级"]),
]

# 每个员工根据岗位分配 3-6 个技能
emp_skill_map: dict[int, list[str]] = {
    1:  ["Python", "SQL", "Docker", "Kubernetes", "项目管理", "沟通表达"],
    2:  ["Python", "SQL", "Docker"],
    3:  ["JavaScript", "TypeScript", "React", "Vue", "沟通表达"],
    4:  ["Python", "机器学习", "NLP", "大模型应用", "Docker"],
    5:  ["需求分析", "数据分析", "项目管理", "沟通表达", "演讲汇报"],
    6:  ["沟通表达", "项目管理", "数据分析", "英语"],
    7:  ["财务分析", "SQL", "数据分析", "英语"],
    8:  ["法律合规", "沟通表达", "英语"],
    9:  ["Python", "项目管理", "团队管理", "OKR", "Docker", "Kubernetes"],
    10: ["Python", "SQL"],
    11: ["JavaScript", "React", "TypeScript"],
    12: ["Python", "NLP", "机器学习", "大模型应用"],
    13: ["测试自动化", "性能测试", "Python", "SQL"],
    14: ["需求分析", "数据分析", "演讲汇报"],
    15: ["沟通表达", "英语"],
    16: ["Python", "Go", "SQL", "Docker", "Kubernetes"],
    17: ["财务分析", "SQL", "数据分析"],
    18: ["测试自动化", "性能测试", "Python", "团队管理", "项目管理"],
    19: ["Python", "机器学习"],
    20: ["JavaScript", "TypeScript", "React", "Vue", "团队管理", "项目管理"],
}

skill_name_to_info = {s[0]: (s[1], s[2]) for s in skill_pool}
skill_records: list[tuple] = []

for eid, skill_names in emp_skill_map.items():
    for sname in skill_names:
        cat, levels = skill_name_to_info[sname]
        level = random.choice(levels)
        source = random.choice(["自评", "自评", "上级评", "认证"])
        verified = source in ("上级评", "认证") or random.random() > 0.5
        skill_records.append((eid, sname, cat, level, source, verified))

for eid, sname, cat, level, source, verified in skill_records:
    sql(
        f"INSERT INTO skills (employee_id, name, category, level, source, verified) "
        f"VALUES ({eid}, {q(sname)}, {q(cat)}, {q(level)}, {q(source)}, {1 if verified else 0});"
    )
sql("")

# ── 15. educations（教育背景） ────────────────────────────────
sql("-- educations")

education_data = [
    (1,  "本科", "计算机科学与技术", "华中科技大学", 2018),
    (1,  "硕士", "软件工程", "华中科技大学", 2021),
    (2,  "本科", "软件工程", "武汉大学", 2022),
    (3,  "本科", "数字媒体技术", "浙江大学", 2019),
    (4,  "本科", "人工智能", "北京大学", 2017),
    (4,  "硕士", "计算机科学", "北京大学", 2020),
    (5,  "本科", "信息管理", "复旦大学", 2019),
    (5,  "MBA", "工商管理", "中欧商学院", 2022),
    (6,  "本科", "人力资源管理", "中国人民大学", 2018),
    (7,  "本科", "会计学", "上海财经大学", 2016),
    (8,  "本科", "法学", "中国政法大学", 2020),
    (8,  "硕士", "国际商法", "中国政法大学", 2023),
    (9,  "本科", "计算机科学与技术", "清华大学", 2014),
    (9,  "硕士", "计算机科学", "清华大学", 2017),
    (10, "本科", "软件工程", "电子科技大学", 2024),
    (11, "本科", "计算机科学与技术", "南京大学", 2023),
    (12, "本科", "计算机科学与技术", "中山大学", 2019),
    (12, "硕士", "自然语言处理", "中山大学", 2022),
    (13, "本科", "软件测试", "西安电子科技大学", 2023),
    (14, "本科", "工业设计", "同济大学", 2021),
    (15, "大专", "人力资源管理", "深圳职业技术学院", 2022),
    (16, "本科", "计算机科学与技术", "厦门大学", 2019),
    (17, "本科", "会计学", "中南财经政法大学", 2022),
    (18, "本科", "软件工程", "哈尔滨工业大学", 2016),
    (18, "硕士", "软件工程", "哈尔滨工业大学", 2019),
    (19, "本科", "人工智能", "上海交通大学", 2025),
    (20, "本科", "计算机科学与技术", "东南大学", 2017),
]

for eid, degree, major, school, grad_year in education_data:
    sql(
        f"INSERT INTO educations (employee_id, degree, major, school, graduation_year) "
        f"VALUES ({eid}, {q(degree)}, {q(major)}, {q(school)}, {grad_year});"
    )
sql("")

# ── 16. project_experiences（项目经历） ────────────────────────
sql("-- project_experiences")

project_data = [
    (1,  "智能客服系统", "核心成员", "2022-03-01", "2022-09-30", "基于 LLM 的智能客服系统开发", "系统上线后客服效率提升 40%"),
    (1,  "微服务架构迁移", "负责人", "2023-06-01", "2024-01-31", "将单体应用拆分为微服务架构", "完成 12 个服务拆分，零故障上线"),
    (1,  "HR 智能助手", "负责人", "2025-06-01", None, "马喜智能助手 HR 模块开发", "完成核心功能上线"),
    (2,  "HR 智能助手", "核心成员", "2025-08-01", None, "HR 助手后端 API 开发", "独立完成考勤和薪资模块"),
    (3,  "企业门户改版", "核心成员", "2022-01-01", "2022-06-30", "公司门户网站前端重构", "页面加载速度提升 60%"),
    (3,  "数据可视化平台", "负责人", "2023-09-01", "2024-03-31", "搭建公司内部数据看板系统", "覆盖 5 个业务部门的数据需求"),
    (4,  "智能推荐引擎", "负责人", "2021-01-01", "2021-12-31", "基于协同过滤的推荐系统", "推荐点击率提升 25%"),
    (4,  "大模型微调平台", "核心成员", "2024-01-01", "2024-09-30", "企业级大模型微调与部署平台", "支持 3 个业务场景的模型微调"),
    (4,  "HR 智能助手", "核心成员", "2025-06-01", None, "HR 助手 AI Agent 模块开发", "设计并实现多 Agent 协作架构"),
    (5,  "产品体验优化", "负责人", "2022-06-01", "2022-12-31", "用户体验全面优化项目", "NPS 评分从 30 提升到 55"),
    (5,  "HR 智能助手", "参与者", "2025-06-01", None, "HR 助手产品设计", "完成产品需求文档和交互设计"),
    (9,  "技术中台建设", "负责人", "2019-06-01", "2020-12-31", "搭建公司技术中台", "统一技术栈，研发效率提升 30%"),
    (9,  "HR 智能助手", "负责人", "2025-03-01", None, "马喜智能助手整体架构和推进", "从 0 到 1 搭建 AI Agent 平台"),
    (12, "情感分析系统", "核心成员", "2023-03-01", "2023-12-31", "中文情感分析模型训练与部署", "模型准确率达到 92%"),
    (12, "HR 智能助手", "参与者", "2025-09-01", None, "HR 助手 NLP 能力支持", "优化意图识别准确率"),
    (16, "支付系统重构", "核心成员", "2022-06-01", "2023-03-31", "支付系统从 PHP 迁移到 Go", "系统 QPS 提升 5 倍"),
    (16, "HR 智能助手", "核心成员", "2025-07-01", None, "HR 助手后端开发", "完成权限和审批模块"),
    (18, "自动化测试平台", "负责人", "2021-06-01", "2022-06-30", "搭建持续测试平台", "测试覆盖率从 40% 提升到 85%"),
    (18, "HR 智能助手", "参与者", "2025-08-01", None, "HR 助手质量保障", "搭建自动化回归测试"),
    (20, "组件库建设", "负责人", "2021-06-01", "2022-03-31", "统一前端组件库开发", "组件复用率达到 70%"),
    (20, "数据可视化平台", "核心成员", "2023-09-01", "2024-03-31", "数据看板前端开发", "实现 20+ 可视化图表组件"),
]

for eid, pname, role, sd, ed, desc, ach in project_data:
    ed_val = q(ed) if ed else "NULL"
    sql(
        f"INSERT INTO project_experiences (employee_id, project_name, role, start_date, end_date, description, achievement) "
        f"VALUES ({eid}, {q(pname)}, {q(role)}, {q(sd)}, {ed_val}, {q(desc)}, {q(ach)});"
    )
sql("")

# ── 17. certificates（证书认证） ──────────────────────────────
sql("-- certificates")

certificate_data = [
    (1,  "AWS Solutions Architect", "Amazon", "2023-06-15", "2026-06-15", "专业技术"),
    (1,  "PMP", "PMI", "2024-03-01", "2027-03-01", "管理"),
    (4,  "TensorFlow Developer", "Google", "2022-09-01", "2025-09-01", "专业技术"),
    (5,  "PMP", "PMI", "2023-11-01", "2026-11-01", "管理"),
    (5,  "NPDP", "PDMA", "2024-08-01", None, "管理"),
    (7,  "CPA", "中国注册会计师协会", "2020-01-15", None, "专业技术"),
    (8,  "法律职业资格证", "司法部", "2021-03-01", None, "专业技术"),
    (9,  "CKA", "CNCF", "2021-08-01", "2024-08-01", "专业技术"),
    (9,  "PMP", "PMI", "2020-05-01", "2023-05-01", "管理"),
    (12, "华为 HCIA-AI", "华为", "2023-05-01", "2026-05-01", "专业技术"),
    (16, "CKA", "CNCF", "2024-01-15", "2027-01-15", "专业技术"),
    (17, "初级会计师", "财政部", "2022-11-01", None, "专业技术"),
    (18, "ISTQB 高级测试经理", "ISTQB", "2022-04-01", None, "专业技术"),
    (20, "Google UX Design", "Google", "2023-07-01", None, "专业技术"),
    (6,  "人力资源管理师（二级）", "人社部", "2021-09-01", None, "专业技术"),
    (6,  "SHRM-CP", "SHRM", "2023-12-01", "2026-12-01", "管理"),
]

for eid, cname, issuer, issue_d, expiry_d, cat in certificate_data:
    exp_val = q(expiry_d) if expiry_d else "NULL"
    sql(
        f"INSERT INTO certificates (employee_id, name, issuer, issue_date, expiry_date, category) "
        f"VALUES ({eid}, {q(cname)}, {q(issuer)}, {q(issue_d)}, {exp_val}, {q(cat)});"
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
print(f"  trainings:                {len(training_records)}")
print(f"  talent_reviews:           {len(talent_review_records)}")
print(f"  development_plans:        {len(idp_records)}")
print(f"  skills:                   {len(skill_records)}")
print(f"  educations:               {len(education_data)}")
print(f"  project_experiences:      {len(project_data)}")
print(f"  certificates:             {len(certificate_data)}")
