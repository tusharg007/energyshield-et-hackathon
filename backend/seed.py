"""Idempotent seed data for the EnergyShield SQLite database."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import CorridorRisk, GeopoliticalSignal, Supplier


# Reference shares for India's representative crude import mix. The current
# Supplier schema intentionally has no share column, so these remain metadata.
INDIA_IMPORT_MIX_PCT = {
    "Saudi Arabia": 18,
    "Iraq": 22,
    "United Arab Emirates": 10,
    "Russia": 15,
    "United States": 8,
    "Nigeria": 9,
    "Kazakhstan": 6,
    "Angola": 12,
}


CORRIDORS = [
    {
        "corridor_name": "Strait of Hormuz",
        "region": "Persian Gulf",
        "base_risk_score": 0.72,
        "current_risk_score": 0.78,
        "risk_factors": {
            "military_tension": "high",
            "sanctions_exposure": "high",
            "chokepoint_concentration": "critical",
        },
    },
    {
        "corridor_name": "Red Sea",
        "region": "Middle East / North-East Africa",
        "base_risk_score": 0.68,
        "current_risk_score": 0.74,
        "risk_factors": {
            "drone_attacks": "high",
            "insurance_cost": "elevated",
            "rerouting_frequency": "high",
        },
    },
    {
        "corridor_name": "Cape of Good Hope",
        "region": "Southern Africa",
        "base_risk_score": 0.21,
        "current_risk_score": 0.27,
        "risk_factors": {
            "weather": "moderate",
            "voyage_extension": "high",
            "security": "low",
        },
    },
    {
        "corridor_name": "Suez Canal",
        "region": "Egypt / Eastern Mediterranean",
        "base_risk_score": 0.45,
        "current_risk_score": 0.51,
        "risk_factors": {
            "regional_spillover": "elevated",
            "congestion": "moderate",
            "physical_blockage": "moderate",
        },
    },
    {
        "corridor_name": "Malacca Strait",
        "region": "South-East Asia",
        "base_risk_score": 0.31,
        "current_risk_score": 0.34,
        "risk_factors": {
            "congestion": "high",
            "piracy": "moderate",
            "weather": "moderate",
        },
    },
]


SUPPLIERS = [
    {
        "name": "Saudi Arabia — Arab Light",
        "country": "Saudi Arabia",
        "region": "Middle East",
        "crude_grade": "Medium Sour",
        "base_price_usd_bbl": 83.40,
        "availability_score": 0.91,
        "primary_corridor": "Strait of Hormuz",
        "refinery_compatibility": 0.96,
        "lead_time_days": 12,
        "geopolitical_safety_score": 0.67,
    },
    {
        "name": "Iraq — Basra Heavy",
        "country": "Iraq",
        "region": "Middle East",
        "crude_grade": "Heavy Sour",
        "base_price_usd_bbl": 79.10,
        "availability_score": 0.88,
        "primary_corridor": "Strait of Hormuz",
        "refinery_compatibility": 0.94,
        "lead_time_days": 11,
        "geopolitical_safety_score": 0.55,
    },
    {
        "name": "UAE — Murban",
        "country": "United Arab Emirates",
        "region": "Middle East",
        "crude_grade": "Light Sour",
        "base_price_usd_bbl": 84.70,
        "availability_score": 0.82,
        "primary_corridor": "Strait of Hormuz",
        "refinery_compatibility": 0.91,
        "lead_time_days": 10,
        "geopolitical_safety_score": 0.76,
    },
    {
        "name": "Russia — Urals",
        "country": "Russia",
        "region": "Eurasia",
        "crude_grade": "Medium Sour",
        "base_price_usd_bbl": 76.80,
        "availability_score": 0.86,
        "primary_corridor": "Suez Canal",
        "refinery_compatibility": 0.93,
        "lead_time_days": 24,
        "geopolitical_safety_score": 0.42,
    },
    {
        "name": "USA — WTI",
        "country": "United States",
        "region": "North America",
        "crude_grade": "Light Sweet",
        "base_price_usd_bbl": 82.90,
        "availability_score": 0.78,
        "primary_corridor": "Cape of Good Hope",
        "refinery_compatibility": 0.84,
        "lead_time_days": 35,
        "geopolitical_safety_score": 0.91,
    },
    {
        "name": "Nigeria — Bonny Light",
        "country": "Nigeria",
        "region": "West Africa",
        "crude_grade": "Light Sweet",
        "base_price_usd_bbl": 85.20,
        "availability_score": 0.64,
        "primary_corridor": "Cape of Good Hope",
        "refinery_compatibility": 0.88,
        "lead_time_days": 26,
        "geopolitical_safety_score": 0.59,
    },
    {
        "name": "Kazakhstan — CPC Blend",
        "country": "Kazakhstan",
        "region": "Central Asia",
        "crude_grade": "Light Sour",
        "base_price_usd_bbl": 81.60,
        "availability_score": 0.69,
        "primary_corridor": "Suez Canal",
        "refinery_compatibility": 0.86,
        "lead_time_days": 27,
        "geopolitical_safety_score": 0.71,
    },
    {
        "name": "Angola — Girassol",
        "country": "Angola",
        "region": "Southern Africa",
        "crude_grade": "Light Sweet",
        "base_price_usd_bbl": 83.80,
        "availability_score": 0.66,
        "primary_corridor": "Cape of Good Hope",
        "refinery_compatibility": 0.87,
        "lead_time_days": 23,
        "geopolitical_safety_score": 0.73,
    },
]


def signal_rows() -> list[dict]:
    now = datetime.now(UTC)
    return [
        {
            "signal_type": "sanctions",
            "source": "Reuters Energy Desk",
            "headline": "US sanctions target Iranian oil exports, tanker availability tightens in Gulf",
            "affected_corridor": "Strait of Hormuz",
            "severity": 0.82,
            "timestamp": now - timedelta(hours=2),
            "processed": False,
        },
        {
            "signal_type": "maritime_security",
            "source": "UKMTO Advisory",
            "headline": "Commercial vessel reports drone activity near Bab el-Mandeb transit lane",
            "affected_corridor": "Red Sea",
            "severity": 0.88,
            "timestamp": now - timedelta(hours=5),
            "processed": False,
        },
        {
            "signal_type": "insurance",
            "source": "Lloyd's Market Bulletin",
            "headline": "War-risk premiums rise for tankers crossing the southern Red Sea",
            "affected_corridor": "Red Sea",
            "severity": 0.71,
            "timestamp": now - timedelta(hours=9),
            "processed": False,
        },
        {
            "signal_type": "military",
            "source": "Gulf Maritime Monitor",
            "headline": "Naval exercises announced near Strait of Hormuz shipping channels",
            "affected_corridor": "Strait of Hormuz",
            "severity": 0.76,
            "timestamp": now - timedelta(hours=14),
            "processed": False,
        },
        {
            "signal_type": "congestion",
            "source": "Suez Canal Authority",
            "headline": "Convoy delays increase as rerouted vessels return to Suez approaches",
            "affected_corridor": "Suez Canal",
            "severity": 0.49,
            "timestamp": now - timedelta(days=1),
            "processed": False,
        },
        {
            "signal_type": "weather",
            "source": "South African Weather Service",
            "headline": "Severe swells forecast along Cape tanker route for the next 72 hours",
            "affected_corridor": "Cape of Good Hope",
            "severity": 0.44,
            "timestamp": now - timedelta(days=1, hours=6),
            "processed": False,
        },
        {
            "signal_type": "piracy",
            "source": "IMB Piracy Reporting Centre",
            "headline": "Boarding attempt reported east of Singapore in congested tanker lane",
            "affected_corridor": "Malacca Strait",
            "severity": 0.57,
            "timestamp": now - timedelta(days=2),
            "processed": False,
        },
        {
            "signal_type": "infrastructure",
            "source": "Canal Operations Notice",
            "headline": "Suez maintenance window reduces southbound convoy capacity temporarily",
            "affected_corridor": "Suez Canal",
            "severity": 0.38,
            "timestamp": now - timedelta(days=2, hours=8),
            "processed": False,
        },
        {
            "signal_type": "diplomatic",
            "source": "Regional Security Brief",
            "headline": "Gulf states begin emergency talks following escalation in regional tensions",
            "affected_corridor": "Strait of Hormuz",
            "severity": 0.69,
            "timestamp": now - timedelta(days=3),
            "processed": False,
        },
        {
            "signal_type": "port_disruption",
            "source": "Asian Port Intelligence",
            "headline": "Port congestion near Singapore extends crude tanker turnaround times",
            "affected_corridor": "Malacca Strait",
            "severity": 0.52,
            "timestamp": now - timedelta(days=3, hours=12),
            "processed": False,
        },
    ]


def _is_empty(db: Session, model: type) -> bool:
    return db.scalar(select(func.count()).select_from(model)) == 0


def seed_database(db: Session) -> None:
    """Insert each seed collection only when its table is empty."""

    if _is_empty(db, CorridorRisk):
        db.add_all(CorridorRisk(**row) for row in CORRIDORS)

    if _is_empty(db, Supplier):
        db.add_all(Supplier(**row) for row in SUPPLIERS)

    if _is_empty(db, GeopoliticalSignal):
        db.add_all(GeopoliticalSignal(**row) for row in signal_rows())

    db.commit()


def initialize_and_seed() -> None:
    """Create all tables and seed the database."""

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)


if __name__ == "__main__":
    initialize_and_seed()
    print("EnergyShield database initialized and seeded.")
