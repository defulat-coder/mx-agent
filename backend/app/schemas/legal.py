"""法务相关响应 Schema"""

import datetime as dt

from pydantic import BaseModel, Field


class ContractTemplateResponse(BaseModel):
    """合同模板"""

    template_id: int = Field(description="模板 ID")
    name: str = Field(description="模板名称")
    type: str = Field(description="合同类型")
    description: str = Field(default="", description="模板说明")
    file_url: str = Field(default="", description="下载链接")


class ContractResponse(BaseModel):
    """合同记录"""

    contract_id: int = Field(description="合同 ID")
    contract_no: str = Field(description="合同编号")
    title: str = Field(description="合同标题")
    type: str = Field(description="合同类型")
    party_a: str = Field(description="甲方")
    party_b: str = Field(description="乙方")
    amount: float = Field(description="合同金额")
    start_date: dt.date = Field(description="生效日期")
    end_date: dt.date = Field(description="到期日期")
    status: str = Field(description="状态")
    submitted_by: int = Field(description="提交人 ID")
    submitted_name: str = Field(default="", description="提交人姓名")
    department_name: str = Field(default="", description="部门名称")
    created_at: dt.datetime | None = Field(default=None, description="创建时间")


class ContractReviewResponse(BaseModel):
    """合同审查记录"""

    review_id: int = Field(description="审查记录 ID")
    contract_id: int = Field(description="合同 ID")
    reviewer_id: int = Field(description="审查人 ID")
    reviewer_name: str = Field(default="", description="审查人姓名")
    action: str = Field(description="审查动作")
    opinion: str = Field(default="", description="审查意见")
    created_at: dt.datetime | None = Field(default=None, description="审查时间")


class ContractAnalysisResult(BaseModel):
    """合同条款分析结果"""

    contract_id: int = Field(description="合同 ID")
    contract_no: str = Field(description="合同编号")
    summary: str = Field(description="条款摘要")
    risks: list[str] = Field(default_factory=list, description="风险点列表")
    suggestions: list[str] = Field(default_factory=list, description="建议列表")
    disclaimer: str = Field(default="以上分析仅供参考，不构成法律意见。具体法律事务请咨询专业律师。", description="免责声明")


class ContractStatsResponse(BaseModel):
    """合同统计"""

    total_count: int = Field(description="合同总数")
    total_amount: float = Field(description="合同总金额")
    status_distribution: dict[str, int] = Field(default_factory=dict, description="状态分布")
    type_distribution: dict[str, int] = Field(default_factory=dict, description="类型分布")
    expiring_count: int = Field(default=0, description="即将到期数（30天内）")
