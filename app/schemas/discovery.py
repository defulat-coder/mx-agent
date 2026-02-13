"""人才发现引擎响应 Schema — 6 个发现场景的结构化结果"""

import datetime as dt

from pydantic import BaseModel, Field

from app.schemas.hr import (
    CertificateResponse,
    DevelopmentPlanResponse,
    EducationResponse,
    EmployeeInfoResponse,
    EmploymentHistoryResponse,
    PerformanceReviewResponse,
    ProjectExperienceResponse,
    SkillResponse,
    TalentReviewResponse,
    TrainingResponse,
)


class HiddenTalentCandidate(BaseModel):
    """被埋没高潜候选人"""

    info: EmployeeInfoResponse = Field(description="员工基本信息")
    performance_trend: list[str] = Field(description="近期绩效评级轨迹，如 ['B+', 'A', 'A']")
    self_initiated_training_count: int = Field(description="自主报名培训数")
    idp_completion_rate: float = Field(description="IDP 完成率")
    current_nine_grid: str = Field(description="当前九宫格位置")
    current_tag: str = Field(description="当前人才标签")
    signals: list[str] = Field(description="关注信号摘要")


class HiddenTalentResult(BaseModel):
    """被埋没高潜识别结果"""

    candidates: list[HiddenTalentCandidate] = Field(description="候选人列表")
    total: int = Field(description="候选人总数")


class FlightRiskCandidate(BaseModel):
    """流失风险候选人"""

    info: EmployeeInfoResponse = Field(description="员工基本信息")
    performance_ratings: list[str] = Field(description="近期绩效评级")
    level_tenure_years: float = Field(description="当前职级停留年数")
    idp_status: str = Field(description="IDP 状态（无/进行中/已完成/已放弃）")
    recent_overtime_hours: float = Field(description="近 3 个月加班总时长")
    risk_signals: list[str] = Field(description="风险信号")


class FlightRiskResult(BaseModel):
    """流失风险预警结果"""

    candidates: list[FlightRiskCandidate] = Field(description="风险人员列表")
    total: int = Field(description="风险人员总数")


class PromotionReadinessItem(BaseModel):
    """晋升准备度评估项"""

    info: EmployeeInfoResponse = Field(description="员工基本信息")
    level_tenure_years: float = Field(description="当前职级停留年数")
    latest_rating: str = Field(description="最近绩效评级")
    management_training_count: int = Field(description="管理类培训完成数")
    idp_progress: int = Field(description="IDP 平均进度")
    readiness_score: int = Field(description="综合就绪度评分 1-100")


class PromotionReadinessResult(BaseModel):
    """晋升准备度评估结果"""

    items: list[PromotionReadinessItem] = Field(description="评估列表")


class CandidateMatchItem(BaseModel):
    """岗位适配候选人"""

    info: EmployeeInfoResponse = Field(description="员工基本信息")
    matched_skills: list[str] = Field(description="匹配的技能")
    relevant_projects: list[str] = Field(description="相关项目名称")
    latest_rating: str = Field(description="最近绩效评级")
    match_summary: str = Field(description="匹配度说明")


class CandidateMatchResult(BaseModel):
    """岗位适配推荐结果"""

    candidates: list[CandidateMatchItem] = Field(description="候选人列表")
    total: int = Field(description="候选人总数")
    notice: str = Field(default="", description="提示信息（如技能数据不足提醒）")


class TalentPortraitResult(BaseModel):
    """完整人才画像"""

    info: EmployeeInfoResponse = Field(description="员工基本信息")
    educations: list[EducationResponse] = Field(description="教育背景")
    skills: list[SkillResponse] = Field(description="技能标签")
    projects: list[ProjectExperienceResponse] = Field(description="项目经历")
    certificates: list[CertificateResponse] = Field(description="证书认证")
    performance_reviews: list[PerformanceReviewResponse] = Field(description="绩效轨迹")
    trainings: list[TrainingResponse] = Field(description="培训记录")
    development_plans: list[DevelopmentPlanResponse] = Field(description="个人发展计划")
    talent_reviews: list[TalentReviewResponse] = Field(description="九宫格盘点历史")
    employment_histories: list[EmploymentHistoryResponse] = Field(description="岗位变动历史")


class SkillCoverage(BaseModel):
    """技能覆盖统计"""

    skill_name: str = Field(description="技能名称")
    count: int = Field(description="拥有人数")
    levels: dict[str, int] = Field(description="各等级人数分布")


class TeamCapabilityGapResult(BaseModel):
    """团队能力短板分析结果"""

    department_name: str = Field(description="部门名称")
    total_employees: int = Field(description="部门总人数")
    skill_coverage: list[SkillCoverage] = Field(description="技能覆盖统计")
    high_frequency_skills: list[str] = Field(description="团队高频技能")
    rare_skills: list[str] = Field(description="团队稀缺技能（仅1人掌握）")
    suggestions: list[str] = Field(description="补强建议")
    notice: str = Field(default="", description="提示信息")
