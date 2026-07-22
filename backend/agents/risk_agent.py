"""LangGraph-powered geopolitical risk assessment agent."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, NotRequired, TypedDict
from uuid import uuid4

from dotenv import load_dotenv
from groq import Groq
from langgraph.channels import UntrackedValue
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models import CorridorRisk, GeopoliticalSignal
from schemas import RiskAssessmentResult


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SYSTEM_PROMPT = (
    "You are a geopolitical risk analyst specializing in energy supply chain "
    "security for India. You analyze signals affecting oil import corridors and "
    "produce precise risk assessments. Always output valid JSON only."
)


class SignalPayload(TypedDict):
    id: int
    signal_type: str
    source: str
    headline: str
    severity: float
    timestamp: str


class RiskAgentState(TypedDict, total=False):
    corridor_name: str
    signals: list[SignalPayload]
    previous_score: float
    new_score: float
    reasoning_trace: str
    # Sessions are request-scoped live objects and must never be checkpointed.
    db_session: Annotated[Session, UntrackedValue(Session)]
    result: NotRequired[RiskAssessmentResult]


def _serialize_signal(signal: GeopoliticalSignal) -> SignalPayload:
    return {
        "id": signal.id,
        "signal_type": signal.signal_type,
        "source": signal.source,
        "headline": signal.headline,
        "severity": signal.severity,
        "timestamp": signal.timestamp.isoformat(),
    }


async def fetch_corridor_data(state: RiskAgentState) -> dict:
    """Load the latest corridor score and its still-unprocessed signals."""

    db = state["db_session"]
    corridor_name = state["corridor_name"]
    corridor = db.scalar(
        select(CorridorRisk).where(CorridorRisk.corridor_name == corridor_name)
    )
    if corridor is None:
        raise LookupError(f"Unknown energy corridor: {corridor_name}")

    signals = list(
        db.scalars(
            select(GeopoliticalSignal)
            .where(
                GeopoliticalSignal.affected_corridor == corridor_name,
                GeopoliticalSignal.processed.is_(False),
            )
            .order_by(GeopoliticalSignal.timestamp.asc())
        )
    )
    return {
        "previous_score": corridor.current_risk_score,
        "signals": [_serialize_signal(signal) for signal in signals],
    }


def _format_signal_list(signals: list[SignalPayload]) -> str:
    return "\n".join(
        f"- [{signal['source']}] {signal['headline']} "
        f"(severity: {signal['severity']:.2f})"
        for signal in signals
    )


async def assess_risk(state: RiskAgentState) -> dict:
    """Assess the corridor with Groq or the deterministic mock formula."""

    signals = state.get("signals", [])
    previous_score = state["previous_score"]
    corridor_name = state["corridor_name"]

    if not signals:
        return {
            "new_score": previous_score,
            "reasoning_trace": (
                f"No unprocessed signals were found for {corridor_name}; "
                "the risk score was left unchanged."
            ),
        }

    average_severity = sum(signal["severity"] for signal in signals) / len(signals)
    if not os.getenv("GROQ_API_KEY", "").strip():
        new_score = min(1.0, previous_score + (average_severity * 0.15))
        reasoning = (
            f"MOCK MODE: {len(signals)} signals detected affecting {corridor_name}. "
            f"Severity average: {average_severity:.2f}. "
            f"Risk score adjusted from {previous_score:.2f} to {new_score:.2f} "
            "based on signal severity weighting."
        )
        return {"new_score": new_score, "reasoning_trace": reasoning}

    signal_list = _format_signal_list(signals)
    user_prompt = f"""Corridor: {corridor_name}
Current risk score: {previous_score}/1.0

New signals detected:
{signal_list}

Analyze these signals and respond with JSON only:
{{
  'new_risk_score': <float 0.0-1.0>,
  'reasoning_trace': '<3-5 sentence plain English explanation of why score changed, referencing specific signals, written for a procurement decision-maker, not a technical audience>'
}}"""

    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=300,
    )
    result_text = response.choices[0].message.content or ""
    try:
        parsed = json.loads(result_text)
        new_score = float(parsed["new_risk_score"])
        reasoning = str(parsed["reasoning_trace"]).strip()
        if not 0.0 <= new_score <= 1.0 or not reasoning:
            raise ValueError("Groq returned an invalid risk assessment")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        new_score = min(1.0, previous_score + average_severity * 0.15)
        reasoning = (
            f"Signal analysis: {len(signals)} signals processed for "
            f"{corridor_name}. Score adjusted to {new_score:.2f}."
        )

    return {
        "new_score": new_score,
        "reasoning_trace": reasoning,
    }


async def update_database(state: RiskAgentState) -> dict:
    """Persist the score and atomically mark the assessed signals processed."""

    signals = state.get("signals", [])
    if not signals:
        return {}

    db = state["db_session"]
    corridor = db.scalar(
        select(CorridorRisk).where(
            CorridorRisk.corridor_name == state["corridor_name"]
        )
    )
    if corridor is None:
        raise LookupError(f"Unknown energy corridor: {state['corridor_name']}")

    try:
        corridor.current_risk_score = state["new_score"]
        corridor.last_updated = datetime.now(UTC)
        signal_ids = [signal["id"] for signal in signals]
        db.execute(
            update(GeopoliticalSignal)
            .where(
                GeopoliticalSignal.id.in_(signal_ids),
                GeopoliticalSignal.processed.is_(False),
            )
            .values(processed=True)
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {}


async def format_result(state: RiskAgentState) -> dict:
    """Package the graph state as the public risk assessment response."""

    previous_score = state["previous_score"]
    new_score = state["new_score"]
    result = RiskAssessmentResult(
        corridor_name=state["corridor_name"],
        previous_score=previous_score,
        new_score=new_score,
        delta=new_score - previous_score,
        reasoning_trace=state["reasoning_trace"],
        signals_processed=len(state.get("signals", [])),
    )
    return {"result": result}


def _build_graph():
    workflow = StateGraph(RiskAgentState)
    workflow.add_node("fetch_corridor_data", fetch_corridor_data)
    workflow.add_node("assess_risk", assess_risk)
    workflow.add_node("update_database", update_database)
    workflow.add_node("format_result", format_result)
    workflow.add_edge(START, "fetch_corridor_data")
    workflow.add_edge("fetch_corridor_data", "assess_risk")
    workflow.add_edge("assess_risk", "update_database")
    workflow.add_edge("update_database", "format_result")
    workflow.add_edge("format_result", END)
    return workflow.compile(checkpointer=MemorySaver())


risk_graph = _build_graph()


async def run_risk_agent(db: Session) -> list[RiskAssessmentResult]:
    """Run one graph per corridor that currently has unprocessed signals."""

    unprocessed_signals = list(
        db.scalars(
            select(GeopoliticalSignal)
            .where(GeopoliticalSignal.processed.is_(False))
            .order_by(GeopoliticalSignal.timestamp.asc())
        )
    )
    grouped_signals: dict[str, list[GeopoliticalSignal]] = defaultdict(list)
    for signal in unprocessed_signals:
        grouped_signals[signal.affected_corridor].append(signal)

    if not grouped_signals:
        return []

    known_corridors = set(
        db.scalars(
            select(CorridorRisk.corridor_name).where(
                CorridorRisk.corridor_name.in_(grouped_signals)
            )
        )
    )
    results: list[RiskAssessmentResult] = []
    for corridor_name in grouped_signals:
        if corridor_name not in known_corridors or not grouped_signals[corridor_name]:
            continue

        final_state = await risk_graph.ainvoke(
            {
                "corridor_name": corridor_name,
                "signals": [],
                "previous_score": 0.0,
                "new_score": 0.0,
                "reasoning_trace": "",
                "db_session": db,
            },
            config={
                "configurable": {
                    "thread_id": f"risk-{corridor_name}-{uuid4()}"
                }
            },
            # Persist the completed assessment without checkpointing a live
            # request task between nodes. The Session channel itself is untracked.
            durability="exit",
        )
        if final_state.get("signals"):
            results.append(final_state["result"])

    return results
