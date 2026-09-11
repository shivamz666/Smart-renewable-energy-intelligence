"""
Smart Renewable Energy Intelligence Platform — FastAPI Backend
Agentic AI Decision Support for Solar-Wind Hybrid Parks (Kutch & Banaskantha)

SAFETY NOTICE: This is a DECISION-SUPPORT system only.
The AI provides recommendations. Human operators make all final decisions.
No physical equipment is controlled by this software.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os

from .orchestrator.orchestrator import orchestrator
from .granite.granite_client import granite_client
from .config.settings import settings

app = FastAPI(
    title=settings.APP_TITLE,
    description=(
        "Agentic AI Decision Support Platform for Renewable Energy Parks. "
        "This is a DECISION-SUPPORT system. Human operators approve all recommendations. "
        "DATA: DEMO / SIMULATED"
    ),
    version=settings.APP_VERSION,
)

# CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response models ────────────────────────────────────────────────

class HumanDecisionRequest(BaseModel):
    rec_id: str
    decision: str           # APPROVED / REJECTED / IGNORED
    note: Optional[str] = None


class ChatRequest(BaseModel):
    message: str


class ScenarioRequest(BaseModel):
    scenario: str           # underperformance / high_generation / weather_drop / normal


# ─── API routes ───────────────────────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "platform": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "data_source": "DEMO / SIMULATED DATA",
        "granite_mode": "mock" if settings.USE_MOCK_GRANITE else "live",
        "safety_notice": (
            "This is a DECISION-SUPPORT system. "
            "AI provides recommendations only. "
            "Human operators must approve all actions. "
            "No physical equipment is controlled."
        ),
    }


@app.get("/api/dashboard")
def get_dashboard():
    """
    Main dashboard endpoint — runs all agents and returns unified state.
    DATA: DEMO / SIMULATED
    """
    try:
        state = orchestrator.run()
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/assets/solar")
def get_solar_assets(location: Optional[str] = None):
    from .data.simulator import simulator
    assets = simulator.get_solar_assets()
    if location:
        assets = [a for a in assets if a.location == location]
    return {"assets": [a.dict() for a in assets], "data_source": "DEMO / SIMULATED DATA"}


@app.get("/api/assets/wind")
def get_wind_assets(location: Optional[str] = None):
    from .data.simulator import simulator
    assets = simulator.get_wind_assets()
    if location:
        assets = [a for a in assets if a.location == location]
    return {"assets": [a.dict() for a in assets], "data_source": "DEMO / SIMULATED DATA"}


@app.get("/api/weather")
def get_weather():
    from .data.simulator import simulator
    return {
        "kutch": simulator.get_weather("kutch").dict(),
        "banaskantha": simulator.get_weather("banaskantha").dict(),
        "data_source": "DEMO / SIMULATED DATA",
    }


@app.get("/api/generation/historical")
def get_historical_generation(hours: int = Query(24, ge=1, le=168)):
    """Returns historical generation data. DATA: DEMO / SIMULATED"""
    return {
        "data": orchestrator.get_historical_generation(hours),
        "hours": hours,
        "data_source": "DEMO / SIMULATED DATA",
    }


@app.get("/api/generation/forecast")
def get_forecast(hours: int = Query(6, ge=1, le=48)):
    from .data.simulator import simulator
    from .agents.forecasting_agent import ForecastingAgent
    agent = ForecastingAgent()
    kw = simulator.get_weather("kutch")
    bw = simulator.get_weather("banaskantha")
    if hours <= 6:
        fc = agent.generate_6h_forecast(kw, bw, orchestrator._current_scenario)
    else:
        fc = agent.generate_24h_forecast(kw, bw, orchestrator._current_scenario)
    return {"forecast": fc, "data_source": "DEMO / SIMULATED DATA"}


@app.get("/api/maintenance/risks")
def get_maintenance_risks():
    from .data.simulator import simulator
    from .agents.maintenance_agent import MaintenanceAgent
    agent = MaintenanceAgent()
    risks, _ = agent.analyze(
        simulator.get_solar_assets(),
        simulator.get_wind_assets(),
        simulator.get_maintenance_history()
    )
    return {
        "risks": [r.dict() for r in risks],
        "data_source": "DEMO / SIMULATED DATA",
    }


@app.get("/api/grid/status")
def get_grid_status():
    from .data.simulator import simulator
    solar = sum(a.actual_output_mw for a in simulator.get_solar_assets())
    wind = sum(a.actual_output_mw for a in simulator.get_wind_assets())
    grid = simulator.get_grid_status(solar, wind)
    storage = simulator.get_storage()
    return {
        "grid": grid.dict(),
        "storage": [s.dict() for s in storage],
        "data_source": "DEMO / SIMULATED DATA",
    }


@app.get("/api/recommendations")
def get_recommendations():
    """Returns all recommendations with human-decision status."""
    return {
        "recommendations": orchestrator.get_recommendations(),
        "safety_note": (
            "⚠️ DECISION-SUPPORT ONLY: All recommendations require human operator approval. "
            "No physical actions have been or will be taken automatically."
        ),
        "data_source": "DEMO / SIMULATED DATA",
    }


@app.post("/api/recommendations/decide")
def human_decision(request: HumanDecisionRequest):
    """
    Record human operator decision on a recommendation.
    SAFETY: Records decision only. No physical actions taken.
    """
    result = orchestrator.process_human_decision(
        request.rec_id, request.decision, request.note
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@app.get("/api/decisions/log")
def get_decision_log():
    """Returns the full AI decision log for auditability."""
    return {
        "log": orchestrator.get_decision_log(),
        "description": "Complete log of AI findings, recommendations, and human decisions.",
    }


@app.get("/api/agents/activity")
def get_agent_activity():
    """Returns recent agent activity log."""
    return {
        "activities": orchestrator.get_all_activities(),
    }


@app.post("/api/chat")
def chat(request: ChatRequest):
    """
    IBM Granite AI chat endpoint.
    Provides natural-language responses based on current park data.
    """
    try:
        state = orchestrator.run()
        granite_client.set_context(state)
        result = granite_client.chat(request.message, state)
        return {
            "response": result["response"],
            "source": result["source"],
            "model": result.get("model", "N/A"),
            "confidence": result.get("confidence", 0.8),
            "note": result.get("note", "DATA SOURCE: DEMO / SIMULATED DATA"),
            "safety_notice": (
                "AI responses are for information and decision support only. "
                "No physical actions are taken based on AI output."
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scenario/run")
def run_scenario(request: ScenarioRequest):
    """
    Run a demo scenario to showcase AI agent capabilities.
    DATA: DEMO / SIMULATED
    """
    valid_scenarios = ["underperformance", "high_generation", "weather_drop", "normal"]
    if request.scenario not in valid_scenarios:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario. Choose from: {valid_scenarios}"
        )
    result = orchestrator.run_scenario(request.scenario)
    return result


@app.post("/api/scenario/reset")
def reset_scenario():
    orchestrator.reset_scenario()
    return {"success": True, "message": "Scenario reset to normal operation"}


@app.get("/api/config/info")
def get_config_info():
    """Returns non-sensitive configuration information."""
    return {
        "platform": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "granite_mode": "mock" if settings.USE_MOCK_GRANITE else "live",
        "locations": settings.LOCATIONS,
        "granite_configured": bool(settings.GRANITE_API_KEY),
        "data_source": "DEMO / SIMULATED DATA",
        "safety_notice": (
            "🛡 HUMAN-IN-THE-LOOP: All AI recommendations require operator approval. "
            "No physical equipment is controlled by this system."
        ),
    }


# ─── Serve frontend static files ─────────────────────────────────────────────

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        index = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Frontend not built")
