"""SQLAlchemy ORM models for the EnergyShield data store."""

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CorridorRisk(Base):
    __tablename__ = "corridor_risks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    corridor_name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    base_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    current_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_factors: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    crude_grade: Mapped[str] = mapped_column(String, nullable=False)
    base_price_usd_bbl: Mapped[float] = mapped_column(Float, nullable=False)
    availability_score: Mapped[float] = mapped_column(Float, nullable=False)
    primary_corridor: Mapped[str] = mapped_column(String, nullable=False, index=True)
    refinery_compatibility: Mapped[float] = mapped_column(Float, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    geopolitical_safety_score: Mapped[float] = mapped_column(Float, nullable=False)


class GeopoliticalSignal(Base):
    __tablename__ = "geopolitical_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    signal_type: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    affected_corridor: Mapped[str] = mapped_column(String, nullable=False, index=True)
    severity: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ScenarioResult(Base):
    __tablename__ = "scenario_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_name: Mapped[str] = mapped_column(String, nullable=False)
    trigger_corridor: Mapped[str] = mapped_column(String, nullable=False, index=True)
    closure_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    import_gap_mbd: Mapped[float] = mapped_column(Float, nullable=False)
    price_impact_pct: Mapped[float] = mapped_column(Float, nullable=False)
    gdp_impact_pct: Mapped[float] = mapped_column(Float, nullable=False)
    refinery_stress_score: Mapped[float] = mapped_column(Float, nullable=False)
    spr_days_remaining: Mapped[float] = mapped_column(Float, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )


class ProcurementRecommendation(Base):
    __tablename__ = "procurement_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenario_results.id"), nullable=False, index=True
    )
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"), nullable=False, index=True
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    price_score: Mapped[float] = mapped_column(Float, nullable=False)
    time_score: Mapped[float] = mapped_column(Float, nullable=False)
    grade_score: Mapped[float] = mapped_column(Float, nullable=False)
    corridor_safety_score: Mapped[float] = mapped_column(Float, nullable=False)
    volume_mbd: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning_trace: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
