"""绩效考评模型"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PerformanceReview(Base):
    """员工半年度绩效考评记录。

    Attributes:
        employee_id: 员工 ID
        year: 考评年度
        half: 上半年/下半年
        rating: 等级（A/B+/B/C/D）
        score: 百分制分数
        reviewer: 考评人姓名
        comment: 考评评语
    """

    __tablename__ = "performance_reviews"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    year: Mapped[int] = mapped_column(comment="考评年度")
    half: Mapped[str] = mapped_column(String(16), comment="半年度标识")
    rating: Mapped[str] = mapped_column(String(8), comment="考评等级")
    score: Mapped[int] = mapped_column(comment="考评分数")
    reviewer: Mapped[str] = mapped_column(String(64), comment="考评人姓名")
    comment: Mapped[str] = mapped_column(String(512), default="", comment="考评评语")
