"""LangGraph procurement orchestrator for post-Hormuz sourcing."""

from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, NotRequired, TypedDict
from uuid import uuid4

from dotenv import load_dotenv
from groq import Groq
from langgraph.channels import UntrackedValue
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from sqlalchemy import select
from sqlalchemy.orm import Session

from agents.scenario_agent import calculate_scenario_impacts
from models import (
    CorridorRisk,
    ProcurementRecommendation,
    ScenarioResult,
    Supplier,
)
from schemas import ProcurementResult


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DISRUPTED_CORRIDOR = "Strait of Hormuz"
SYSTEM_PROMPT = (
    "You are a senior procurement analyst for an Indian oil refinery. "
    "You explain supplier ranking decisions clearly to procurement directors. "
    "Be specific about numbers. Write plain English only."
)


class SupplierPayload(TypedDict):
    id: int
    name: str
    country: str
    crude_grade: str
    base_price_usd_bbl: float
    primary_corridor: str
    refinery_compatibility: float
    lead_time_days: int


class ScoredSupplier(SupplierPayload):
    rank: int
    composite_score: float
    price_score: float
    time_score: float
    grade_score: float
    corridor_safety_score: float


class RecommendationPayload(ScoredSupplier):
    volume_mbd: float
    reasoning_trace: str


class ProcurementAgentState(TypedDict, total=False):
    closure_percentage: float
    import_gap_mbd: float
    scenario_id: int | None
    available_suppliers: list[SupplierPayload]
    scored_suppliers: list[ScoredSupplier]
    top3_reasoning: dict[int, str]
    recommendations: list[RecommendationPayload]
    db_session: Annotated[Session, UntrackedValue(Session)]


class ProcurementGraphOutput(TypedDict):
    recommendations: list[RecommendationPayload]


def _serialize_supplier(supplier: Supplier) -> SupplierPayload:
    return {
        "id": supplier.id,
        "name": supplier.name,
        "country": supplier.country,
        "crude_grade": supplier.crude_grade,
        "base_price_usd_bbl": supplier.base_price_usd_bbl,
        "primary_corridor": supplier.primary_corridor,
        "refinery_compatibility": supplier.refinery_compatibility,
        "lead_time_days": supplier.lead_time_days,
    }


async def fetch_and_filter_suppliers(state: ProcurementAgentState) -> dict:
    """Fetch every supplier and remove routes disrupted by Hormuz closure."""

    db = state["db_session"]
    suppliers = list(db.scalars(select(Supplier).order_by(Supplier.id.asc())))
    available = [
        _serialize_supplier(supplier)
        for supplier in suppliers
        if supplier.primary_corridor != DISRUPTED_CORRIDOR
    ]
    return {"available_suppliers": available}


async def score_and_rank(state: ProcurementAgentState) -> dict:
    """Calculate the four normalized sub-scores and weighted ranking."""

    suppliers = state.get("available_suppliers", [])
    if not suppliers:
        return {"scored_suppliers": []}

    db = state["db_session"]
    max_price = max(supplier["base_price_usd_bbl"] for supplier in suppliers)
    min_price = min(supplier["base_price_usd_bbl"] for supplier in suppliers)
    max_days = max(supplier["lead_time_days"] for supplier in suppliers)
    min_days = min(supplier["lead_time_days"] for supplier in suppliers)
    corridor_risks = {
        corridor.corridor_name: corridor.current_risk_score
        for corridor in db.scalars(select(CorridorRisk))
    }

    scored: list[ScoredSupplier] = []
    for supplier in suppliers:
        price_score = 1.0 - (
            (supplier["base_price_usd_bbl"] - min_price)
            / (max_price - min_price + 0.001)
        )
        time_score = 1.0 - (
            (supplier["lead_time_days"] - min_days)
            / (max_days - min_days + 0.001)
        )
        grade_score = supplier["refinery_compatibility"]
        corridor_risk = corridor_risks.get(supplier["primary_corridor"])
        corridor_safety_score = (
            1.0 - corridor_risk if corridor_risk is not None else 0.5
        )
        composite_score = round(
            (price_score * 0.25)
            + (time_score * 0.25)
            + (grade_score * 0.30)
            + (corridor_safety_score * 0.20),
            4,
        )
        scored.append(
            {
                **supplier,
                "rank": 0,
                "composite_score": composite_score,
                "price_score": price_score,
                "time_score": time_score,
                "grade_score": grade_score,
                "corridor_safety_score": corridor_safety_score,
            }
        )

    scored.sort(key=lambda supplier: (-supplier["composite_score"], supplier["name"]))
    for rank, supplier in enumerate(scored, start=1):
        supplier["rank"] = rank
    return {"scored_suppliers": scored}


def _mock_reasoning(supplier: ScoredSupplier) -> str:
    alternatives = ["strong", "viable", "acceptable"]
    routing_risks = ["low", "moderate", "elevated"]
    rank = supplier["rank"]
    safety = supplier["corridor_safety_score"]
    return (
        f"{supplier['name']} ranks #{rank} with a composite score of "
        f"{supplier['composite_score']:.3f}. Grade compatibility of "
        f"{supplier['grade_score']:.0%} and {supplier['lead_time_days']}-day lead "
        f"time make it a {alternatives[min(rank - 1, 2)]} alternative. "
        f"Corridor safety score of {safety:.2f} reflects "
        f"{routing_risks[min(int(safety * 3), 2)]} routing risk."
    )


def _reasoning_prompt(state: ProcurementAgentState, top_suppliers: list[ScoredSupplier]) -> str:
    supplier_sections = []
    for supplier in top_suppliers:
        supplier_sections.append(
            f"Rank {supplier['rank']}: {supplier['name']} ({supplier['country']})\n"
            f"  Composite score: {supplier['composite_score']:.3f}\n"
            f"  Price: ${supplier['base_price_usd_bbl']}/bbl | "
            f"Lead time: {supplier['lead_time_days']} days | "
            f"Grade compatibility: {supplier['grade_score']:.0%} | "
            f"Corridor safety: {supplier['corridor_safety_score']:.2f}"
        )
    supplier_list = "\n\n".join(supplier_sections)
    return f"""Hormuz disruption scenario: {state['closure_percentage'] * 100:g}% closure
Import gap to fill: {state['import_gap_mbd']:.2f} MBD

Top 3 ranked alternative suppliers after Hormuz disruption:

{supplier_list}

Write exactly 3 short paragraphs (one per supplier) explaining why each supplier
is ranked where it is, referencing its specific scores. Each paragraph must be
2-3 sentences maximum. Start each paragraph with the supplier name."""


def _split_reasoning(response_text: str, expected_parts: int) -> list[str]:
    parts = [
        part.strip()
        for part in re.split(r"\n\s*\n+", response_text.strip())
        if part.strip()
    ]
    if len(parts) < expected_parts:
        parts = [
            part.strip()
            for part in re.split(
                r"(?im)(?=^\s*Rank\s*[1-3]\s*:)", response_text.strip()
            )
            if part.strip()
        ]
    return parts


async def generate_top3_reasoning(state: ProcurementAgentState) -> dict:
    """Generate one reasoning paragraph for each of the top three suppliers."""

    top_suppliers = state.get("scored_suppliers", [])[:3]
    if not top_suppliers:
        return {"top3_reasoning": {}}

    if not os.getenv("GROQ_API_KEY", "").strip():
        return {
            "top3_reasoning": {
                supplier["id"]: _mock_reasoning(supplier)
                for supplier in top_suppliers
            }
        }

    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _reasoning_prompt(state, top_suppliers)},
        ],
        temperature=0.1,
        max_tokens=700,
    )
    response_text = (response.choices[0].message.content or "").strip()
    parts = _split_reasoning(response_text, len(top_suppliers))
    if len(parts) < len(top_suppliers):
        parts = [response_text] + [""] * (len(top_suppliers) - 1)
    return {
        "top3_reasoning": {
            supplier["id"]: parts[index]
            for index, supplier in enumerate(top_suppliers)
        }
    }


async def save_recommendations(state: ProcurementAgentState) -> dict:
    """Save every ranked recommendation and allocate volume to the top three."""

    db = state["db_session"]
    suppliers = state.get("scored_suppliers", [])
    reasoning = state.get("top3_reasoning", {})
    if not suppliers:
        return {"recommendations": []}

    top_supplier_count = min(3, len(suppliers))
    top_volume = state["import_gap_mbd"] / top_supplier_count
    generated_at = datetime.now(UTC)
    recommendations: list[RecommendationPayload] = []
    records: list[ProcurementRecommendation] = []
    for supplier in suppliers:
        volume_mbd = top_volume if supplier["rank"] <= 3 else 0.0
        reasoning_trace = reasoning.get(supplier["id"], "")
        records.append(
            ProcurementRecommendation(
                scenario_id=state["scenario_id"],
                supplier_id=supplier["id"],
                rank=supplier["rank"],
                composite_score=supplier["composite_score"],
                price_score=supplier["price_score"],
                time_score=supplier["time_score"],
                grade_score=supplier["grade_score"],
                corridor_safety_score=supplier["corridor_safety_score"],
                volume_mbd=volume_mbd,
                reasoning_trace=reasoning_trace,
                generated_at=generated_at,
            )
        )
        recommendations.append(
            {
                **supplier,
                "volume_mbd": volume_mbd,
                "reasoning_trace": reasoning_trace,
            }
        )

    try:
        db.add_all(records)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"recommendations": recommendations}


async def format_output(state: ProcurementAgentState) -> ProcurementGraphOutput:
    recommendations = [
        ProcurementResult(
            rank=item["rank"],
            supplier_name=item["name"],
            country=item["country"],
            crude_grade=item["crude_grade"],
            composite_score=item["composite_score"],
            price_score=item["price_score"],
            time_score=item["time_score"],
            grade_score=item["grade_score"],
            corridor_safety_score=item["corridor_safety_score"],
            base_price_usd_bbl=item["base_price_usd_bbl"],
            lead_time_days=item["lead_time_days"],
            volume_mbd=item["volume_mbd"],
            reasoning_trace=item["reasoning_trace"],
        ).model_dump()
        for item in state.get("recommendations", [])
    ]
    return {"recommendations": recommendations}


def _build_graph():
    workflow = StateGraph(
        ProcurementAgentState,
        output_schema=ProcurementGraphOutput,
    )
    workflow.add_node("fetch_and_filter_suppliers", fetch_and_filter_suppliers)
    workflow.add_node("score_and_rank", score_and_rank)
    workflow.add_node("generate_top3_reasoning", generate_top3_reasoning)
    workflow.add_node("save_recommendations", save_recommendations)
    workflow.add_node("format_output", format_output)
    workflow.add_edge(START, "fetch_and_filter_suppliers")
    workflow.add_edge("fetch_and_filter_suppliers", "score_and_rank")
    workflow.add_edge("score_and_rank", "generate_top3_reasoning")
    workflow.add_edge("generate_top3_reasoning", "save_recommendations")
    workflow.add_edge("save_recommendations", "format_output")
    workflow.add_edge("format_output", END)
    return workflow.compile(checkpointer=MemorySaver())


procurement_graph = _build_graph()


def _create_ad_hoc_scenario(
    db: Session,
    closure_percentage: float,
    import_gap_mbd: float,
) -> int:
    calc = calculate_scenario_impacts(closure_percentage)
    record = ScenarioResult(
        scenario_name=f"Ad hoc Hormuz {closure_percentage * 100:g}% Closure",
        trigger_corridor=DISRUPTED_CORRIDOR,
        closure_percentage=closure_percentage,
        import_gap_mbd=import_gap_mbd,
        price_impact_pct=calc["price_impact_pct"],
        gdp_impact_pct=calc["gdp_impact_pct"],
        refinery_stress_score=calc["refinery_stress_score"],
        spr_days_remaining=calc["spr_days_remaining"],
        computed_at=datetime.now(UTC),
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception:
        db.rollback()
        raise
    return record.id


async def run_procurement_agent(
    db: Session,
    closure_percentage: float,
    import_gap_mbd: float,
    scenario_id: int | None = None,
) -> list[ProcurementResult]:
    """Rank viable suppliers and persist recommendations for a scenario."""

    if not 0.0 <= closure_percentage <= 1.0:
        raise ValueError("closure_percentage must be between 0.0 and 1.0")
    if import_gap_mbd < 0:
        raise ValueError("import_gap_mbd must be non-negative")
    if scenario_id is None:
        scenario_id = _create_ad_hoc_scenario(
            db, closure_percentage, import_gap_mbd
        )
    elif db.get(ScenarioResult, scenario_id) is None:
        raise ValueError(f"ScenarioResult {scenario_id} does not exist")

    final_state = await procurement_graph.ainvoke(
        {
            "closure_percentage": closure_percentage,
            "import_gap_mbd": import_gap_mbd,
            "scenario_id": scenario_id,
            "available_suppliers": [],
            "scored_suppliers": [],
            "top3_reasoning": {},
            "recommendations": [],
            "db_session": db,
        },
        config={"configurable": {"thread_id": f"procurement-{uuid4()}"}},
        durability="exit",
    )
    return [
        ProcurementResult.model_validate(item)
        for item in final_state["recommendations"]
    ]
