"""
IBM Granite LLM Client
Provides natural-language reasoning for the renewable energy platform.
Uses IBM WatsonX / Granite API when credentials are available.
Falls back to intelligent mock implementation when credentials are not set.
API keys are NEVER hardcoded — loaded from environment variables only.
"""
import os
import json
import re
from typing import Dict, Any, Optional, List
from ..config.settings import settings


class GraniteClient:
    """
    IBM Granite AI Client for natural language generation.
    Automatically uses mock mode if API credentials are not configured.
    """

    SYSTEM_PROMPT = """You are an AI assistant for a Smart Renewable Energy Intelligence Platform 
monitoring solar-wind hybrid parks in Kutch and Banaskantha, Gujarat, India.

Your role is to help operators understand complex renewable energy data and make better decisions.

CRITICAL RULES:
1. You provide analysis and recommendations ONLY — never commands to equipment.
2. Always distinguish between: Sensor Data, Calculated Metrics, Forecasts, AI Analysis, Recommendations.
3. Never invent sensor readings. Base all answers on the provided data context.
4. If data is insufficient, say "Insufficient data for reliable recommendation."
5. All data in this system is SIMULATED (demo mode).
6. You support human decision-making. Operators must approve all recommendations.
7. Be concise and clear — operators need quick, actionable insights.
"""

    def __init__(self):
        self.use_mock = settings.USE_MOCK_GRANITE
        self._context_cache: Dict = {}

    def set_context(self, context: Dict):
        """Update the current park data context for AI responses."""
        self._context_cache = context

    def chat(self, user_message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send a message to Granite AI and get a response.
        Returns structured response with source attribution.
        """
        ctx = context or self._context_cache

        if self.use_mock:
            return self._mock_response(user_message, ctx)

        try:
            return self._real_granite_response(user_message, ctx)
        except Exception as e:
            return {
                "response": f"[IBM Granite API unavailable: {str(e)[:100]}. Using analytical fallback.]\n\n"
                            + self._mock_response(user_message, ctx)["response"],
                "source": "MOCK (API error)",
                "model": "fallback",
                "confidence": 0.7,
            }

    def generate_recommendation_explanation(
        self,
        recommendation: Dict,
        context: Dict,
    ) -> str:
        """Generate a natural-language explanation for a recommendation."""
        if self.use_mock:
            return self._mock_explain_recommendation(recommendation, context)
        prompt = self._build_explanation_prompt(recommendation, context)
        result = self._call_granite(prompt)
        return result.get("response", self._mock_explain_recommendation(recommendation, context))

    def generate_anomaly_explanation(self, asset_id: str, findings: List[Dict]) -> str:
        """Generate explanation for asset anomaly."""
        relevant = [f for f in findings if f.get("asset_id") == asset_id]
        if not relevant:
            return f"No anomaly data found for {asset_id}."
        return self._mock_explain_anomaly(asset_id, relevant, self._context_cache)

    def generate_park_summary(self, context: Dict) -> str:
        """Generate a natural-language park health summary."""
        if self.use_mock:
            return self._mock_park_summary(context)
        prompt = self._build_summary_prompt(context)
        result = self._call_granite(prompt)
        return result.get("response", self._mock_park_summary(context))

    # ─── Real Granite API ─────────────────────────────────────────────────────

    def _real_granite_response(self, message: str, context: Dict) -> Dict[str, Any]:
        """Call IBM WatsonX Granite API."""
        import urllib.request

        ctx_summary = self._build_context_summary(context)
        prompt = f"{self.SYSTEM_PROMPT}\n\nCurrent Park Data:\n{ctx_summary}\n\nOperator Question: {message}\n\nResponse:"

        payload = json.dumps({
            "model_id": settings.GRANITE_MODEL_ID,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 400,
                "min_new_tokens": 20,
                "stop_sequences": ["\n\n\n"],
                "temperature": 0.3,
            },
            "project_id": settings.GRANITE_PROJECT_ID,
        }).encode()

        req = urllib.request.Request(
            settings.GRANITE_API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.GRANITE_API_KEY}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())

        response_text = data.get("results", [{}])[0].get("generated_text", "No response").strip()
        return {
            "response": response_text,
            "source": "IBM Granite (WatsonX)",
            "model": settings.GRANITE_MODEL_ID,
            "confidence": 0.88,
        }

    def _call_granite(self, prompt: str) -> Dict[str, Any]:
        """Low-level Granite call."""
        return self._real_granite_response(prompt, {})

    # ─── Mock Granite ─────────────────────────────────────────────────────────

    def _mock_response(self, message: str, context: Dict) -> Dict[str, Any]:
        """
        Intelligent mock response using pattern matching on the question
        and actual data from the context.
        """
        msg_lower = message.lower()
        response = ""

        kpis = context.get("kpis", {})
        risks = context.get("maintenance_risks", [])
        recs = context.get("active_recommendations", [])
        findings = context.get("all_findings", [])
        solar_assets = context.get("solar_assets", [])
        wind_assets = context.get("wind_assets", [])
        grid = context.get("grid_status", {})
        weather_k = context.get("kutch_weather", {})
        forecast = context.get("forecast_6h", [])
        park = context.get("park_summary", {})

        if any(w in msg_lower for w in ["underperform", "below", "low performance", "poor"]):
            response = self._answer_underperformance(wind_assets, solar_assets, findings)

        elif "wt-07" in msg_lower or ("turbine 7" in msg_lower):
            response = self._answer_wt07(wind_assets, findings, risks)

        elif any(w in msg_lower for w in ["maintenance", "risk", "inspect", "repair"]):
            response = self._answer_maintenance(risks)

        elif any(w in msg_lower for w in ["forecast", "next", "6 hour", "24 hour", "generation expect"]):
            response = self._answer_forecast(forecast, kpis)

        elif any(w in msg_lower for w in ["exceed", "surplus", "demand", "storage", "battery", "export"]):
            response = self._answer_grid(grid, kpis, recs)

        elif any(w in msg_lower for w in ["recommend", "suggest", "should", "consider", "action"]):
            response = self._answer_recommendations(recs, grid, kpis)

        elif any(w in msg_lower for w in ["health", "summary", "status", "park", "overview"]):
            response = self._answer_park_summary(park, kpis, risks)

        elif any(w in msg_lower for w in ["weather", "wind speed", "solar irradiance", "cloud", "temperature"]):
            response = self._answer_weather(weather_k)

        elif any(w in msg_lower for w in ["why", "reason", "explain", "cause"]):
            response = self._answer_explanation(msg_lower, findings, wind_assets)

        else:
            response = self._answer_general(kpis, park, risks, recs)

        return {
            "response": response,
            "source": "IBM Granite (Mock — configure GRANITE_API_KEY for live API)",
            "model": "granite-13b-instruct-v2 (mock)",
            "confidence": 0.82,
            "note": "DATA SOURCE: DEMO / SIMULATED DATA",
        }

    def _answer_underperformance(self, wind: List, solar: List, findings: List) -> str:
        underperforming_wind = [a for a in wind if a.get("efficiency", 100) < 85]
        underperforming_solar = [a for a in solar if a.get("efficiency", 100) < 85]
        lines = ["**AI Analysis — Based on Current Simulated Sensor Data:**\n"]
        if underperforming_wind:
            lines.append(f"**Wind turbines underperforming ({len(underperforming_wind)}):**")
            for a in underperforming_wind[:5]:
                lines.append(f"• {a['asset_id']} ({a['name']}): {a['efficiency']:.1f}% efficiency, {a['performance_deviation']:.1f}% deviation — Status: {a['status']}")
        if underperforming_solar:
            lines.append(f"\n**Solar arrays underperforming ({len(underperforming_solar)}):**")
            for a in underperforming_solar[:5]:
                lines.append(f"• {a['asset_id']} ({a['name']}): {a['efficiency']:.1f}% efficiency — Status: {a['status']}")
        if not underperforming_wind and not underperforming_solar:
            lines.append("✅ All assets are currently performing within acceptable efficiency thresholds (>85%).")
        lines.append("\n*Source: Calculated from simulated sensor data. Physical verification required for confirmed faults.*")
        return "\n".join(lines)

    def _answer_wt07(self, wind: List, findings: List, risks: List) -> str:
        wt07 = next((a for a in wind if a.get("asset_id") == "WT-07"), None)
        risk = next((r for r in risks if r.get("asset_id") == "WT-07"), None)
        lines = ["**AI Analysis: WT-07 — Kutch Wind Turbine 7**\n"]
        lines.append("*Source: Simulated sensor data + AI analysis*\n")
        if wt07:
            lines.append(f"**Current Performance (Sensor Data):**")
            lines.append(f"• Actual output: {wt07['actual_output_mw']:.3f} MW | Expected: {wt07['expected_output_mw']:.3f} MW")
            lines.append(f"• Efficiency: {wt07['efficiency']:.1f}% (deviation: {wt07['performance_deviation']:.1f}%)")
            lines.append(f"• Wind speed: {wt07['wind_speed']:.1f} m/s (favorable range)")
            lines.append(f"• Generator temperature: {wt07['generator_temperature']:.1f}°C")
            lines.append(f"• Vibration: {wt07['vibration']:.2f} mm/s")
            lines.append(f"• Status: {wt07['status']}")
        if risk:
            lines.append(f"\n**Maintenance Risk (Calculated):**")
            lines.append(f"• Risk score: {risk['risk_score']}/100 — {risk['risk_level']}")
            lines.append(f"• Possible issue: {risk['possible_issue']}")
            lines.append(f"• Recommended action: {risk['recommended_inspection']}")
        lines.append("\n**AI Recommendation:**")
        lines.append("WT-07 is producing significantly below expected output despite favorable wind conditions. ")
        lines.append("The combination of reduced efficiency, elevated vibration, and high generator temperature suggests ")
        lines.append("possible mechanical degradation. A physical inspection is recommended within 48 hours.")
        lines.append("\n⚠️ *This is AI analysis only — not a confirmed fault. Physical inspection required.*")
        return "\n".join(lines)

    def _answer_maintenance(self, risks: List) -> str:
        high = [r for r in risks if r.get("risk_level") in ("HIGH", "CRITICAL")]
        lines = ["**AI Analysis — Maintenance Risk Assessment:**\n"]
        lines.append(f"*Source: Calculated from simulated sensor data and performance trends*\n")
        if high:
            lines.append(f"**{len(high)} high-priority asset(s) identified:**\n")
            for r in high[:5]:
                lines.append(f"**{r['asset_id']}** ({r['asset_name']})")
                lines.append(f"  Risk Score: {r['risk_score']}/100 | Level: {r['risk_level']}")
                lines.append(f"  Issue: {r['possible_issue']}")
                lines.append(f"  Action: {r['recommended_inspection']}")
                lines.append(f"  Performance decline: {r['performance_decline_pct']:.1f}%\n")
        else:
            lines.append("✅ No high-priority maintenance issues currently identified.")
        lines.append("⚠️ *Recommendations only — operator must approve any inspection scheduling.*")
        return "\n".join(lines)

    def _answer_forecast(self, forecast: List, kpis: Dict) -> str:
        if not forecast:
            return "Insufficient forecast data available."
        avg_6h = sum(f.get("total_forecast_mw", 0) for f in forecast) / len(forecast)
        peak = max(forecast, key=lambda f: f.get("total_forecast_mw", 0))
        lines = ["**Generation Forecast — Next 6 Hours:**\n"]
        lines.append("*Source: SIMULATED FORECAST DATA based on weather models*\n")
        lines.append(f"• Current total generation: {kpis.get('total_renewable_mw', 0):.1f} MW")
        lines.append(f"• Average forecast next 6h: {avg_6h:.1f} MW")
        lines.append(f"• Peak forecast: {peak['total_forecast_mw']:.1f} MW at {peak.get('label', 'N/A')}")
        lines.append(f"• Solar forecast H+1: {forecast[0]['solar_forecast_mw']:.1f} MW")
        lines.append(f"• Wind forecast H+1: {forecast[0]['wind_forecast_mw']:.1f} MW")
        lines.append(f"• Confidence: {forecast[0].get('confidence', 0):.0f}% (decreasing over time)")
        lines.append("\n*Note: All forecasts are SIMULATED. Confidence decreases with forecast horizon.*")
        return "\n".join(lines)

    def _answer_grid(self, grid: Dict, kpis: Dict, recs: List) -> str:
        surplus = grid.get("surplus_mw", 0)
        lines = ["**Grid Situation Analysis:**\n"]
        lines.append("*Source: Simulated grid data + AI analysis*\n")
        lines.append(f"• Renewable generation: {grid.get('renewable_generation_mw', 0):.1f} MW")
        lines.append(f"• Grid demand: {grid.get('total_demand_mw', 0):.1f} MW")
        lines.append(f"• {'Surplus' if surplus > 0 else 'Shortfall'}: {abs(surplus):.1f} MW")
        lines.append(f"• Storage SoC: {kpis.get('storage_soc_pct', 0):.0f}%")
        lines.append(f"• Current export: {grid.get('grid_export_mw', 0):.1f} MW")
        if surplus > 10:
            lines.append("\n**AI Analysis:** Renewable generation exceeds demand. Consider reviewing storage and export options.")
        elif surplus < -5:
            lines.append("\n**AI Analysis:** Demand exceeds renewable generation. Storage discharge or import may be appropriate.")
        else:
            lines.append("\n**AI Analysis:** Generation and demand are approximately balanced.")
        grid_recs = [r for r in recs if "grid" in r.get("agent_name", "").lower() or "store" in r.get("recommendation_type", "").lower()]
        if grid_recs:
            lines.append(f"\n**Active Recommendation:** {grid_recs[0]['title']} — awaiting operator decision.")
        lines.append("\n⚠️ *Decision support only. No grid actions have been or will be taken automatically.*")
        return "\n".join(lines)

    def _answer_recommendations(self, recs: List, grid: Dict, kpis: Dict) -> str:
        lines = ["**AI Recommendations — Current Active:**\n"]
        lines.append("*Source: AI analysis of simulated data*\n")
        if recs:
            for r in recs[:4]:
                lines.append(f"**{r['title']}** [{r['risk_level']}]")
                lines.append(f"  Agent: {r['agent_name']}")
                lines.append(f"  {r['description'][:150]}...")
                lines.append(f"  Confidence: {r['confidence']:.0f}% | Status: {r['human_decision']}\n")
        else:
            lines.append("✅ No active recommendations at this time.")
        lines.append("⚠️ *All recommendations require human operator approval. No actions are automated.*")
        return "\n".join(lines)

    def _answer_park_summary(self, park: Dict, kpis: Dict, risks: List) -> str:
        lines = ["**Park Health Summary — DEMO / SIMULATED DATA**\n"]
        lines.append(f"*Generated: {park.get('timestamp', 'N/A')[:19]}*\n")
        lines.append(f"**Overall Status:** {park.get('overall_status', 'N/A')}")
        lines.append(f"{park.get('health_summary', '')}\n")
        lines.append(f"**Generation (Calculated):**")
        lines.append(f"• Solar: {kpis.get('solar_generation_mw', 0):.1f} MW | Wind: {kpis.get('wind_generation_mw', 0):.1f} MW")
        lines.append(f"• Total: {kpis.get('total_renewable_mw', 0):.1f} MW | Efficiency: {kpis.get('park_efficiency_pct', 0):.1f}%")
        lines.append(f"• CO₂ Avoided: {kpis.get('co2_avoided_tons_hr', 0):.1f} tons/hr\n")
        lines.append(f"**Asset Health:**")
        lines.append(f"• ✅ Healthy: {park.get('healthy_assets', 0)} | ⚠️ Warning: {park.get('warning_assets', 0)} | 🔴 Critical: {park.get('critical_assets', 0)}")
        high_risk = [r for r in risks if r.get("risk_level") in ("HIGH", "CRITICAL")]
        lines.append(f"• High maintenance risk: {len(high_risk)} asset(s)")
        return "\n".join(lines)

    def _answer_weather(self, weather: Dict) -> str:
        lines = ["**Current Weather — Kutch (SIMULATED DATA)**\n"]
        lines.append(f"• Condition: {weather.get('condition', 'N/A')}")
        lines.append(f"• Solar irradiance: {weather.get('solar_irradiance', 0):.0f} W/m²")
        lines.append(f"• Wind speed: {weather.get('wind_speed', 0):.1f} m/s | Direction: {weather.get('wind_direction', 0):.0f}°")
        lines.append(f"• Temperature: {weather.get('temperature', 0):.1f}°C")
        lines.append(f"• Cloud cover: {weather.get('cloud_cover', 0):.0f}%")
        lines.append(f"• Humidity: {weather.get('humidity', 0):.0f}%")
        lines.append(f"\n*Source: SIMULATED WEATHER DATA — Not real meteorological data*")
        return "\n".join(lines)

    def _answer_explanation(self, msg: str, findings: List, wind: List) -> str:
        if "wt-07" in msg:
            return self._answer_wt07(wind, findings, [])
        crit_findings = [f for f in findings if f.get("severity") in ("CRITICAL", "WARNING")]
        if crit_findings:
            f = crit_findings[0]
            return f"**AI Analysis — {f.get('asset_id', 'System')}:**\n\n{f['description']}\n\n*Source: {f['data_source']}*"
        return "I don't have enough specific context to explain that. Please ask about a specific asset ID or condition."

    def _answer_general(self, kpis: Dict, park: Dict, risks: List, recs: List) -> str:
        lines = ["**Smart Renewable Energy Intelligence Platform**\n"]
        lines.append("*DATA SOURCE: DEMO / SIMULATED DATA*\n")
        lines.append(f"I'm monitoring your solar-wind hybrid park in Kutch and Banaskantha, Gujarat.\n")
        lines.append(f"**Quick Status:**")
        lines.append(f"• Total generation: {kpis.get('total_renewable_mw', 0):.1f} MW (Efficiency: {kpis.get('park_efficiency_pct', 0):.1f}%)")
        lines.append(f"• Park status: {park.get('overall_status', 'N/A')}")
        high_risk = len([r for r in risks if r.get("risk_level") in ("HIGH", "CRITICAL")])
        lines.append(f"• High-risk assets: {high_risk}")
        lines.append(f"• Active recommendations: {len(recs)}\n")
        lines.append("You can ask me about:")
        lines.append("• Which assets are underperforming?")
        lines.append("• What is the expected generation for the next 6 hours?")
        lines.append("• Which assets have the highest maintenance risk?")
        lines.append("• What should the operator consider doing?")
        lines.append("• Give me the current park health summary.")
        return "\n".join(lines)

    def _mock_explain_recommendation(self, rec: Dict, context: Dict) -> str:
        rec_type = rec.get("recommendation_type", "")
        if "store" in rec_type:
            kpis = context.get("kpis", {})
            grid = context.get("grid_status", {})
            return (
                f"**Why store excess energy?**\n\n"
                f"Renewable generation ({grid.get('renewable_generation_mw', 0):.1f} MW) currently "
                f"exceeds grid demand ({grid.get('total_demand_mw', 0):.1f} MW) by "
                f"{grid.get('surplus_mw', 0):.1f} MW. "
                f"Available storage capacity allows capturing this excess rather than curtailing generation. "
                f"The 6-hour forecast indicates continued high generation, making storage a prudent choice "
                f"to maximize renewable utilization and reduce curtailment.\n\n"
                f"*Source: AI analysis of simulated grid and generation data*"
            )
        return rec.get("description", "No explanation available.")

    def _mock_explain_anomaly(self, asset_id: str, findings: List, context: Dict) -> str:
        if not findings:
            return f"No anomaly data for {asset_id}."
        f = findings[0]
        return f"**AI Analysis — {asset_id}:**\n\n{f['description']}\n\n*Source: {f['data_source']}. This is AI analysis, not a confirmed fault.*"

    def _mock_park_summary(self, context: Dict) -> str:
        return self._answer_general(
            context.get("kpis", {}),
            context.get("park_summary", {}),
            context.get("maintenance_risks", []),
            context.get("active_recommendations", []),
        )

    def _build_context_summary(self, context: Dict) -> str:
        kpis = context.get("kpis", {})
        grid = context.get("grid_status", {})
        park = context.get("park_summary", {})
        risks = context.get("maintenance_risks", [])
        high_risk = [r for r in risks if r.get("risk_level") in ("HIGH", "CRITICAL")]

        return (
            f"Total renewable generation: {kpis.get('total_renewable_mw', 0):.1f} MW\n"
            f"Park efficiency: {kpis.get('park_efficiency_pct', 0):.1f}%\n"
            f"Grid demand: {grid.get('total_demand_mw', 0):.1f} MW\n"
            f"Grid surplus/deficit: {grid.get('surplus_mw', 0):.1f} MW\n"
            f"Storage SoC: {kpis.get('storage_soc_pct', 0):.0f}%\n"
            f"Park status: {park.get('overall_status', 'N/A')}\n"
            f"High-risk assets: {len(high_risk)}\n"
            f"Active recommendations: {len(context.get('active_recommendations', []))}\n"
            f"All data is SIMULATED (demo mode)"
        )

    def _build_explanation_prompt(self, rec: Dict, context: Dict) -> str:
        ctx = self._build_context_summary(context)
        return (
            f"{self.SYSTEM_PROMPT}\n\nCurrent Context:\n{ctx}\n\n"
            f"Recommendation to explain:\n{rec.get('description', '')}\n\n"
            f"Explain why this recommendation was generated in 2-3 sentences:\n"
        )

    def _build_summary_prompt(self, context: Dict) -> str:
        ctx = self._build_context_summary(context)
        return f"{self.SYSTEM_PROMPT}\n\nCurrent Park Data:\n{ctx}\n\nGenerate a concise park health summary for the operator:\n"


# Singleton
granite_client = GraniteClient()
