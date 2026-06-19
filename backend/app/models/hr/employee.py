"""员工基本信息模型"""

from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Employee(Base):
    """员工基本信息。

    Attributes:
        name: 姓名
        employee_no: 工号，全局唯一
        department_id: 所属部门 ID
        position: 岗位
        level: 职级
        hire_date: 入职日期
        status: 在职/离职/试用期
        email: 邮箱
        phone: 手机号
    """

    __tablename__ = "employees"

    name: Mapped[str] = mapped_column(String(64), comment="姓名")
    employee_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, comment="工号")
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), comment="所属部门ID")
    position: Mapped[str] = mapped_column(String(64), default="", comment="岗位")
    level: Mapped[str] = mapped_column(String(32), default="", comment="职级")
    hire_date: Mapped[date | None] = mapped_column(comment="入职日期")
    status: Mapped[str] = mapped_column(String(16), default="在职", comment="在职状态")
    email: Mapped[str] = mapped_column(String(128), default="", comment="邮箱")
    phone: Mapped[str] = mapped_column(String(32), default="", comment="手机号")
