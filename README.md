# EnergyShield

EnergyShield is an AI-driven energy supply chain resilience platform for India.
It currently provides the FastAPI service, SQLite/SQLAlchemy data layer,
realistic seed data, Pydantic schemas, three LangGraph analytical agents, and
a full risk-to-sourcing pipeline with a responsive React intelligence dashboard.

## Run the backend

From the `backend` directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/api/health` to verify the database and table counts.
The SQLite database is created at `backend/energyshield.db` on first startup.

Copy `.env.example` to `.env` and add a Groq API key to enable
`llama-3.3-70b-versatile`.
Without a key, all three agents use deterministic mock behavior.

Key endpoints:

- `POST /api/agents/risk/run` - assess every corridor with unprocessed signals
- `POST /api/agents/scenario/run` - calculate and save a Hormuz scenario
- `POST /api/agents/procurement/run` - rank and save alternative suppliers
- `POST /api/agents/full-pipeline/run` - run risk, scenario, and procurement agents
- `GET /api/scenarios` - return the 10 most recent saved scenarios
- `GET /api/scenarios/compare` - compare closures without saving or using an LLM
- `GET /api/procurement/recommendations` - list or filter saved recommendations
- `GET /api/corridors` - list corridor risks from highest to lowest
- `GET /api/signals` - list geopolitical signals newest first
- `GET /api/health` - report database table counts

To seed without starting the API, run:

```powershell
python seed.py
```

The seed operation is idempotent: it only populates an empty seed table.

## Run the frontend

Keep the backend running on port `8000`, then from the `frontend` directory:

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` requests to the FastAPI
service. Use `npm run build` to create a production bundle in `frontend/dist`.

## Current scope

- Five energy corridor risk records
- Eight representative crude suppliers aligned to India's import mix
- Ten mock geopolitical signals
- LangGraph geopolitical risk assessment with rerunnable demo signals
- Deterministic Hormuz impact modelling with optional AI ministerial briefings
- Weighted supplier scoring and Groq-assisted procurement reasoning
- Full three-agent demo pipeline
- Responsive Vite, React, Tailwind CSS, and Recharts intelligence dashboard
- Live corridor risk, scenario comparison, procurement ranking, and reasoning views
