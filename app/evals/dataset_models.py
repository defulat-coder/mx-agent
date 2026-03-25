from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

EvalLayer = Literal["router", "agent"]
EvalDomain = Literal["hr", "it", "admin", "finance", "legal", "talent", "cross_domain"]
EvalScenarioType = Literal["smoke", "core", "workflow", "forbidden", "edge"]
EvalPriority = Literal["p0", "p1", "p2"]
EvalMatchMode = Literal["all", "any", "ordered", "none"]
NonEmptyStr = Annotated[str, Field(min_length=1)]


class EvalMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: NonEmptyStr
    title: NonEmptyStr
    layer: EvalLayer
    domain: EvalDomain
    scenario_type: EvalScenarioType
    priority: EvalPriority


class EvalAuth(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_id: Annotated[int, Field(gt=0)]
    roles: list[NonEmptyStr] = Field(default_factory=list)
    department_id: Annotated[int, Field(gt=0)] | None = None
    persona_label: NonEmptyStr


class EvalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_input: NonEmptyStr


class EvalExpectation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_agents: list[NonEmptyStr] = Field(default_factory=list)
    expected_agent_mode: EvalMatchMode = "none"
    expected_tools: list[NonEmptyStr] = Field(default_factory=list)
    expected_tool_mode: EvalMatchMode = "none"
    forbidden_tools: list[NonEmptyStr] = Field(default_factory=list)
    response_must_include: list[NonEmptyStr] = Field(default_factory=list)
    response_must_not_include: list[NonEmptyStr] = Field(default_factory=list)
    business_assertions: list[NonEmptyStr] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_mode_consistency(self) -> "EvalExpectation":
        if self.expected_agent_mode == "none":
            if self.expected_agents:
                raise ValueError("expected_agents must be empty when expected_agent_mode is none")
        elif not self.expected_agents:
            raise ValueError("expected_agents must not be empty when expected_agent_mode is not none")

        if self.expected_tool_mode == "none":
            if self.expected_tools:
                raise ValueError("expected_tools must be empty when expected_tool_mode is none")
        elif not self.expected_tools:
            raise ValueError("expected_tools must not be empty when expected_tool_mode is not none")

        return self


class EvalSeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    depends_on_entities: list[NonEmptyStr] = Field(default_factory=list)
    seed_version: NonEmptyStr = "current"
    notes: str = ""


class EvalDatasetCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: EvalMeta
    auth: EvalAuth
    input: EvalInput
    expectation: EvalExpectation
    seed: EvalSeed


class EvalTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: EvalMeta
    auth_profile: NonEmptyStr
    input: EvalInput
    expectation: EvalExpectation
    seed: EvalSeed = Field(default_factory=EvalSeed)
