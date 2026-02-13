"""法务管理数据模型"""

from app.models.legal.contract import Contract
from app.models.legal.contract_review import ContractReview
from app.models.legal.contract_template import ContractTemplate

__all__ = [
    "ContractTemplate",
    "Contract",
    "ContractReview",
]
