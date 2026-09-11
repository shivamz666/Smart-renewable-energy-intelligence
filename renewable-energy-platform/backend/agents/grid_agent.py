"""
Grid Analysis & Optimization Recommendation Agent
IMPORTANT: This agent is an analysis and recommendation agent ONLY.
It does NOT control the grid, batteries, inverters, turbines, or any physical equipment.
All outputs are recommendations requiring human operator approval.
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from ..models.asset_models import (
    GridStatus, StorageStatus, AgentFinding, AgentRecommendation,
    AgentActivity, RiskLevel, HumanDecision
)


class GridAnalysisAgent:
    """
    Agent 4: Grid Analysis & Optimization Recommendation
    Analyzes grid conditions and generates operator recommendations.
    ⚠️ DECISION SUPPORT ONLY — No physical grid commands are issued.
    """
    NAME = "Grid Analysis Agent"

    SURPLUS_THRESHOLD_MW = 10.0      # MW surplus to trigger recommendation
    STORAGE_LOW_PCT = 20.0           # % SoC considered low
    STORAGE_HIGH_PCT = 90.0          # % SoC considered full
    EXPORT_SAFE_MAX_PCT = 80.0       # % of generation safe to export

    def analyze(
        self,
        grid: GridStatus,
        storage: List[StorageStatus],
        forecast_6h: List[Dict],
        scenario: str = "normal",
    ) -> Tuple[List[AgentFinding], List[AgentRecommendation], List[AgentActivity]]:
        findings = []
        recommendations = []
        activities = []
        now = datetime.now().isoformat()

        total_storage_mwh = sum(s.capacity_mwh for s in storage)
        current_charge_mwh = sum(s.current_charge_mwh for s in storage)
        avg_soc = (current_charge_mwh / total_storage_mwh * 100) if total_storage_mwh > 0 else 0
        available_storage_mwh = total_storage_mwh - current_charge_mwh

        forecast_avg = sum(f["total_forecast_mw"] for f in forecast_6h[:3]) / 3 if forecast_6h else 0
        forecast_trend = "increasing" if forecast_avg > grid.renewable_generation_mw else "decreasing"

        # ─── Surplus detection ──────────────────────────────────────────────
        if grid.surplus_mw > self.SURPLUS_THRESHOLD_MW:
            findings.append(AgentFinding(
                agent_name=self.NAME,
                asset_id=None,
                finding_type="renewable_surplus",
                severity="INFO",
                description=(
                    f"Renewable generation ({grid.renewable_generation_mw:.1f} MW) currently exceeds "
                    f"grid demand ({grid.total_demand_mw:.1f} MW) by {grid.surplus_mw:.1f} MW. "
                    f"Available storage: {available_storage_mwh:.1f} MWh. "
                    f"Forecast trend: {forecast_trend}."
                ),
                data_source="SIMULATED DATA",
                timestamp=now,
                details={
                    "surplus_mw": grid.surplus_mw,
                    "renewable_mw": grid.renewable_generation_mw,
                    "demand_mw": grid.total_demand_mw,
                    "available_storage_mwh": available_storage_mwh,
                    "avg_soc_pct": avg_soc,
                }
            ))
            activities.append(AgentActivity(
                timestamp=now,
                agent_name=self.NAME,
                activity=f"Renewable surplus detected: {grid.surplus_mw:.1f} MW above demand — analyzing storage/export options",
                severity="info",
            ))

            # Generate storage recommendation if storage available
            if available_storage_mwh > 5:
                store_amount = min(available_storage_mwh, grid.surplus_mw * 2)
                reasoning = [
                    f"Renewable generation exceeds demand by {grid.surplus_mw:.1f} MW",
                    f"Available storage capacity: {available_storage_mwh:.1f} MWh (SoC: {avg_soc:.0f}%)",
                    f"Forecast shows {forecast_trend} generation trend",
                    "Storing excess prevents curtailment of renewable energy",
                    "Grid export limit considerations apply",
                ]
                if scenario == "high_generation":
                    reasoning.append("High generation scenario: solar and wind both performing above average")

                recommendations.append(AgentRecommendation(
                    rec_id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    agent_name=self.NAME,
                    recommendation_type="store_excess_energy",
                    title="Store Excess Renewable Energy",
                    description=(
                        f"Renewable generation currently exceeds demand by approximately {grid.surplus_mw:.1f} MW. "
                        f"Consider storing up to {store_amount:.1f} MWh of available excess energy in battery storage "
                        f"and exporting the remaining suitable generation to the grid."
                    ),
                    reasoning=reasoning,
                    confidence=82.0 if scenario == "high_generation" else 74.0,
                    risk_level=RiskLevel.LOW,
                    safety_note=(
                        "⚠️ DECISION SUPPORT ONLY: This recommendation has NOT been executed. "
                        "No grid commands, battery commands, or switching operations have been issued. "
                        "Operator must review and approve before any physical action."
                    ),
                ))

        # ─── Generation shortfall ───────────────────────────────────────────
        elif grid.surplus_mw < -5:
            shortfall = abs(grid.surplus_mw)
            findings.append(AgentFinding(
                agent_name=self.NAME,
                asset_id=None,
                finding_type="generation_shortfall",
                severity="WARNING",
                description=(
                    f"Grid demand ({grid.total_demand_mw:.1f} MW) exceeds renewable generation "
                    f"({grid.renewable_generation_mw:.1f} MW) by {shortfall:.1f} MW."
                ),
                data_source="SIMULATED DATA",
                timestamp=now,
                details={"shortfall_mw": shortfall},
            ))
            if avg_soc > 30:
                recommendations.append(AgentRecommendation(
                    rec_id=str(uuid.uuid4())[:8],
                    timestamp=now,
                    agent_name=self.NAME,
                    recommendation_type="discharge_storage",
                    title="Consider Storage Discharge",
                    description=(
                        f"Demand exceeds renewable generation by {shortfall:.1f} MW. "
                        f"Storage is at {avg_soc:.0f}% SoC ({current_charge_mwh:.1f} MWh available). "
                        f"Consider discharging storage to supplement renewable generation and reduce grid import."
                    ),
                    reasoning=[
                        f"Generation shortfall of {shortfall:.1f} MW",
                        f"Storage available: {current_charge_mwh:.1f} MWh at {avg_soc:.0f}% SoC",
                        "Discharge can reduce costly grid import",
                    ],
                    confidence=71.0,
                    risk_level=RiskLevel.MEDIUM,
                ))

        # ─── Weather drop scenario ──────────────────────────────────────────
        if scenario == "weather_drop":
            recommendations.append(AgentRecommendation(
                rec_id=str(uuid.uuid4())[:8],
                timestamp=now,
                agent_name=self.NAME,
                recommendation_type="prepare_for_generation_drop",
                title="Prepare for Solar Generation Drop",
                description=(
                    "Solar generation is expected to decline over the next 2 hours due to increased cloud cover. "
                    "Consider reviewing available wind generation and storage capacity to maintain grid stability."
                ),
                reasoning=[
                    "Detected significant increase in cloud cover",
                    "Solar irradiance declining — forecast shows continued reduction",
                    "Wind generation remains available as partial offset",
                    f"Storage SoC: {avg_soc:.0f}% — can supplement if needed",
                ],
                confidence=78.0,
                risk_level=RiskLevel.MEDIUM,
            ))
            activities.append(AgentActivity(
                timestamp=now,
                agent_name=self.NAME,
                activity="Weather-driven generation drop expected — grid analysis updated with reduced solar forecast",
                severity="warning",
            ))

        # ─── General grid health check ──────────────────────────────────────
        if abs(grid.frequency_hz - 50.0) > 0.1:
            findings.append(AgentFinding(
                agent_name=self.NAME,
                asset_id=None,
                finding_type="frequency_deviation",
                severity="WARNING",
                description=f"Grid frequency {grid.frequency_hz:.3f} Hz deviates from nominal 50 Hz.",
                data_source="SIMULATED DATA",
                timestamp=now,
                details={"frequency": grid.frequency_hz},
            ))

        return findings, recommendations, activities

    def get_grid_summary(self, grid: GridStatus, storage: List[StorageStatus]) -> Dict[str, Any]:
        total_cap = sum(s.capacity_mwh for s in storage)
        total_charge = sum(s.current_charge_mwh for s in storage)
        avg_soc = (total_charge / total_cap * 100) if total_cap > 0 else 0

        situation = "balanced"
        if grid.surplus_mw > 10:
            situation = "surplus"
        elif grid.surplus_mw < -5:
            situation = "deficit"

        return {
            "renewable_generation_mw": grid.renewable_generation_mw,
            "total_demand_mw": grid.total_demand_mw,
            "surplus_mw": grid.surplus_mw,
            "grid_situation": situation,
            "storage_soc_pct": round(avg_soc, 1),
            "storage_available_mwh": round(total_cap - total_charge, 2),
            "total_storage_mwh": round(total_cap, 2),
            "renewable_share_pct": grid.renewable_share_pct,
            "grid_export_mw": grid.grid_export_mw,
            "grid_import_mw": grid.grid_import_mw,
            "data_source": "SIMULATED DATA",
        }
