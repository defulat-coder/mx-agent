"""人才盘点（九宫格）模型"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TalentReview(Base):
    """年度人才盘点记录，绩效 × 潜力 九宫格评估。

    Attributes:
        employee_id: 员工 ID
        review_year: 盘点年度
        performance: 绩效维度（高/中/低）
        potential: 潜力维度（高/中/低）
        nine_grid_pos: 九宫格位置（明星/骨干/潜力股/中坚/待雕琢/守成者/专家/待观察/淘汰区）
        tag: 人才标签（高潜/关键岗位/继任候选/普通）
        reviewer: 盘点人
        comment: 盘点评语
    """

    __tablename__ = "talent_reviews"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True, comment="员工ID")
    review_year: Mapped[int] = mapped_column(comment="盘点年度")
    performance: Mapped[str] = mapped_column(String(8), comment="绩效维度")
    potential: Mapped[str] = mapped_column(String(8), comment="潜力维度")
    nine_grid_pos: Mapped[str] = mapped_column(String(16), comment="九宫格位置")
    tag: Mapped[str] = mapped_column(String(32), comment="人才标签")
    reviewer: Mapped[str] = mapped_column(String(64), comment="盘点人")
    comment: Mapped[str] = mapped_column(String(512), default="", comment="盘点评语")
