"""Pydantic request and response schemas for EnergyShield."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Score = float
CrudeGrade = Literal["Heavy Sour", "Medium Sour", "Light Sweet", "Light Sour"]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CorridorRiskBase(BaseModel):
    corridor_name: str
    region: str
    base_risk_score: Score = Field(ge=0, le=1)
    current_risk_score: Score = Field(ge=0, le=1)
    risk_factors: dict[str, Any]


class CorridorRiskRead(CorridorRiskBase, ORMModel):
    id: int
    last_updated: datetime


class SupplierBase(BaseModel):
    name: str
    country: str
    region: str
    crude_grade: CrudeGrade
    base_price_usd_bbl: float = Field(gt=0)
    availability_score: Score = Field(ge=0, le=1)
    primary_corridor: str
    refinery_compatibility: Score = Field(ge=0, le=1)
    lead_time_days: int = Field(gt=0)
    geopolitical_safety_score: Score = Field(ge=0, le=1)


class SupplierRead(SupplierBase, ORMModel):
    id: int


class GeopoliticalSignalBase(BaseModel):
    signal_type: str
    source: str
    headline: str
    affected_corridor: str
    severity: Score = Field(ge=0, le=1)
    timestamp: datetime
    processed: bool = False


class GeopoliticalSignalRead(GeopoliticalSignalBase, ORMModel):
    id: int


class RiskAssessmentResult(BaseModel):
    corridor_name: str
    previous_score: Score = Field(ge=0, le=1)
    new_score: Score = Field(ge=0, le=1)
    delta: float
    reasoning_trace: str
    signals_processed: int = Field(ge=0)


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    closure_percentage: float = Field(gt=0.0, le=1.0)
    scenario_name: str = Field(
        default="Hormuz Partial Closure", min_length=1, max_length=200
    )


class ScenarioResultBase(BaseModel):
    scenario_name: str
    trigger_corridor: str
    closure_percentage: float = Field(gt=0, le=1)
    import_gap_mbd: float = Field(ge=0)
    price_impact_pct: float
    gdp_impact_pct: float
    refinery_stress_score: Score = Field(ge=0, le=1)
    spr_days_remaining: float = Field(ge=0)


class ScenarioResultRead(ScenarioResultBase, ORMModel):
    id: int
    computed_at: datetime


class ProcurementRequest(BaseModel):
    closure_percentage: float = Field(ge=0.0, le=1.0)
    import_gap_mbd: float = Field(ge=0)
    scenario_id: int | None = Field(default=None, gt=0)


class PipelineRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    closure_percentage: float = Field(gt=0.0, le=1.0)
    scenario_name: str = Field(
        default="Hormuz Partial Closure", min_length=1, max_length=200
    )


class ProcurementResult(BaseModel):
    rank: int = Field(gt=0)
    supplier_name: str
    country: str
    crude_grade: str
    composite_score: Score = Field(ge=0, le=1)
    price_score: Score = Field(ge=0, le=1)
    time_score: Score = Field(ge=0, le=1)
    grade_score: Score = Field(ge=0, le=1)
    corridor_safety_score: Score = Field(ge=0, le=1)
    base_price_usd_bbl: float = Field(gt=0)
    lead_time_days: int = Field(gt=0)
    volume_mbd: float = Field(ge=0)
    reasoning_trace: str


class PipelineScenarioResult(BaseModel):
    scenario_name: str
    closure_percentage: float = Field(gt=0, le=1)
    closure_pct_display: int = Field(gt=0, le=100)
    import_gap_mbd: float = Field(ge=0)
    import_gap_pct: float = Field(ge=0, le=1)
    price_impact_pct: float = Field(ge=0)
    new_brent_price: float = Field(gt=0)
    refinery_stress_score: Score = Field(ge=0, le=1)
    spr_days_remaining: float = Field(ge=0)
    gdp_impact_pct: float
    unmet_gap_mbd: float = Field(ge=0)
    narrative: str
    computed_at: str


class PipelineResult(BaseModel):
    risk_assessments: list[RiskAssessmentResult]
    scenario: PipelineScenarioResult
    procurement_recommendations: list[ProcurementResult]


class ProcurementRecommendationBase(BaseModel):
    scenario_id: int
    supplier_id: int
    rank: int = Field(gt=0)
    composite_score: Score = Field(ge=0, le=1)
    price_score: Score = Field(ge=0, le=1)
    time_score: Score = Field(ge=0, le=1)
    grade_score: Score = Field(ge=0, le=1)
    corridor_safety_score: Score = Field(ge=0, le=1)
    volume_mbd: float = Field(ge=0)
    reasoning_trace: str


class ProcurementRecommendationRead(ProcurementRecommendationBase, ORMModel):
    id: int
    generated_at: datetime


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    database: str
    table_counts: dict[str, int]
