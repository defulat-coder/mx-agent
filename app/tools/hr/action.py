"""HR 业务办理 Tools — 请假申请/加班登记/报销申请，收集信息后返回审批系统链接"""

import json
from urllib.parse import urlencode

from agno.run import RunContext

from app.tools.hr.utils import get_employee_id
from loguru import logger


_HR_BASE_URL = "https://hr.example.com"


async def apply_leave(
    run_context: RunContext,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str = "",
) -> str:
    """发起请假申请。收集请假类型、起止日期、原因后，返回审批系统链接。

    Args:
        leave_type: 假期类型（年假/调休/病假/事假/婚假/产假等）
        start_date: 开始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD
        reason: 请假原因
    """
    logger.info(
        "tool=apply_leave | leave_type={leave_type} start_date={start_date} end_date={end_date}",
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
    )
    employee_id = get_employee_id(run_context)
    params = urlencode({
        "employee_id": employee_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
    })
    url = f"{_HR_BASE_URL}/leave/apply?{params}"
    return json.dumps({
        "type": "redirect",
        "url": url,
        "message": f"已为您准备好{leave_type}申请（{start_date} 至 {end_date}），请点击链接前往审批系统提交。",
    }, ensure_ascii=False)


async def apply_overtime(
    run_context: RunContext,
    date: str,
    start_time: str,
    end_time: str,
    overtime_type: str = "工作日",
) -> str:
    """发起加班登记。收集加班日期、时段、类型后，返回审批系统链接。

    Args:
        date: 加班日期 YYYY-MM-DD
        start_time: 开始时间 HH:MM
        end_time: 结束时间 HH:MM
        overtime_type: 加班类型（工作日/周末/节假日）
    """
    logger.info(
        "tool=apply_overtime | date={date} start_time={start_time} end_time={end_time}",
        date=date,
        start_time=start_time,
        end_time=end_time,
    )
    employee_id = get_employee_id(run_context)
    params = urlencode({
        "employee_id": employee_id,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "type": overtime_type,
    })
    url = f"{_HR_BASE_URL}/overtime/apply?{params}"
    return json.dumps({
        "type": "redirect",
        "url": url,
        "message": f"已为您准备好加班登记（{date} {start_time}-{end_time}），请点击链接前往审批系统提交。",
    }, ensure_ascii=False)


async def apply_reimbursement(
    run_context: RunContext,
    reimbursement_type: str,
    amount: float,
    description: str = "",
) -> str:
    """发起报销申请。收集报销类型、金额、说明后，返回报销系统链接。

    Args:
        reimbursement_type: 报销类型（差旅/办公/通讯/其他）
        amount: 报销金额
        description: 费用说明
    """
    logger.info(
        "tool=apply_reimbursement | type={reimbursement_type} amount={amount}",
        reimbursement_type=reimbursement_type,
        amount=amount,
    )
    employee_id = get_employee_id(run_context)
    params = urlencode({
        "employee_id": employee_id,
        "type": reimbursement_type,
        "amount": amount,
        "description": description,
    })
    url = f"{_HR_BASE_URL}/reimbursement/apply?{params}"
    return json.dumps({
        "type": "redirect",
        "url": url,
        "message": f"已为您准备好{reimbursement_type}报销申请（金额 {amount} 元），请点击链接前往报销系统提交。",
    }, ensure_ascii=False)
