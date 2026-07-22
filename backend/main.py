"""FastAPI entry point for EnergyShield."""

from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from agents.procurement_agent import run_procurement_agent
from agents.risk_agent import run_risk_agent
from agents.scenario_agent import (
    ScenarioOutput,
    run_scenario_agent,
    run_scenario_comparison,
)
from database import DATABASE_PATH, get_db
from models import (
    CorridorRisk,
    GeopoliticalSignal,
    ProcurementRecommendation,
    ScenarioResult,
    Supplier,
)
from schemas import (
    CorridorRiskRead,
    GeopoliticalSignalRead,
    HealthResponse,
    PipelineRequest,
    PipelineResult,
    ProcurementRecommendationRead,
    ProcurementRequest,
    ProcurementResult,
    RiskAssessmentResult,
    ScenarioRequest,
    ScenarioResultRead,
)
from seed import initialize_and_seed


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_and_seed()
    yield


app = FastAPI(
    title="EnergyShield API",
    description="AI-driven energy supply chain resilience for India.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health(db: Session = Depends(get_db)) -> HealthResponse:
    models = {
        "corridor_risks": CorridorRisk,
        "suppliers": Supplier,
        "geopolitical_signals": GeopoliticalSignal,
        "scenario_results": ScenarioResult,
        "procurement_recommendations": ProcurementRecommendation,
    }
    counts = {
        table_name: db.scalar(select(func.count()).select_from(model)) or 0
        for table_name, model in models.items()
    }
    return HealthResponse(
        status="healthy",
        database=DATABASE_PATH.name,
        table_counts=counts,
    )


@app.post(
    "/api/agents/risk/run",
    response_model=list[RiskAssessmentResult],
    tags=["agents"],
)
async def run_geopolitical_risk_agent(
    db: Session = Depends(get_db),
) -> list[RiskAssessmentResult]:
    unprocessed_count = db.scalar(
        select(func.count())
        .select_from(GeopoliticalSignal)
        .where(GeopoliticalSignal.processed.is_(False))
    )
    if unprocessed_count == 0:
        db.execute(update(GeopoliticalSignal).values(processed=False))
        db.commit()

    return await run_risk_agent(db)


@app.get(
    "/api/corridors",
    response_model=list[CorridorRiskRead],
    tags=["energy-security"],
)
def list_corridors(db: Session = Depends(get_db)) -> list[CorridorRisk]:
    return list(
        db.scalars(
            select(CorridorRisk).order_by(CorridorRisk.current_risk_score.desc())
        )
    )


@app.get(
    "/api/signals",
    response_model=list[GeopoliticalSignalRead],
    tags=["energy-security"],
)
def list_signals(db: Session = Depends(get_db)) -> list[GeopoliticalSignal]:
    return list(
        db.scalars(
            select(GeopoliticalSignal).order_by(
                GeopoliticalSignal.timestamp.desc()
            )
        )
    )


@app.post(
    "/api/agents/scenario/run",
    response_model=ScenarioOutput,
    tags=["agents"],
)
async def run_hormuz_scenario(
    request: ScenarioRequest,
    db: Session = Depends(get_db),
) -> ScenarioOutput:
    return await run_scenario_agent(
        db=db,
        closure_percentage=request.closure_percentage,
        scenario_name=request.scenario_name,
    )


@app.get(
    "/api/scenarios",
    response_model=list[ScenarioResultRead],
    tags=["energy-security"],
)
def list_scenarios(db: Session = Depends(get_db)) -> list[ScenarioResult]:
    return list(
        db.scalars(
            select(ScenarioResult)
            .order_by(ScenarioResult.computed_at.desc())
            .limit(10)
        )
    )


@app.get(
    "/api/scenarios/compare",
    response_model=list[ScenarioOutput],
    tags=["energy-security"],
)
def compare_scenarios(
    closures: str = Query(
        default="0.2,0.4,0.6,0.8",
        description="Comma-separated closure fractions between 0.0 and 1.0",
    ),
) -> list[ScenarioOutput]:
    try:
        closure_values = [
            float(value.strip()) for value in closures.split(",") if value.strip()
        ]
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="closures must be comma-separated numbers between 0.0 and 1.0",
        ) from exc

    if not closure_values or any(
        not 0.0 <= closure <= 1.0 for closure in closure_values
    ):
        raise HTTPException(
            status_code=422,
            detail="closures must contain values between 0.0 and 1.0",
        )

    return [
        run_scenario_comparison(
            closure,
            f"Hormuz {closure * 100:g}% Closure",
        )
        for closure in closure_values
    ]


@app.post(
    "/api/agents/procurement/run",
    response_model=list[ProcurementResult],
    tags=["agents"],
)
async def run_procurement_orchestrator(
    request: ProcurementRequest,
    db: Session = Depends(get_db),
) -> list[ProcurementResult]:
    try:
        return await run_procurement_agent(
            db=db,
            closure_percentage=request.closure_percentage,
            import_gap_mbd=request.import_gap_mbd,
            scenario_id=request.scenario_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post(
    "/api/agents/full-pipeline/run",
    response_model=PipelineResult,
    tags=["agents"],
)
async def run_full_energyshield_pipeline(
    request: PipelineRequest,
    db: Session = Depends(get_db),
) -> PipelineResult:
    unprocessed_count = db.scalar(
        select(func.count())
        .select_from(GeopoliticalSignal)
        .where(GeopoliticalSignal.processed.is_(False))
    )
    if unprocessed_count == 0:
        db.execute(update(GeopoliticalSignal).values(processed=False))
        db.commit()

    risk_assessments = await run_risk_agent(db)
    previous_scenario_id = db.scalar(select(func.max(ScenarioResult.id))) or 0
    scenario = await run_scenario_agent(
        db=db,
        closure_percentage=request.closure_percentage,
        scenario_name=request.scenario_name,
    )
    scenario_record = db.scalar(
        select(ScenarioResult)
        .where(
            ScenarioResult.id > previous_scenario_id,
            ScenarioResult.scenario_name == scenario.scenario_name,
        )
        .order_by(ScenarioResult.id.desc())
    )
    if scenario_record is None:
        raise HTTPException(
            status_code=500,
            detail="Scenario completed but its database record could not be resolved",
        )

    procurement_recommendations = await run_procurement_agent(
        db=db,
        closure_percentage=request.closure_percentage,
        import_gap_mbd=scenario.import_gap_mbd,
        scenario_id=scenario_record.id,
    )
    return PipelineResult(
        risk_assessments=risk_assessments,
        scenario=asdict(scenario),
        procurement_recommendations=procurement_recommendations,
    )


@app.get(
    "/api/procurement/recommendations",
    response_model=list[ProcurementRecommendationRead],
    tags=["energy-security"],
)
def list_procurement_recommendations(
    scenario_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> list[ProcurementRecommendation]:
    statement = select(ProcurementRecommendation)
    if scenario_id is not None:
        statement = statement.where(
            ProcurementRecommendation.scenario_id == scenario_id
        )
    return list(
        db.scalars(statement.order_by(ProcurementRecommendation.rank.asc()))
    )
