"""
Predictive Maintenance Agent
Analyzes asset performance trends and generates maintenance risk scores and recommendations.
IMPORTANT: This agent only recommends maintenance. It does NOT create or execute maintenance orders.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from ..models.asset_models import (
    SolarAsset, WindAsset, MaintenanceRecord, MaintenanceRisk,
    RiskLevel, AssetType, AgentFinding, AgentRecommendation, AgentActivity
)
import random


class MaintenanceAgent:
    """
    Agent 2: Predictive Maintenance
    Generates risk scores and recommendations.
    Does NOT automatically schedule or execute maintenance.
    """
    NAME = "Predictive Maintenance Agent"

    # Historical fault counts for demo (asset_id -> fault_count in last 30 days)
    FAULT_HISTORY = {
        "WT-07": 3,
        "WT-03": 2,
        "WT-12": 2,
        "SP-05": 1,
        "SP-11": 2,
        "SP-17": 1,
    }

    # Days since last maintenance
    LAST_MAINTENANCE = {
        "WT-07": 4,
        "WT-03": 3,
        "WT-12": 6,
        "SP-05": 1,
        "SP-11": 5,
        "SP-17": 7,
    }

    def analyze(
        self,
        solar_assets: List[SolarAsset],
        wind_assets: List[WindAsset],
        maintenance_history: List[MaintenanceRecord],
    ) -> Tuple[List[MaintenanceRisk], List[AgentActivity]]:
        risks = []
        activities = []
        now = datetime.now().isoformat()

        for a in wind_assets:
            score = self._wind_risk_score(a)
            level = self._score_to_level(score)
            issue, inspection, trend = self._wind_diagnosis(a, score)

            if score > 20:
                risks.append(MaintenanceRisk(
                    asset_id=a.asset_id,
                    asset_name=a.name,
                    asset_type=AssetType.WIND,
                    location=a.location,
                    risk_score=score,
                    risk_level=level,
                    performance_decline_pct=max(0, 100 - a.efficiency),
                    possible_issue=issue,
                    recommended_inspection=inspection,
                    priority=self._level_to_priority(level),
                    degradation_trend=trend,
                    last_maintenance=self._last_maint_label(a.asset_id),
                    fault_history=self.FAULT_HISTORY.get(a.asset_id, 0),
                ))
                if level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                    activities.append(AgentActivity(
                        timestamp=now,
                        agent_name=self.NAME,
                        activity=f"{a.asset_id} maintenance risk elevated to {level.value} (score: {score}/100)",
                        severity="alert" if level == RiskLevel.CRITICAL else "warning",
                    ))

        for a in solar_assets:
            score = self._solar_risk_score(a)
            level = self._score_to_level(score)
            issue, inspection, trend = self._solar_diagnosis(a, score)

            if score > 20:
                risks.append(MaintenanceRisk(
                    asset_id=a.asset_id,
                    asset_name=a.name,
                    asset_type=AssetType.SOLAR,
                    location=a.location,
                    risk_score=score,
                    risk_level=level,
                    performance_decline_pct=max(0, 100 - a.efficiency),
                    possible_issue=issue,
                    recommended_inspection=inspection,
                    priority=self._level_to_priority(level),
                    degradation_trend=trend,
                    last_maintenance=self._last_maint_label(a.asset_id),
                    fault_history=self.FAULT_HISTORY.get(a.asset_id, 0),
                ))

        # Sort by risk score descending
        risks.sort(key=lambda r: r.risk_score, reverse=True)
        return risks, activities

    def generate_recommendations(self, risks: List[MaintenanceRisk]) -> List[AgentRecommendation]:
        """
        Generate maintenance recommendations for high-risk assets.
        IMPORTANT: Recommendations only. No automatic execution.
        """
        recs = []
        now = datetime.now().isoformat()
        import uuid

        for risk in risks:
            if risk.risk_level not in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                continue

            urgency = "within 24 hours" if risk.risk_level == RiskLevel.CRITICAL else "within 48 hours"
            recs.append(AgentRecommendation(
                rec_id=str(uuid.uuid4())[:8],
                timestamp=now,
                agent_name=self.NAME,
                asset_id=risk.asset_id,
                recommendation_type="maintenance",
                title=f"Maintenance Required: {risk.asset_id}",
                description=(
                    f"{risk.asset_id} ({risk.asset_name}) has a maintenance risk score of "
                    f"{risk.risk_score}/100 ({risk.risk_level.value}). "
                    f"Consider scheduling {risk.recommended_inspection} {urgency}."
                ),
                reasoning=[
                    f"Risk score: {risk.risk_score}/100",
                    f"Performance decline: {risk.performance_decline_pct:.1f}%",
                    f"Possible issue: {risk.possible_issue}",
                    f"Degradation trend: {risk.degradation_trend}",
                    f"Fault history: {risk.fault_history} faults in last 30 days",
                ],
                confidence=min(95, 60 + risk.risk_score * 0.35),
                risk_level=risk.risk_level,
                safety_note=(
                    "⚠️ This is an AI recommendation only. No maintenance order has been created "
                    "or executed. Operator must approve before any physical inspection is scheduled."
                ),
            ))
        return recs

    # ─── Risk scoring ─────────────────────────────────────────────────────────

    def _wind_risk_score(self, a: WindAsset) -> float:
        score = 0.0

        # Performance degradation
        decline = max(0, 100 - a.efficiency)
        score += decline * 0.5

        # Vibration
        if a.vibration > 5.0:
            score += 30
        elif a.vibration > 3.5:
            score += 18

        # Generator temperature
        if a.generator_temperature > 90:
            score += 25
        elif a.generator_temperature > 80:
            score += 15
        elif a.generator_temperature > 70:
            score += 8

        # Fault history
        faults = self.FAULT_HISTORY.get(a.asset_id, 0)
        score += faults * 8

        # Time since maintenance
        days = self.LAST_MAINTENANCE.get(a.asset_id, 0)
        if days > 5:
            score += 10

        return min(100, round(score, 1))

    def _solar_risk_score(self, a: SolarAsset) -> float:
        score = 0.0
        decline = max(0, 100 - a.efficiency)
        score += decline * 0.45

        if a.panel_temperature > 75:
            score += 20
        elif a.panel_temperature > 65:
            score += 10

        if a.inverter_efficiency < 94:
            score += 20
        elif a.inverter_efficiency < 97:
            score += 8

        faults = self.FAULT_HISTORY.get(a.asset_id, 0)
        score += faults * 6

        days = self.LAST_MAINTENANCE.get(a.asset_id, 0)
        if days > 5:
            score += 8

        return min(100, round(score, 1))

    def _score_to_level(self, score: float) -> RiskLevel:
        if score >= 75:
            return RiskLevel.CRITICAL
        if score >= 55:
            return RiskLevel.HIGH
        if score >= 30:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _level_to_priority(self, level: RiskLevel) -> int:
        return {RiskLevel.CRITICAL: 1, RiskLevel.HIGH: 2, RiskLevel.MEDIUM: 3, RiskLevel.LOW: 4}[level]

    def _wind_diagnosis(self, a: WindAsset, score: float):
        if a.vibration > 3.5 and a.generator_temperature > 75:
            issue = "Mechanical degradation with bearing wear and thermal stress"
            inspection = "Full mechanical inspection including gearbox, bearings, and cooling system"
            trend = "Rapidly deteriorating"
        elif a.vibration > 3.5:
            issue = "Mechanical imbalance or bearing degradation"
            inspection = "Vibration analysis and bearing inspection"
            trend = "Deteriorating"
        elif a.efficiency < 75:
            issue = "Aerodynamic performance loss (blade degradation or yaw misalignment)"
            inspection = "Blade inspection and yaw system calibration"
            trend = "Gradual decline"
        elif a.generator_temperature > 75:
            issue = "Cooling system degradation"
            inspection = "Cooling system and generator inspection"
            trend = "Moderate deterioration"
        else:
            issue = "General performance degradation"
            inspection = "Routine inspection"
            trend = "Stable with minor decline"
        return issue, inspection, trend

    def _solar_diagnosis(self, a: SolarAsset, score: float):
        if a.inverter_efficiency < 95 and a.efficiency < 80:
            issue = "Inverter degradation and panel performance loss"
            inspection = "Inverter diagnostic and panel inspection"
            trend = "Deteriorating"
        elif a.efficiency < 80:
            issue = "Panel soiling, partial shading, or cell degradation"
            inspection = "Panel cleaning, shading analysis, and IV curve test"
            trend = "Gradual decline"
        elif a.panel_temperature > 70:
            issue = "Thermal management issue"
            inspection = "Ventilation and mounting inspection"
            trend = "Temperature trending up"
        else:
            issue = "Minor performance degradation"
            inspection = "Routine visual and electrical inspection"
            trend = "Stable"
        return issue, inspection, trend

    def _last_maint_label(self, asset_id: str) -> Optional[str]:
        days = self.LAST_MAINTENANCE.get(asset_id)
        if days is None:
            return None
        from datetime import timedelta
        d = (datetime.now() - timedelta(days=days)).date().isoformat()
        return d
