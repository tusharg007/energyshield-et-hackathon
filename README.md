# EnergyShield 🛡️
### AI-Driven Energy Supply Chain Resilience for Import-Dependent Economies

> Built for ET AI Hackathon 2.0 — Problem Statement #2
> by Tushar Ghosh, IIIT Nagpur (B.Tech CSE — Data Science & Analytics)

---

## 🔴 The Problem

India imports 88% of its crude oil. 40-45% of that volume
transits the Strait of Hormuz — a single chokepoint whose
closure would drain India's Strategic Petroleum Reserve
in under 10 days. The 2025 US-Iran standoff sent Brent
crude up 8% in a single trading session. India had no
automated intelligence layer to respond.

Traditional supply chain tools cannot:
- Model geopolitical disruption scenarios in real time
- Dynamically rank alternative procurement corridors
- Explain their recommendations to decision-makers

**EnergyShield is that missing intelligence layer.**

---

## 🧠 What It Does

A single button press runs three LangGraph agents in sequence:

### Agent 1 — Geopolitical Risk Agent
Ingests geopolitical signals (sanctions, naval activity,
weather, piracy) and updates live risk scores for 5
major oil import corridors. Powered by Groq LLaMA-3.3-70B,
each corridor gets a plain-English reasoning trace
explaining exactly why its risk score changed.

### Agent 2 — Hormuz Scenario Modeller  
Given a closure percentage (10-90%), computes cascading
impacts deterministically using real India energy figures:
- Import gap (MBD)
- Brent crude price spike
- Refinery stress score
- SPR days remaining
- GDP drag estimate
- Unmet gap after maximum rerouting

All assumptions are explicit and testable — no black box.

### Agent 3 — Procurement Orchestrator
Filters out disrupted (Hormuz) suppliers, then ranks
all available alternatives on a 4-dimension composite score:

| Dimension | Weight | Logic |
|-----------|--------|-------|
| Price | 25% | Lower $/bbl = higher score |
| Lead Time | 25% | Shorter days = higher score |
| Grade Compatibility | 30% | Refinery match % |
| Corridor Safety | 20% | 1 - current_risk_score |

Top 3 suppliers get a per-supplier LLM reasoning trace
explaining the ranking decision with specific numbers.

---

## 🏗️ Architecture

```text
Geopolitical Signals (mock → real API-ready)
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ Geopolitical Risk Agent                                    │
│ LangGraph 4-node graph · Groq LLaMA-3.3-70B               │
└────────────────────────────┬───────────────────────────────┘
                             │ corridor risk scores
                             ▼
┌────────────────────────────────────────────────────────────┐
│ SQLite Database · SQLAlchemy ORM                           │
│ corridors · suppliers · signals · scenarios · recs         │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Hormuz Scenario Agent                                      │
│ LangGraph 4-node graph · deterministic model · Groq brief  │
└────────────────────────────┬───────────────────────────────┘
                             │ import_gap_mbd
                             ▼
┌────────────────────────────────────────────────────────────┐
│ Procurement Orchestrator                                   │
│ LangGraph 5-node graph · composite scorer · Groq rationale │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ FastAPI REST Layer                                         │
│ POST /api/agents/full-pipeline/run                         │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ React Dashboard · Vite · Tailwind · Recharts               │
│ Risk · Scenario · Procurement · Agent Reasoning Traces     │
└────────────────────────────────────────────────────────────┘
```

---

## 🌐 Live Demo

- **Frontend:** https://energyshield-frontend.onrender.com
- **Backend API:** https://energyshield-backend.onrender.com
- **API Docs:** https://energyshield-backend.onrender.com/docs
- **Health Check:** https://energyshield-backend.onrender.com/api/health
- **GitHub:** https://github.com/tusharg007/energyshield-et-hackathon

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API key (free at console.groq.com)

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
python seed.py
uvicorn main:app --reload
# Backend: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Dashboard: http://localhost:5173
```

### Run the Pipeline
1. Open http://localhost:5173
2. Set Hormuz closure level (try 40%)
3. Click "Run Full Intelligence Pipeline"
4. Watch 3 agents execute in sequence
5. Read the reasoning traces

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | DB status + table counts |
| GET | /api/corridors | All corridor risk scores |
| GET | /api/signals | All geopolitical signals |
| POST | /api/agents/risk/run | Run Risk Agent only |
| POST | /api/agents/scenario/run | Run Scenario Agent only |
| POST | /api/agents/procurement/run | Run Procurement Agent only |
| POST | /api/agents/full-pipeline/run | **Hero endpoint — all 3 agents** |
| GET | /api/scenarios/compare | Multi-closure comparison |
| GET | /api/procurement/recommendations | Saved recommendations |

### Hero Endpoint Example
```bash
curl -X POST http://localhost:8000/api/agents/full-pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"closure_percentage": 0.40, "scenario_name": "Hormuz 40% Closure"}'
```

Returns:
```json
{
  "risk_assessments": [...],     // 5 corridors with reasoning
  "scenario": {...},             // 6 impact metrics + narrative  
  "procurement_recommendations": [...]  // ranked suppliers + rationale
}
```

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| corridor_risks | 5 corridors with live risk scores |
| suppliers | 8 suppliers with grade/price/lead time |
| geopolitical_signals | Mock signal feed (10 signals) |
| scenario_results | Saved Hormuz closure computations |
| procurement_recommendations | Ranked supplier outputs |

---

## 🧱 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Agent Orchestration | LangGraph | 1.2.9 |
| LLM | Groq — LLaMA-3.3-70B-Versatile | Latest |
| Backend Framework | FastAPI | 0.139.0 |
| ORM | SQLAlchemy | 2.0.51 |
| Database | SQLite | — |
| Frontend | React + Vite | 18 + 8.x |
| Styling | Tailwind CSS | 4.x |
| Charts | Recharts | Latest |
| Deployment | Render | — |

---

## 🌍 Data Strategy

| Data Type | Current | Production-Ready Swap |
|-----------|---------|----------------------|
| Geopolitical signals | Simulated (realistic) | NewsAPI, GDELT |
| AIS vessel tracking | Implicit in signals | MarineTraffic API |
| Sanctions data | Signal headlines | OFAC registry feed |
| Brent price | Hardcoded $74 baseline | EIA / Bloomberg API |
| Supplier prices | Realistic seed data | Argus, Platts feeds |

All simulated data is schema-compatible with real feeds.
Switching to live data = changing one data ingestion function.

---

## 📊 Domain Constants Used

```python
INDIA_CRUDE_IMPORT_MBD = 4.5      # Million barrels/day
HORMUZ_SHARE = 0.42                # 42% of imports via Hormuz  
SPR_TOTAL_DAYS = 9.5               # Strategic reserve cover
BRENT_BASE_PRICE_USD = 74.0        # Baseline (July 2026)
INDIA_GDP_USD_T = 3.9              # Trillion USD
OIL_GDP_SENSITIVITY = 0.6          # % GDP per 10% oil price rise
```

All figures sourced from public data:
MoPNG, IEA, McKinsey Energy Practice, PPAC India.

---

## 🔮 Future Scope

- Live AIS vessel tracking integration (MarineTraffic API)
- Real-time news ingestion (GDELT + NewsAPI)
- Multi-country extension (Bangladesh, Sri Lanka, Pakistan)
- SPR drawdown optimizer agent
- WebSocket live updates (replace polling)
- Mobile-responsive dashboard

---

## 📁 Project Structure

```text
energyshield/
├── backend/
│   ├── main.py                 # FastAPI app + all endpoints
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models.py               # ORM models (5 tables)
│   ├── schemas.py              # Pydantic schemas
│   ├── seed.py                 # DB initialization + seed data
│   ├── agents/
│   │   ├── risk_agent.py       # Geopolitical Risk Agent
│   │   ├── scenario_agent.py   # Hormuz Scenario Modeller
│   │   └── procurement_agent.py # Procurement Orchestrator
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main app + state management
│   │   ├── config.js           # API base URL config
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── ControlPanel.jsx
│   │       ├── RiskCorridorPanel.jsx
│   │       ├── ScenarioPanel.jsx
│   │       ├── ProcurementTable.jsx
│   │       └── ReasoningTrace.jsx
│   ├── package.json
│   └── vite.config.js
├── render.yaml                 # Render deployment config
├── SUBMISSION.md               # Hackathon submission document
└── README.md                   # This file
```

---

## 👤 Author

**Tushar Ghosh**
B.Tech CSE (Data Science & Analytics) — IIIT Nagpur
GitHub: github.com/tusharg007

*Built for ET AI Hackathon 2.0 — Economic Times*
*Problem Statement #2: AI-Driven Energy Supply Chain Resilience*

---

## 🏆 Judging Criteria Alignment

EnergyShield is designed around the complete decision cycle in the problem statement: detect a geopolitical disruption, quantify its consequences for India, and convert the result into an executable procurement response. The following mapping is grounded in features that judges can inspect in the live application, API responses, database records, and source code.

| Judging dimension | EnergyShield's evidence | Judge-visible proof |
|-------------------|-------------------------|---------------------|
| Relevance to Problem Statement | Models India's dependence on imported crude and exposure to the Strait of Hormuz from signal detection through supplier rerouting | Set a closure level and run the full pipeline |
| Innovation & Creativity | Cascading multi-agent intelligence, deterministic scenario mathematics, dynamic supplier scoring, and decision-level explanations | Risk scores directly influence downstream procurement rankings |
| Technical Implementation | Three LangGraph workflows, Groq LLaMA-3.3-70B, FastAPI, Pydantic validation, SQLAlchemy persistence, React, and Recharts | Inspect `/docs`, reasoning traces, saved scenarios, and source code |
| Impact & Scalability | Converts hours of fragmented analysis into one repeatable flow and provides a clear path from simulated feeds to live national-scale data | Compare 20%, 40%, 60%, and 80% closure outcomes |
| Presentation & Clarity | Single-click demo, six decision metrics, comparison chart, ranked procurement table, and plain-English briefings | Complete narrative from crisis input to recommended action |
| Business Viability | Supports refinery procurement, ministry coordination, strategic-reserve planning, and auditable decision governance | Recommendations include supplier, score breakdown, volume, and rationale |

### 1. Relevance to Problem Statement

The chosen problem is not simply to predict an oil-price shock; it is to make an import-dependent energy supply chain more resilient. EnergyShield addresses that requirement end to end:

| Problem requirement | EnergyShield response |
|---------------------|-----------------------|
| Detect emerging threats to supply routes | The Geopolitical Risk Agent groups new sanctions, military, piracy, insurance, congestion, weather, and infrastructure signals by corridor and updates the corridor's current risk score. |
| Model the consequences of disruption | The Hormuz Scenario Modeller accepts any closure level from 1% to 100% and calculates import loss, price impact, refinery stress, SPR cover, GDP drag, and the residual gap after rerouting. |
| Generate actionable alternatives | The Procurement Orchestrator removes suppliers that depend on the disrupted corridor, scores every viable alternative, ranks them, allocates the gap across the top three, and explains each recommendation. |
| Support decisions under time pressure | `POST /api/agents/full-pipeline/run` runs all three stages sequentially from one request and returns one decision package. |
| Make outputs trustworthy | Every risk change, scenario consequence, and top-three supplier recommendation includes a plain-English reasoning trace. |

The solution is India-specific rather than a generic supply-chain chatbot. Its model uses 4.5 MBD of crude imports, a 42% Hormuz share, 9.5 days of SPR cover, a $74/bbl Brent baseline, refinery constraints, and supplier-grade compatibility. The output is expressed in procurement units—MBD, dollars per barrel, lead time, crude grade, route safety, and allocated volume—so it can support an actual sourcing conversation.

**Why this matters:** conventional alerting tools stop at “risk is rising.” EnergyShield continues from the alert to quantified national exposure and then to the suppliers and volumes required to respond.

### 2. Innovation & Creativity

#### Cascading intelligence instead of isolated AI outputs

EnergyShield's key innovation is the dependency between agents. New geopolitical signals alter corridor risk; corridor risk changes the safety component of supplier scores; supplier scores change the final sourcing order. This creates a reactive intelligence chain rather than three disconnected demos.

#### Hybrid AI and deterministic decision modelling

The system uses each technique where it is strongest:

- Groq-hosted LLaMA-3.3-70B interprets unstructured geopolitical headlines and writes decision-focused explanations.
- Explicit formulas compute import gaps, price shocks, refinery stress, SPR drawdown, GDP exposure, and rerouting shortfalls.
- A transparent weighted model ranks suppliers by price (25%), lead time (25%), refinery compatibility (30%), and corridor safety (20%).

This separation avoids asking an LLM to invent critical numerical outcomes. Quantitative impacts remain reproducible, while AI adds contextual interpretation and communication.

#### Explainability as a first-class output

Reasoning is stored and displayed, not hidden in logs. The Risk Agent references individual signal headlines; the Scenario Agent converts computed metrics into a four-sentence ministerial note; and the Procurement Agent produces supplier-specific rationales using the exact price, time, compatibility, and safety scores shown in the table. A judge can therefore follow the chain from evidence to score to action.

#### Designed for repeatable demonstrations and operational evolution

When the seeded signal batch has been processed, the demo endpoint resets its processed state so the complete intelligence cycle remains reproducible. In production, that mechanism is replaced by continuous ingestion while the downstream agents, schemas, and UI contract remain unchanged.

### 3. Technical Implementation

#### Agent orchestration

Each agent is an explicit LangGraph state machine with typed state, named nodes, linear edges, asynchronous invocation, and a `MemorySaver` checkpointer:

- [Risk Agent](backend/agents/risk_agent.py): `fetch_corridor_data → assess_risk → update_database → format_result`
- [Scenario Agent](backend/agents/scenario_agent.py): `calculate_impacts → generate_narrative → save_to_db → format_output`
- [Procurement Agent](backend/agents/procurement_agent.py): `fetch_and_filter_suppliers → score_and_rank → generate_top3_reasoning → save_recommendations → format_output`

This makes the system inspectable and extensible. A production team can add human approval, live-data validation, sanctions screening, or an SPR optimization node without rewriting the full pipeline.

#### Reliable AI integration

- Groq uses `llama-3.3-70b-versatile` with low temperatures for consistent analytical output.
- The Risk Agent requests structured JSON, validates the score range and reasoning, and falls back to a deterministic severity calculation if parsing fails.
- All three agents support mock mode when `GROQ_API_KEY` is unavailable, keeping the demo functional and the calculations testable.
- LLMs explain or interpret decisions; they do not replace the deterministic impact and procurement formulas.

#### API and data integrity

- [FastAPI](backend/main.py) exposes individual-agent endpoints, read endpoints, scenario comparison, health checks, and the hero pipeline endpoint.
- [Pydantic schemas](backend/schemas.py) constrain closure percentages, scores, prices, lead times, identifiers, and scenario names before they reach agent logic.
- [SQLAlchemy models](backend/models.py) persist five connected domains: corridors, suppliers, geopolitical signals, scenarios, and procurement recommendations.
- Database mutations use commit/rollback handling. Risk-score updates and signal-processing flags are committed together, and procurement recommendations retain the scenario and supplier IDs that produced them.
- The scenario comparison endpoint is deterministic and read-only, making sensitivity analysis fast and inexpensive.

#### Frontend and deployment

The React interface separates control, risk, scenario, procurement, and reasoning concerns into focused components. It provides loading and error states, responsive layouts, six impact cards, a Recharts comparison view, score-breakdown bars, and collapsible agent traces. `VITE_API_URL` decouples the frontend from the backend, while Render configuration deploys the FastAPI service and Vite static build independently.

### 4. Impact & Scalability

#### Meaningful operational impact

EnergyShield compresses a fragmented workflow—monitoring news, estimating shortages, checking reserves, comparing routes, screening suppliers, and preparing a briefing—into one repeatable decision flow. Its result is not only a warning; it contains:

- the corridors whose risk changed and the signals responsible;
- the volume of crude at risk and its share of national imports;
- the expected price, refinery, reserve, and GDP consequences;
- the remaining shortage after rerouting;
- a ranked list of alternative suppliers with proposed MBD allocation; and
- an auditable explanation for every major recommendation.

That output is useful to refinery procurement teams, corporate risk units, the Ministry of Petroleum and Natural Gas, strategic-reserve planners, and financial-policy stakeholders who need a shared operating picture during a disruption.

#### Scale path

| Layer | Hackathon implementation | Scale-up path |
|-------|--------------------------|---------------|
| Signals | 10 realistic seeded events | Continuous GDELT, NewsAPI, UKMTO, OFAC, weather, insurance, and AIS ingestion |
| Geography | Five oil corridors focused on India | Add corridor, supplier, refinery, and country records without changing the agent contract |
| Storage | SQLite for a portable demonstration | PostgreSQL with managed backups, audit retention, and time-series partitions |
| Execution | Synchronous hero endpoint | Background jobs, event queues, parallel corridor assessment, retries, and WebSocket updates |
| Governance | Stored reasoning and model outputs | Human approval gates, role-based access, model/version tracking, and policy thresholds |
| Optimization | Transparent weighted ranking | Capacity constraints, contract terms, freight rates, sanctions exposure, and multi-objective optimization |

The current simulation is clearly labelled. Its value is that the database and API shapes already match the fields expected from real feeds, so moving from seeded to live intelligence changes the ingestion layer rather than the entire product.

### 5. Presentation & Clarity

The demo is structured around the decision-maker's natural questions:

1. **What changed?** Live corridor cards show severity, score movement, signal count, and the Risk Agent's explanation.
2. **What does it mean for India?** The Scenario Panel presents six consequences and a concise ministerial briefing.
3. **What should we do now?** The Procurement Table ranks viable alternatives, exposes the four score components, proposes volume, and explains the top three choices.
4. **How does severity change the outcome?** The comparison chart shows the effect of 20%, 40%, 60%, and 80% Hormuz closures.
5. **Can the recommendation be defended?** The Reasoning Trace panel exposes the evidence and logic from all three agents.

The single-click pipeline gives the pitch a clear beginning, middle, and end: crisis input → intelligence processing → quantified impact → procurement action. The live deployment, Swagger documentation, README, project document, seeded data, and mock-mode fallback also ensure judges can evaluate the system even if an external model service is temporarily unavailable.

### 6. Business Viability

#### Target users and decisions

| User | Decision supported |
|------|--------------------|
| Indian refinery procurement director | Which non-disrupted suppliers to contact, in what order, and for what volume |
| Corporate risk and trading desk | Which corridor and market indicators require escalation |
| Ministry of Petroleum and Natural Gas | Expected national shortfall, refinery stress, and urgency of intervention |
| Strategic Petroleum Reserve operator | How rapidly reserve cover may deteriorate under each closure level |
| Ministry of Finance / economic policy team | Potential price and GDP exposure if disruption persists |

#### Practical adoption model

- **MVP:** the deployed system demonstrates the full workflow using transparent assumptions and simulated but realistic signals.
- **Pilot:** connect one live news feed, one AIS provider, refinery configuration data, and supplier price/contract feeds for a participating refinery.
- **Operational product:** add continuous monitoring, alert thresholds, user roles, approval workflows, enterprise databases, audit logs, and integration with procurement/ERP systems.
- **Expansion:** reuse the corridor-supplier model for LNG, coal, fertilizers, or other import-dependent economies exposed to maritime chokepoints.

The commercial value comes from faster disruption response, reduced emergency spot-buying exposure, better use of strategic reserves, and a defensible record of why a sourcing decision was made. A realistic delivery model is a subscription intelligence platform for refiners and traders, with institution-wide deployments for ministries and energy-security agencies.

#### Why EnergyShield is viable

EnergyShield does not require an organization to trust an opaque autonomous buyer. It operates as a decision-support layer: calculations and weights are visible, the AI's role is bounded, recommendations are reviewable, and human procurement authority remains intact. That lowers adoption risk while still delivering immediate analytical value.

> **Shortlisting case:** EnergyShield combines direct problem relevance, an original cascading-agent design, working full-stack implementation, measurable national-scale impact, a clear live demonstration, and a credible path from hackathon prototype to operational decision-support product.
