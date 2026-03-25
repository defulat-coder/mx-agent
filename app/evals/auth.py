from typing import Callable

import jwt

from app.evals.runner import EvalCase


def build_eval_token(case: EvalCase, secret: str) -> str:
    profile = case.auth_profile
    payload = {
        "employee_id": profile.employee_id if profile else 1,
        "roles": list(profile.roles) if profile else [],
        "department_id": profile.department_id if profile else None,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def make_auth_token_resolver(
    secret: str,
    static_token: str = "",
) -> Callable[[EvalCase], str]:
    def resolve(case: EvalCase) -> str:
        if static_token:
            return static_token
        return build_eval_token(case, secret)

    return resolve
