"""LangGraph-powered Strait of Hormuz scenario modeller."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, NotRequired, TypedDict
from uuid import uuid4

from groq import Groq
from langgraph.channels import UntrackedValue
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from models import ScenarioResult

INDIA_CRUDE_IMPORT_MBD = 4.5
HORMUZ_SHARE = 0.42
HORMUZ_DAILY_VOLUME_MBD = 1.89
SPR_TOTAL_DAYS = 9.5
INDIA_REFINERY_CAPACITY_MBD = 5.0
BRENT_BASE_PRICE_USD = 74.0
INDIA_OIL_IMPORT_BILL_ANNUAL_USD_B = 132.0
INDIA_GDP_USD_T = 3.9
OIL_GDP_SENSITIVITY = 0.6

TRIGGER_CORRIDOR = "Strait of Hormuz"
SYSTEM_PROMPT = (
    "You are an energy security analyst briefing India's Petroleum Ministry. "
    "Be precise, urgent where warranted, and always quantify impacts. "
    "Write plain English only, no JSON, no bullet points."
)


@dataclass(frozen=True, slots=True)
class ScenarioOutput:
    scenario_name: str
    closure_percentage: float
    closure_pct_display: int
    import_gap_mbd: float
    import_gap_pct: float
    price_impact_pct: float
    new_brent_price: float
    refinery_stress_score: float
    spr_days_remaining: float
    gdp_impact_pct: float
    unmet_gap_mbd: float
    narrative: str
    computed_at: str


class ScenarioCalculation(TypedDict):
    import_gap_mbd: float
    import_gap_pct: float
    price_impact_pct: float
    new_brent_price: float
    refinery_stress_score: float
    spr_days_remaining: float
    gdp_impact_pct: float
    unmet_gap_mbd: float
    computed_at: NotRequired[str]


class ScenarioAgentState(TypedDict, total=False):
    closure_percentage: float
    scenario_name: str
    calc: ScenarioCalculation
    narrative: str
    db_session: Annotated[Session, UntrackedValue(Session)]


class ScenarioGraphOutput(TypedDict):
    output: ScenarioOutput


def calculate_scenario_impacts(closure_percentage: float) -> ScenarioCalculation:
    """Run the six deterministic Hormuz impact calculations."""

    if not 0.0 <= closure_percentage <= 1.0:
        raise ValueError("closure_percentage must be between 0.0 and 1.0")

    hormuz_disrupted_mbd = HORMUZ_DAILY_VOLUME_MBD * closure_percentage
    import_gap_mbd = hormuz_disrupted_mbd
    import_gap_pct = hormuz_disrupted_mbd / INDIA_CRUDE_IMPORT_MBD

    price_spike_pct = closure_percentage * 0.8
    new_brent_price = BRENT_BASE_PRICE_USD * (1 + price_spike_pct)
    price_impact_pct = price_spike_pct * 100

    domestic_production = 0.8
    available_crude = INDIA_CRUDE_IMPORT_MBD - import_gap_mbd
    total_available = available_crude + domestic_production
    refinery_utilization = min(
        1.0,
        total_available / (INDIA_REFINERY_CAPACITY_MBD * 0.9),
    )
    refinery_stress_score = round(1.0 - refinery_utilization, 4)

    if import_gap_mbd > 0:
        spr_days_remaining = round(
            SPR_TOTAL_DAYS * (1 - closure_percentage * 0.7),
            2,
        )
    else:
        spr_days_remaining = SPR_TOTAL_DAYS

    gdp_impact_pct = round(
        -(price_spike_pct * 10) * OIL_GDP_SENSITIVITY / 10,
        4,
    )

    reroutable_pct = 0.35
    unmet_gap_mbd = round(import_gap_mbd * (1 - reroutable_pct), 4)

    return {
        "import_gap_mbd": import_gap_mbd,
        "import_gap_pct": import_gap_pct,
        "price_impact_pct": price_impact_pct,
        "new_brent_price": new_brent_price,
        "refinery_stress_score": refinery_stress_score,
        "spr_days_remaining": spr_days_remaining,
        "gdp_impact_pct": gdp_impact_pct,
        "unmet_gap_mbd": unmet_gap_mbd,
    }


def build_mock_narrative(
    closure_percentage: float,
    calc: ScenarioCalculation,
) -> str:
    closure_pct_display = int(round(closure_percentage * 100))
    return (
        f"A {closure_pct_display}% closure of the Strait of Hormuz would disrupt "
        f"{calc['import_gap_mbd']:.2f} MBD of India's crude imports \u2014 "
        f"{calc['import_gap_pct']:.1%} of total daily intake. "
        f"Brent crude would spike approximately {calc['price_impact_pct']:.1f}%, "
        f"reaching ${calc['new_brent_price']:.0f}/bbl, placing refinery operations "
        f"under stress (score: {calc['refinery_stress_score']:.2f}/1.0). "
        f"India's Strategic Petroleum Reserve would provide approximately "
        f"{calc['spr_days_remaining']:.1f} days of buffer, with "
        f"{calc['unmet_gap_mbd']:.2f} MBD remaining unmet after maximum rerouting. "
        f"Unresolved within 30 days, this translates to an estimated "
        f"{abs(calc['gdp_impact_pct']):.2f}% GDP drag on India's "
        f"${INDIA_GDP_USD_T:.1f}T economy."
    )


async def calculate_impacts(state: ScenarioAgentState) -> dict:
    return {"calc": calculate_scenario_impacts(state["closure_percentage"])}


async def generate_narrative(state: ScenarioAgentState) -> dict:
    """Generate a four-sentence ministerial note with Groq or mock mode."""

    closure_percentage = state["closure_percentage"]
    closure_pct_display = int(round(closure_percentage * 100))
    calc = state["calc"]
    if not os.getenv("GROQ_API_KEY", "").strip():
        return {"narrative": build_mock_narrative(closure_percentage, calc)}

    user_prompt = f"""Hormuz Partial Closure Scenario
Closure level: {closure_pct_display}%

Computed impacts:
- Import gap: {calc['import_gap_mbd']:.2f} MBD ({calc['import_gap_pct']:.1%} of total imports)
- Brent price spike: +{calc['price_impact_pct']:.1f}% (${calc['new_brent_price']:.0f}/bbl)
- Refinery stress score: {calc['refinery_stress_score']:.2f}/1.0
- SPR cover remaining: {calc['spr_days_remaining']:.1f} days
- GDP drag estimate: {calc['gdp_impact_pct']:.2f}%
- Unmet gap after rerouting: {calc['unmet_gap_mbd']:.2f} MBD

Write exactly 4 sentences as a ministerial briefing note:
Sentence 1: What is happening and immediate scale of disruption.
Sentence 2: Price and refinery impact on domestic operations.
Sentence 3: SPR buffer duration and rerouting shortfall.
Sentence 4: Macro risk and urgency if unresolved in 30 days."""

    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=350,
    )
    narrative = (response.choices[0].message.content or "").strip()
    if not narrative:
        raise ValueError("The scenario narrative model returned empty content")
    return {"narrative": narrative}


async def save_to_db(state: ScenarioAgentState) -> dict:
    """Persist the modelled scenario using the existing ScenarioResult table."""

    db = state["db_session"]
    calc = state["calc"]
    computed_at = datetime.now(UTC)
    record = ScenarioResult(
        scenario_name=state["scenario_name"],
        trigger_corridor=TRIGGER_CORRIDOR,
        closure_percentage=state["closure_percentage"],
        import_gap_mbd=calc["import_gap_mbd"],
        price_impact_pct=calc["price_impact_pct"],
        gdp_impact_pct=calc["gdp_impact_pct"],
        refinery_stress_score=calc["refinery_stress_score"],
        spr_days_remaining=calc["spr_days_remaining"],
        computed_at=computed_at,
    )
    try:
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"calc": {**calc, "computed_at": computed_at.isoformat()}}


async def format_output(state: ScenarioAgentState) -> ScenarioGraphOutput:
    calc = state["calc"]
    output = ScenarioOutput(
        scenario_name=state["scenario_name"],
        closure_percentage=state["closure_percentage"],
        closure_pct_display=int(round(state["closure_percentage"] * 100)),
        import_gap_mbd=calc["import_gap_mbd"],
        import_gap_pct=calc["import_gap_pct"],
        price_impact_pct=calc["price_impact_pct"],
        new_brent_price=calc["new_brent_price"],
        refinery_stress_score=calc["refinery_stress_score"],
        spr_days_remaining=calc["spr_days_remaining"],
        gdp_impact_pct=calc["gdp_impact_pct"],
        unmet_gap_mbd=calc["unmet_gap_mbd"],
        narrative=state["narrative"],
        computed_at=calc["computed_at"],
    )
    return {"output": output}


def _build_graph():
    workflow = StateGraph(
        ScenarioAgentState,
        output_schema=ScenarioGraphOutput,
    )
    workflow.add_node("calculate_impacts", calculate_impacts)
    workflow.add_node("generate_narrative", generate_narrative)
    workflow.add_node("save_to_db", save_to_db)
    workflow.add_node("format_output", format_output)
    workflow.add_edge(START, "calculate_impacts")
    workflow.add_edge("calculate_impacts", "generate_narrative")
    workflow.add_edge("generate_narrative", "save_to_db")
    workflow.add_edge("save_to_db", "format_output")
    workflow.add_edge("format_output", END)
    return workflow.compile(checkpointer=MemorySaver())


scenario_graph = _build_graph()


async def run_scenario_agent(
    db: Session,
    closure_percentage: float,
    scenario_name: str = "Hormuz Partial Closure",
) -> ScenarioOutput:
    """Run and persist a Hormuz closure scenario."""

    if not 0.0 < closure_percentage <= 1.0:
        raise ValueError("closure_percentage must be greater than 0.0 and at most 1.0")
    if not scenario_name.strip():
        raise ValueError("scenario_name must not be empty")

    final_state = await scenario_graph.ainvoke(
        {
            "closure_percentage": closure_percentage,
            "scenario_name": scenario_name.strip(),
            "calc": {},
            "narrative": "",
            "db_session": db,
        },
        config={"configurable": {"thread_id": f"scenario-{uuid4()}"}},
        durability="exit",
    )
    return final_state["output"]


def run_scenario_comparison(
    closure_percentage: float,
    scenario_name: str,
) -> ScenarioOutput:
    """Calculate a comparison row without an LLM call or database write."""

    calc = calculate_scenario_impacts(closure_percentage)
    return ScenarioOutput(
        scenario_name=scenario_name,
        closure_percentage=closure_percentage,
        closure_pct_display=int(round(closure_percentage * 100)),
        import_gap_mbd=calc["import_gap_mbd"],
        import_gap_pct=calc["import_gap_pct"],
        price_impact_pct=calc["price_impact_pct"],
        new_brent_price=calc["new_brent_price"],
        refinery_stress_score=calc["refinery_stress_score"],
        spr_days_remaining=calc["spr_days_remaining"],
        gdp_impact_pct=calc["gdp_impact_pct"],
        unmet_gap_mbd=calc["unmet_gap_mbd"],
        narrative=build_mock_narrative(closure_percentage, calc),
        computed_at=datetime.now(UTC).isoformat(),
    )
