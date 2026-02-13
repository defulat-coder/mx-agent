"""证书认证模型"""

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Certificate(Base):
    """员工证书认证记录

    Attributes:
        employee_id: 员工 ID
        name: 证书名称
        issuer: 颁发机构
        issue_date: 颁发日期
        expiry_date: 有效期，为空表示永久有效
        category: 证书分类（专业技术/管理/语言/行业）
    """

    __tablename__ = "certificates"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    name: Mapped[str] = mapped_column(String(128), comment="证书名称")
    issuer: Mapped[str] = mapped_column(String(128), comment="颁发机构")
    issue_date: Mapped[date] = mapped_column(Date, comment="颁发日期")
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True, default=None, comment="有效期")
    category: Mapped[str] = mapped_column(String(16), comment="证书分类")
