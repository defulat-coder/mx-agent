"""人才发展查询 Tools — 全公司数据查询 + 分析报表（只读）"""

from agno.run import RunContext

from app.core.database import async_session_factory
from app.services import hr as hr_service
from app.tools.hr.utils import get_talent_dev_id


# ── 个人数据查询 ─────────────────────────────────────────────


async def td_get_employee_profile(
    run_context: RunContext,
    employee_id: int,
) -> str:
    """查询任意员工的完整档案（基本信息 + 绩效 + 履历 + 薪资 + 社保）"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        profile = await hr_service.get_any_employee_profile(session, employee_id)
        return profile.model_dump_json()


async def td_get_employee_training(
    run_context: RunContext,
    employee_id: int,
    status: str | None = None,
) -> str:
    """查询任意员工的培训记录。可传 status 过滤（待开始/进行中/已完成/未通过）。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_training(session, employee_id, status)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_get_employee_talent_review(
    run_context: RunContext,
    employee_id: int,
    review_year: int | None = None,
) -> str:
    """查询任意员工的人才盘点（九宫格）历史。可指定盘点年度。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_talent_review(session, employee_id, review_year)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_get_employee_idp(
    run_context: RunContext,
    employee_id: int,
    plan_year: int | None = None,
) -> str:
    """查询任意员工的个人发展计划 (IDP)。可指定计划年度。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_idp(session, employee_id, plan_year)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_get_employee_performance(
    run_context: RunContext,
    employee_id: int,
) -> str:
    """查询任意员工的绩效考评详情（含评分和评语）"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_performance_detail(session, employee_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_get_employee_history(
    run_context: RunContext,
    employee_id: int,
) -> str:
    """查询任意员工的岗位变动履历（入职/转正/晋升/调岗等）"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_employment_history(session, employee_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_get_employee_attendance(
    run_context: RunContext,
    employee_id: int,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """查询任意员工的考勤记录。日期格式 YYYY-MM-DD。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_attendance_records(
            session, employee_id, start_date, end_date,
        )
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


# ── 分析报表 ─────────────────────────────────────────────────


async def td_training_summary(
    run_context: RunContext,
    year: int | None = None,
) -> str:
    """各部门培训统计（完成率、人均学时、合规必修完成率）"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_training_summary(session, year)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_nine_grid_distribution(
    run_context: RunContext,
    review_year: int | None = None,
    department_id: int | None = None,
) -> str:
    """九宫格分布统计（含高潜人才清单）。可按部门过滤。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await hr_service.get_nine_grid_distribution(session, review_year, department_id)
        return result.model_dump_json()


async def td_performance_distribution(
    run_context: RunContext,
    year: int | None = None,
    half: str | None = None,
) -> str:
    """各部门绩效评级分布（A/B+/B/C/D 占比）。可指定年度和半年度。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_performance_distribution(session, year, half)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_turnover_analysis(run_context: RunContext) -> str:
    """各部门人员流动分析（离职率、转正率、平均司龄）"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_turnover_analysis(session)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_promotion_stats(
    run_context: RunContext,
    year: int | None = None,
) -> str:
    """各部门晋升/调岗统计。默认统计上一年。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_promotion_stats(session, year)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_idp_summary(
    run_context: RunContext,
    plan_year: int | None = None,
) -> str:
    """IDP 汇总统计（完成率、各类目标分布、平均进度）"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        result = await hr_service.get_idp_summary(session, plan_year)
        return result.model_dump_json()


# ── 人才发现新增数据查询 ───────────────────────────────────────


async def td_get_employee_skills(
    run_context: RunContext,
    employee_id: int,
    category: str | None = None,
) -> str:
    """查询任意员工的技能标签列表。可按分类过滤（技术/管理/业务/通用）。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_skills(session, employee_id, category)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_get_employee_education(
    run_context: RunContext,
    employee_id: int,
) -> str:
    """查询任意员工的教育背景（学历、专业、院校）"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_education(session, employee_id)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_get_employee_projects(
    run_context: RunContext,
    employee_id: int,
    role: str | None = None,
) -> str:
    """查询任意员工的项目参与经历。可按角色过滤（负责人/核心成员/参与者）。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_projects(session, employee_id, role)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_get_employee_certificates(
    run_context: RunContext,
    employee_id: int,
    category: str | None = None,
) -> str:
    """查询任意员工的证书认证。可按分类过滤（专业技术/管理/语言/行业）。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        records = await hr_service.get_employee_certificates(session, employee_id, category)
        return "[" + ",".join(r.model_dump_json() for r in records) + "]"


async def td_search_employee(
    run_context: RunContext,
    name: str,
) -> str:
    """根据姓名搜索员工，返回匹配的员工 ID、姓名、工号、部门、岗位、职级。支持模糊匹配。"""
    try:
        get_talent_dev_id(run_context)
    except ValueError as e:
        return str(e)
    async with async_session_factory() as session:
        import json
        results = await hr_service.search_employee_by_name(session, name)
        return json.dumps(results, ensure_ascii=False)
