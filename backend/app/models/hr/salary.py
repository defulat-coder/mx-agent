"""薪资记录模型"""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SalaryRecord(Base):
    """月度薪资明细。

    Attributes:
        employee_id: 员工 ID
        year_month: 月份，格式 YYYY-MM
        base_salary: 基本工资
        bonus: 奖金
        allowance: 补贴
        deduction: 扣款
        social_insurance: 社保个人缴纳
        housing_fund: 公积金个人缴纳
        tax: 个税
        net_salary: 实发工资
    """

    __tablename__ = "salary_records"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    year_month: Mapped[str] = mapped_column(String(7), index=True, comment="薪资月份，格式YYYY-MM")
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="基本工资")
    bonus: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="奖金")
    allowance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="补贴")
    deduction: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="扣款")
    social_insurance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="社保个人缴纳")
    housing_fund: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="公积金个人缴纳")
    tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="个税")
    net_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="实发工资")
