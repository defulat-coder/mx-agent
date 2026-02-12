"""HR 相关响应 Schema — 查询结果的 Pydantic 模型"""

from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, Field


class EmployeeInfoResponse(BaseModel):
    """员工基本信息"""

    employee_id: int = Field(description="员工 ID")
    name: str = Field(description="姓名")
    employee_no: str = Field(description="工号")
    department: str | None = Field(default=None, description="部门名称")
    position: str = Field(description="职位")
    level: str = Field(description="职级")
    hire_date: date | None = Field(default=None, description="入职日期")
    status: str = Field(description="在职状态")


class SalaryRecordResponse(BaseModel):
    """薪资明细"""

    year_month: str = Field(description="年月，格式 YYYY-MM")
    base_salary: Decimal = Field(description="基本工资")
    bonus: Decimal = Field(description="奖金")
    allowance: Decimal = Field(description="津贴")
    deduction: Decimal = Field(description="扣款")
    social_insurance: Decimal = Field(description="社保个人缴纳")
    housing_fund: Decimal = Field(description="公积金个人缴纳")
    tax: Decimal = Field(description="个人所得税")
    net_salary: Decimal = Field(description="实发工资")


class SocialInsuranceResponse(BaseModel):
    """五险一金缴纳明细"""

    year_month: str = Field(description="年月，格式 YYYY-MM")
    pension: Decimal = Field(description="养老保险（个人）")
    medical: Decimal = Field(description="医疗保险（个人）")
    unemployment: Decimal = Field(description="失业保险（个人）")
    housing_fund: Decimal = Field(description="公积金（个人）")
    pension_company: Decimal = Field(description="养老保险（公司）")
    medical_company: Decimal = Field(description="医疗保险（公司）")
    unemployment_company: Decimal = Field(description="失业保险（公司）")
    injury_company: Decimal = Field(description="工伤保险（公司）")
    maternity_company: Decimal = Field(description="生育保险（公司）")
    housing_fund_company: Decimal = Field(description="公积金（公司）")


class AttendanceResponse(BaseModel):
    """考勤记录"""

    date: date = Field(description="考勤日期")
    check_in: time | None = Field(default=None, description="签到时间")
    check_out: time | None = Field(default=None, description="签退时间")
    status: str = Field(description="考勤状态")
    remark: str = Field(description="备注")


class LeaveBalanceResponse(BaseModel):
    """假期余额"""

    leave_type: str = Field(description="假期类型")
    total_days: Decimal = Field(description="总天数")
    used_days: Decimal = Field(description="已用天数")
    remaining_days: Decimal = Field(description="剩余天数")


class LeaveRequestResponse(BaseModel):
    """请假记录"""

    leave_type: str = Field(description="假期类型")
    start_date: date = Field(description="开始日期")
    end_date: date = Field(description="结束日期")
    days: Decimal = Field(description="请假天数")
    reason: str = Field(description="请假事由")
    status: str = Field(description="审批状态")


class OvertimeRecordResponse(BaseModel):
    """加班记录"""

    date: date = Field(description="加班日期")
    start_time: time = Field(description="开始时间")
    end_time: time = Field(description="结束时间")
    hours: Decimal = Field(description="加班时长（小时）")
    type: str = Field(description="加班类型")
    status: str = Field(description="审批状态")


class ActionResponse(BaseModel):
    """业务办理 Action 响应"""

    type: str = Field(default="redirect", description="动作类型")
    url: str = Field(description="跳转目标 URL")
    message: str = Field(description="提示信息")


# ── 主管相关 Schema ──────────────────────────────────────────


class TeamMemberResponse(BaseModel):
    """团队成员信息"""

    employee_id: int = Field(description="员工 ID")
    name: str = Field(description="姓名")
    employee_no: str = Field(description="工号")
    department: str | None = Field(default=None, description="部门名称")
    position: str = Field(description="职位")
    level: str = Field(description="职级")
    status: str = Field(description="在职状态")


class TeamAttendanceResponse(BaseModel):
    """团队考勤记录（含员工姓名）"""

    employee_id: int = Field(description="员工 ID")
    employee_name: str = Field(description="员工姓名")
    date: date = Field(description="考勤日期")
    check_in: time | None = Field(default=None, description="签到时间")
    check_out: time | None = Field(default=None, description="签退时间")
    status: str = Field(description="考勤状态")
    remark: str = Field(description="备注")


class TeamLeaveRequestResponse(BaseModel):
    """团队请假记录（含员工姓名和 request_id）"""

    request_id: int = Field(description="请假申请 ID")
    employee_id: int = Field(description="员工 ID")
    employee_name: str = Field(description="员工姓名")
    leave_type: str = Field(description="假期类型")
    start_date: date = Field(description="开始日期")
    end_date: date = Field(description="结束日期")
    days: Decimal = Field(description="请假天数")
    reason: str = Field(description="请假事由")
    status: str = Field(description="审批状态")


class TeamLeaveBalanceResponse(BaseModel):
    """团队假期余额（含员工姓名）"""

    employee_id: int = Field(description="员工 ID")
    employee_name: str = Field(description="员工姓名")
    leave_type: str = Field(description="假期类型")
    total_days: Decimal = Field(description="总天数")
    used_days: Decimal = Field(description="已用天数")
    remaining_days: Decimal = Field(description="剩余天数")


class TeamOvertimeRecordResponse(BaseModel):
    """团队加班记录（含员工姓名和 record_id）"""

    record_id: int = Field(description="加班记录 ID")
    employee_id: int = Field(description="员工 ID")
    employee_name: str = Field(description="员工姓名")
    date: date = Field(description="加班日期")
    start_time: time = Field(description="开始时间")
    end_time: time = Field(description="结束时间")
    hours: Decimal = Field(description="加班时长（小时）")
    type: str = Field(description="加班类型")
    status: str = Field(description="审批状态")


class ApprovalResponse(BaseModel):
    """审批结果"""

    success: bool = Field(description="是否审批成功")
    request_id: int | None = Field(default=None, description="关联的申请 ID")
    action: str | None = Field(default=None, description="审批动作")
    message: str = Field(description="审批结果说明")


class PerformanceReviewResponse(BaseModel):
    """绩效考评记录"""

    year: int = Field(description="考评年份")
    half: str = Field(description="上半年/下半年")
    rating: str = Field(description="评级")
    score: int = Field(description="评分")
    reviewer: str = Field(description="评审人")
    comment: str = Field(description="评语")


class EmploymentHistoryResponse(BaseModel):
    """在职履历记录"""

    start_date: date = Field(description="开始日期")
    end_date: date | None = Field(default=None, description="结束日期")
    department: str = Field(description="部门名称")
    position: str = Field(description="职位")
    level: str = Field(description="职级")
    change_type: str = Field(description="变动类型")
    remark: str = Field(description="备注")


class EmployeeProfileResponse(BaseModel):
    """员工档案（基本信息 + 绩效 + 履历）"""

    info: EmployeeInfoResponse = Field(description="员工基本信息")
    performance_reviews: list[PerformanceReviewResponse] = Field(description="绩效考评记录列表")
    employment_histories: list[EmploymentHistoryResponse] = Field(description="在职履历列表")
