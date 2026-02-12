"""社保公积金记录模型"""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SocialInsuranceRecord(Base):
    """五险一金缴纳明细。

    Attributes:
        employee_id: 员工 ID
        year_month: 月份，格式 YYYY-MM
        pension / pension_company: 养老保险（个人/公司）
        medical / medical_company: 医疗保险
        unemployment / unemployment_company: 失业保险
        injury_company: 工伤保险（仅公司缴纳）
        maternity_company: 生育保险（仅公司缴纳）
        housing_fund / housing_fund_company: 住房公积金
    """

    __tablename__ = "social_insurance_records"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    year_month: Mapped[str] = mapped_column(String(7), index=True, comment="缴纳月份，格式YYYY-MM")

    # 个人缴纳
    pension: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="养老保险个人缴纳")
    medical: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="医疗保险个人缴纳")
    unemployment: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="失业保险个人缴纳")
    housing_fund: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="住房公积金个人缴纳")

    # 公司缴纳
    pension_company: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="养老保险公司缴纳")
    medical_company: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="医疗保险公司缴纳")
    unemployment_company: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="失业保险公司缴纳")
    injury_company: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="工伤保险公司缴纳")
    maternity_company: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="生育保险公司缴纳")
    housing_fund_company: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, comment="住房公积金公司缴纳")
