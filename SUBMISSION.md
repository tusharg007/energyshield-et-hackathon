# EnergyShield — AI-Driven Energy Supply Chain Resilience
## ET AI Hackathon 2.0 | Problem Statement #2

### Team
- Name: Tushar Ghosh
- Institution: IIIT Nagpur (B.Tech CSE — Data Science & Analytics)
- GitHub: github.com/tusharg007

---

### Problem Understanding
India sources 88% of crude oil from imports, with 40-45%
transiting the Strait of Hormuz. Traditional supply chain tools
cannot model geopolitical disruptions in real time or generate
executable rerouting recommendations. The 2025 US-Iran standoff
sent Brent crude up 8% in a single session — India had no
automated intelligence layer to respond.

### Solution: EnergyShield
An agentic intelligence platform that converts geopolitical
signals into procurement actions in minutes, not weeks.

Three LangGraph agents run in sequence via a single API call:
1. Geopolitical Risk Agent — scores corridor disruption
   probability from live signals
2. Scenario Modeller — computes cascading Hormuz closure
   impacts deterministically
3. Procurement Orchestrator — ranks alternative suppliers
   by composite score with explicit reasoning

### Architecture
Signal Feed → Risk Agent (LangGraph + Groq LLaMA-3.3-70B)
           → SQL DB (SQLite/SQLAlchemy)
           → Scenario Agent (deterministic math model)
           → Procurement Agent (composite scorer + LLM reasoning)
           → FastAPI REST Layer
           → React Dashboard (Vite + Tailwind + Recharts)

### Innovation
1. Real-time cascading intelligence: geopolitical signal
   changes update corridor risk scores, which feed directly
   into procurement re-ranking — the entire chain updates
   on each pipeline run.

2. Transparent reasoning: every agent decision includes a
   plain-English explanation. Judges/procurement directors
   can read exactly why Russia ranks #1 over Angola —
   referencing specific scores and corridor conditions.

3. Explicit assumption architecture: the scenario model's
   constants (88% import dependency, 9.5 SPR days,
   $74 Brent baseline) are all documented and testable —
   judges can challenge any number and we can defend it.

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph 1.2.9 |
| LLM | Groq — LLaMA-3.3-70B-Versatile |
| Backend | FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy ORM |
| Frontend | React 18 + Vite + Tailwind CSS |
| Charts | Recharts |
| Deployment | Render |

### Judging Criteria Mapping
| Criterion | How EnergyShield addresses it |
|-----------|-------------------------------|
| Innovation (25%) | Cascading multi-agent pipeline; transparent reasoning traces; real-time risk-to-recommendation flow |
| Business Impact (25%) | Directly addresses India's $132B/year oil import vulnerability; SPR optimization; executable procurement output |
| Technical Excellence (20%) | LangGraph agent architecture; composite scoring with 4 weighted dimensions; deterministic scenario model with explicit assumptions |
| Scalability (15%) | Real AIS/news API integration is schema-ready; multi-country extension requires only new corridor/supplier rows |
| User Experience (15%) | Single-click full pipeline; ministerial briefing note; collapsible reasoning traces; comparison bar chart |

### Data Strategy
Geopolitical signals: simulated (schema-compatible with
NewsAPI, GDELT, OFAC sanctions registry)
Supplier data: realistic India import mix (Iraq 22%,
Saudi 18%, Russia 15%, UAE 10%)
Corridor risk factors: based on publicly reported
threat assessments (Lloyd's, UKMTO, CERT)
All simulation clearly labeled — real API integration
is one environment variable swap.

### Live Demo
- Local: http://localhost:5173
- Deployed: [Render URL after deployment]
- GitHub: https://github.com/tusharg007/energyshield-et-hackathon
