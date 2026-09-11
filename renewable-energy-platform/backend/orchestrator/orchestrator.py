"""
Agent Orchestrator
Coordinates all AI agents, manages data flow, maintains decision log,
and handles scenario simulation for demo purposes.
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..data.simulator import simulator
from ..agents.performance_agent import PerformanceAgent
from ..agents.maintenance_agent import MaintenanceAgent
from ..agents.forecasting_agent import ForecastingAgent
from ..agents.grid_agent import GridAnalysisAgent
from ..agents.dashboard_agent import DashboardAgent
from ..models.asset_models import (
    AgentRecommendation, DecisionLogEntry, AgentActivity, HumanDecision,
    AssetStatus, ParkSummary
)


class AgentOrchestrator:
    """
    Central orchestrator that coordinates all AI agents.
    Manages data pipeline, recommendation tracking, and decision log.
    """

    def __init__(self):
        self.performance_agent = PerformanceAgent()
        self.maintenance_agent = MaintenanceAgent()
        self.forecasting_agent = ForecastingAgent()
        self.grid_agent = GridAnalysisAgent()
        self.dashboard_agent = DashboardAgent()

        # In-memory stores (would be a database in production)
        self._recommendations: Dict[str, AgentRecommendation] = {}
        self._decision_log: List[DecisionLogEntry] = []
        self._activity_log: List[AgentActivity] = []
        self._current_scenario: str = "normal"

    # ─── Main orchestration run ───────────────────────────────────────────────

    def run(self) -> Dict[str, Any]:
        """
        Execute all agents in sequence and return unified state.
        This is called on each API request for live data.
        """
        now = datetime.now().isoformat()
        new_activities: List[AgentActivity] = []

        # 1. Collect sensor data
        solar_assets = simulator.get_solar_assets()
        wind_assets = simulator.get_wind_assets()
        substations = simulator.get_substations()
        storage = simulator.get_storage()
        maintenance_history = simulator.get_maintenance_history()
        kutch_weather = simulator.get_weather("kutch")
        banas_weather = simulator.get_weather("banaskantha")

        # 2. Performance agent
        perf_findings_solar, perf_acts_solar = self.performance_agent.analyze_solar_assets(solar_assets)
        perf_findings_wind, perf_acts_wind = self.performance_agent.analyze_wind_assets(wind_assets)
        all_perf_findings = perf_findings_solar + perf_findings_wind
        new_activities.extend(perf_acts_solar + perf_acts_wind)

        # Build maintenance risk map from performance data
        maintenance_risks_list, maint_acts = self.maintenance_agent.analyze(
            solar_assets, wind_assets, maintenance_history
        )
        new_activities.extend(maint_acts)
        maintenance_risk_map = {r.asset_id: r.risk_score for r in maintenance_risks_list}

        # 3. Asset health list
        asset_health = self.performance_agent.get_asset_health_list(
            solar_assets, wind_assets, maintenance_risk_map
        )

        # 4. Forecasting agent
        weather_findings, weather_acts = self.forecasting_agent.analyze_weather_impact(
            kutch_weather, banas_weather
        )
        new_activities.extend(weather_acts)
        forecast_6h = self.forecasting_agent.generate_6h_forecast(
            kutch_weather, banas_weather, self._current_scenario
        )
        forecast_24h = self.forecasting_agent.generate_24h_forecast(
            kutch_weather, banas_weather, self._current_scenario
        )

        # 5. Grid status
        solar_total = sum(a.actual_output_mw for a in solar_assets)
        wind_total = sum(a.actual_output_mw for a in wind_assets)
        grid_status = simulator.get_grid_status(solar_total, wind_total)

        # 6. Grid analysis agent
        grid_findings, grid_recs, grid_acts = self.grid_agent.analyze(
            grid_status, storage, forecast_6h, self._current_scenario
        )
        new_activities.extend(grid_acts)

        # 7. Maintenance recommendations
        maint_recs = self.maintenance_agent.generate_recommendations(maintenance_risks_list)

        # 8. All recommendations
        all_new_recs = grid_recs + maint_recs

        # Register new recommendations (avoid duplicates by asset+type)
        registered_recs = self._register_recommendations(all_new_recs)

        # 9. Dashboard agent summary
        active_recs = [r for r in self._recommendations.values() if r.human_decision == HumanDecision.PENDING]
        park_summary = self.dashboard_agent.generate_park_summary(
            asset_health, grid_status, storage,
            kutch_weather, banas_weather,
            maintenance_risks_list, active_recs
        )

        kpis = self.dashboard_agent.get_kpi_cards(asset_health, grid_status, storage)

        # 10. Record activities
        if new_activities:
            self._activity_log = (new_activities + self._activity_log)[:200]

        # Forecast summary
        gen_summary = self.forecasting_agent.get_generation_summary(
            forecast_6h, solar_total, wind_total
        )

        _d = lambda obj: obj.model_dump(mode="json")
        return {
            "timestamp": now,
            "scenario": self._current_scenario,
            "data_source": "DEMO / SIMULATED DATA",
            "park_summary": _d(park_summary),
            "kpis": kpis,
            "solar_assets": [_d(a) for a in solar_assets],
            "wind_assets": [_d(a) for a in wind_assets],
            "substations": [_d(s) for s in substations],
            "storage": [_d(s) for s in storage],
            "asset_health": [_d(a) for a in asset_health],
            "kutch_weather": _d(kutch_weather),
            "banas_weather": _d(banas_weather),
            "grid_status": _d(grid_status),
            "forecast_6h": forecast_6h,
            "forecast_24h": forecast_24h,
            "generation_summary": gen_summary,
            "all_findings": [_d(f) for f in all_perf_findings + weather_findings + grid_findings],
            "maintenance_risks": [_d(r) for r in maintenance_risks_list],
            "active_recommendations": [_d(r) for r in active_recs],
            "agent_activities": [_d(a) for a in self._activity_log[:50]],
        }

    # ─── Historical data ──────────────────────────────────────────────────────

    def get_historical_generation(self, hours: int = 24) -> List[Dict]:
        return [p.model_dump(mode="json") for p in simulator.get_historical_generation(hours)]

    # ─── Decision management ──────────────────────────────────────────────────

    def process_human_decision(
        self,
        rec_id: str,
        decision: str,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a human operator decision on a recommendation.
        SAFETY: This only records the decision. No physical actions are taken.
        """
        if rec_id not in self._recommendations:
            return {"success": False, "error": f"Recommendation {rec_id} not found"}

        rec = self._recommendations[rec_id]
        try:
            human_dec = HumanDecision(decision.upper())
        except ValueError:
            return {"success": False, "error": f"Invalid decision: {decision}"}

        rec.human_decision = human_dec
        rec.decision_timestamp = datetime.now().isoformat()
        rec.decision_note = note

        # Add to decision log
        log_entry = DecisionLogEntry(
            log_id=str(uuid.uuid4())[:8],
            timestamp=rec.decision_timestamp,
            agent_name=rec.agent_name,
            asset_id=rec.asset_id,
            finding=rec.description[:120],
            recommendation=rec.title,
            confidence=rec.confidence,
            human_decision=human_dec,
            decision_timestamp=rec.decision_timestamp,
            rec_id=rec_id,
        )
        self._decision_log.insert(0, log_entry)

        return {
            "success": True,
            "rec_id": rec_id,
            "decision": human_dec.value,
            "timestamp": rec.decision_timestamp,
            "safety_note": (
                "✅ Decision recorded. No physical equipment has been controlled. "
                "This platform is a decision-support system only."
            ),
        }

    def get_decision_log(self) -> List[Dict]:
        return [e.model_dump(mode="json") for e in self._decision_log[:100]]

    def get_recommendations(self) -> List[Dict]:
        return [r.model_dump(mode="json") for r in self._recommendations.values()]

    def get_all_activities(self) -> List[Dict]:
        return [a.model_dump(mode="json") for a in self._activity_log[:100]]

    # ─── Scenario management ─────────────────────────────────────────────────

    def run_scenario(self, scenario_type: str) -> Dict[str, Any]:
        """
        Trigger a demo scenario.
        Returns a series of agent activities simulating the scenario workflow.
        """
        self._current_scenario = scenario_type
        simulator.set_scenario(scenario_type)

        steps = self._build_scenario_steps(scenario_type)
        for step in steps:
            self._activity_log.insert(0, AgentActivity(**step))

        result = self.run()
        result["scenario_steps"] = steps
        result["scenario_type"] = scenario_type
        return result

    def reset_scenario(self):
        self._current_scenario = "normal"
        simulator.set_scenario("normal")

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _register_recommendations(
        self, new_recs: List[AgentRecommendation]
    ) -> List[AgentRecommendation]:
        registered = []
        for rec in new_recs:
            # Check if an active recommendation of same type already exists
            key = f"{rec.recommendation_type}_{rec.asset_id or 'grid'}"
            existing = next(
                (r for r in self._recommendations.values()
                 if f"{r.recommendation_type}_{r.asset_id or 'grid'}" == key
                 and r.human_decision == HumanDecision.PENDING),
                None
            )
            if existing is None:
                self._recommendations[rec.rec_id] = rec
                registered.append(rec)

                # Auto-add to decision log as PENDING
                log_entry = DecisionLogEntry(
                    log_id=str(uuid.uuid4())[:8],
                    timestamp=rec.timestamp,
                    agent_name=rec.agent_name,
                    asset_id=rec.asset_id,
                    finding=rec.description[:120],
                    recommendation=rec.title,
                    confidence=rec.confidence,
                    human_decision=HumanDecision.PENDING,
                    rec_id=rec.rec_id,
                )
                # Only add if not already present
                if not any(e.rec_id == rec.rec_id for e in self._decision_log):
                    self._decision_log.insert(0, log_entry)

        return registered

    def _build_scenario_steps(self, scenario: str) -> List[Dict]:
        now = datetime.now()

        if scenario == "underperformance":
            return [
                {"timestamp": (now - timedelta(seconds=11)).isoformat(), "agent_name": "Weather & Forecasting Agent", "activity": "Detected: Wind speed in Kutch remains favorable at 7.8 m/s — optimal generation conditions", "severity": "info"},
                {"timestamp": (now - timedelta(seconds=9)).isoformat(), "agent_name": "Performance Monitoring Agent", "activity": "WT-07 output declining — now 22% below expected despite favorable wind conditions", "severity": "warning"},
                {"timestamp": (now - timedelta(seconds=7)).isoformat(), "agent_name": "Performance Monitoring Agent", "activity": "WT-07 vibration elevated: 4.8 mm/s (normal: <3.5 mm/s). Generator temperature: 88°C", "severity": "alert"},
                {"timestamp": (now - timedelta(seconds=5)).isoformat(), "agent_name": "Predictive Maintenance Agent", "activity": "WT-07 maintenance risk increased to HIGH (score: 82/100) — mechanical degradation pattern detected", "severity": "alert"},
                {"timestamp": (now - timedelta(seconds=4)).isoformat(), "agent_name": "Weather & Forecasting Agent", "activity": "Confirmed: Wind conditions favorable for next 6 hours — WT-07 underperformance is asset-specific, not weather-related", "severity": "info"},
                {"timestamp": (now - timedelta(seconds=3)).isoformat(), "agent_name": "Weather & Forecasting Agent", "activity": "Updated wind generation forecast — WT-07 output excluded from reliable generation estimate", "severity": "warning"},
                {"timestamp": (now - timedelta(seconds=2)).isoformat(), "agent_name": "Grid Analysis Agent", "activity": "Recalculated expected renewable generation with WT-07 degraded output — minor impact on total park output", "severity": "info"},
                {"timestamp": (now - timedelta(seconds=1)).isoformat(), "agent_name": "IBM Granite AI", "activity": "AI analysis generated: WT-07 requires operator attention due to abnormal performance despite favorable wind conditions.", "severity": "alert"},
                {"timestamp": now.isoformat(), "agent_name": "Dashboard Agent", "activity": "ALERT GENERATED: WT-07 high maintenance risk — operator recommendation issued. Awaiting human decision.", "severity": "alert"},
            ]
        elif scenario == "high_generation":
            return [
                {"timestamp": (now - timedelta(seconds=11)).isoformat(), "agent_name": "Weather & Forecasting Agent", "activity": "Detected: Solar irradiance 945 W/m² in Kutch. Wind speed 11.2 m/s — exceptional generation conditions", "severity": "info"},
                {"timestamp": (now - timedelta(seconds=9)).isoformat(), "agent_name": "Performance Monitoring Agent", "activity": "All solar assets performing at 95%+ efficiency. Wind farm output 18% above baseline", "severity": "info"},
                {"timestamp": (now - timedelta(seconds=7)).isoformat(), "agent_name": "Weather & Forecasting Agent", "activity": "6-hour forecast: High generation expected to continue. Confidence: 88%", "severity": "info"},
                {"timestamp": (now - timedelta(seconds=5)).isoformat(), "agent_name": "Grid Analysis Agent", "activity": f"Potential renewable surplus detected: ~{25:.0f} MW above current demand", "severity": "warning"},
                {"timestamp": (now - timedelta(seconds=3)).isoformat(), "agent_name": "Grid Analysis Agent", "activity": "Storage analysis: 68 MWh available capacity across 3 BESS units. Export headroom available", "severity": "info"},
                {"timestamp": (now - timedelta(seconds=2)).isoformat(), "agent_name": "IBM Granite AI", "activity": "AI recommendation generated: Store excess renewable energy and export remaining. Awaiting operator approval.", "severity": "info"},
                {"timestamp": now.isoformat(), "agent_name": "Dashboard Agent", "activity": "RECOMMENDATION READY: Renewable surplus management — human operator decision required. No actions taken.", "severity": "info"},
            ]
        elif scenario == "weather_drop":
            return [
                {"timestamp": (now - timedelta(seconds=11)).isoformat(), "agent_name": "Weather & Forecasting Agent", "activity": "Detected: Rapid cloud cover increase — from 25% to 78% in Kutch over 30 minutes", "severity": "warning"},
                {"timestamp": (now - timedelta(seconds=9)).isoformat(), "agent_name": "Weather & Forecasting Agent", "activity": "Solar irradiance dropping: 850 W/m² → 280 W/m². Forecast shows continued cloud cover for 2+ hours", "severity": "alert"},
                {"timestamp": (now - timedelta(seconds=7)).isoformat(), "agent_name": "Performance Monitoring Agent", "activity": "Solar generation declining across Kutch arrays. Current output 40% below expected", "severity": "warning"},
                {"timestamp": (now - timedelta(seconds=5)).isoformat(), "agent_name": "Weather & Forecasting Agent", "activity": "Updated forecast: Solar generation expected to remain suppressed for next 2-3 hours. Wind partially compensates", "severity": "warning"},
                {"timestamp": (now - timedelta(seconds=4)).isoformat(), "agent_name": "Performance Monitoring Agent", "activity": "Park efficiency updated: 61% (from 94%). Wind generation stable at 28 MW", "severity": "warning"},
                {"timestamp": (now - timedelta(seconds=2)).isoformat(), "agent_name": "Grid Analysis Agent", "activity": "Grid impact analyzed: Renewable share declining. Storage discharge may be needed if demand rises", "severity": "warning"},
                {"timestamp": (now - timedelta(seconds=1)).isoformat(), "agent_name": "IBM Granite AI", "activity": "AI analysis: Solar generation declining due to cloud cover. Wind available as partial offset. Storage review recommended.", "severity": "warning"},
                {"timestamp": now.isoformat(), "agent_name": "Dashboard Agent", "activity": "WEATHER ALERT: Solar generation drop in progress — operator recommendation issued. No automatic action taken.", "severity": "alert"},
            ]
        return []


# Singleton
orchestrator = AgentOrchestrator()
