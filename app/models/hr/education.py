"""教育背景模型"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Education(Base):
    """员工教育背景

    Attributes:
        employee_id: 员工 ID
        degree: 学历（大专/本科/硕士/博士/MBA）
        major: 专业
        school: 院校名称
        graduation_year: 毕业年份
    """

    __tablename__ = "educations"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    degree: Mapped[str] = mapped_column(String(16), comment="学历")
    major: Mapped[str] = mapped_column(String(64), comment="专业")
    school: Mapped[str] = mapped_column(String(128), comment="院校名称")
    graduation_year: Mapped[int] = mapped_column(comment="毕业年份")
