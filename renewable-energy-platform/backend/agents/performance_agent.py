"""
Asset Performance Monitoring Agent
Monitors solar and wind assets, detects anomalies, classifies health status.
"""
from datetime import datetime
from typing import List, Dict, Any, Tuple
from ..models.asset_models import (
    SolarAsset, WindAsset, AssetStatus, AssetHealth, AssetType,
    AgentFinding, RiskLevel, AgentActivity
)


class PerformanceAgent:
    """
    Agent 1: Asset Performance Monitoring
    Analyzes real-time asset performance and detects anomalies.
    DATA SOURCE: Simulated sensor data
    """
    NAME = "Performance Monitoring Agent"

    EFFICIENCY_THRESHOLDS = {
        "healthy": 85.0,
        "warning": 70.0,
        "critical": 0.0,
    }

    WIND_VIBRATION_NORMAL = 3.5   # mm/s
    WIND_TEMP_HIGH = 85.0          # °C
    SOLAR_TEMP_HIGH = 75.0         # °C

    def analyze_solar_assets(self, assets: List[SolarAsset]) -> Tuple[List[AgentFinding], List[AgentActivity]]:
        findings = []
        activities = []
        now = datetime.now().isoformat()

        for asset in assets:
            if asset.efficiency < self.EFFICIENCY_THRESHOLDS["healthy"]:
                severity = "WARNING" if asset.efficiency >= self.EFFICIENCY_THRESHOLDS["warning"] else "CRITICAL"
                detail_msg = self._diagnose_solar(asset)
                findings.append(AgentFinding(
                    agent_name=self.NAME,
                    asset_id=asset.asset_id,
                    finding_type="performance_deviation",
                    severity=severity,
                    description=(
                        f"{asset.asset_id} is producing {abs(asset.performance_deviation):.1f}% "
                        f"{'less' if asset.performance_deviation < 0 else 'more'} power than expected. "
                        f"{detail_msg}"
                    ),
                    data_source="SIMULATED SENSOR DATA",
                    timestamp=now,
                    details={
                        "efficiency": asset.efficiency,
                        "actual_mw": asset.actual_output_mw,
                        "expected_mw": asset.expected_output_mw,
                        "deviation_pct": asset.performance_deviation,
                        "irradiance": asset.solar_irradiance,
                        "panel_temp": asset.panel_temperature,
                    }
                ))
                activities.append(AgentActivity(
                    timestamp=now,
                    agent_name=self.NAME,
                    activity=f"Anomaly detected: {asset.asset_id} efficiency {asset.efficiency:.1f}%",
                    severity="warning" if severity == "WARNING" else "alert",
                ))

            if asset.panel_temperature > self.SOLAR_TEMP_HIGH:
                findings.append(AgentFinding(
                    agent_name=self.NAME,
                    asset_id=asset.asset_id,
                    finding_type="high_temperature",
                    severity="WARNING",
                    description=(
                        f"{asset.asset_id} panel temperature is {asset.panel_temperature:.1f}°C, "
                        f"exceeding normal operating range. AI Analysis: High temperature can reduce "
                        f"output and may indicate soiling or poor ventilation."
                    ),
                    data_source="SIMULATED SENSOR DATA",
                    timestamp=now,
                    details={"panel_temp": asset.panel_temperature},
                ))

        return findings, activities

    def analyze_wind_assets(self, assets: List[WindAsset]) -> Tuple[List[AgentFinding], List[AgentActivity]]:
        findings = []
        activities = []
        now = datetime.now().isoformat()

        for asset in assets:
            # Performance deviation detection
            if asset.wind_speed >= 3 and asset.efficiency < self.EFFICIENCY_THRESHOLDS["healthy"]:
                severity = "WARNING" if asset.efficiency >= self.EFFICIENCY_THRESHOLDS["warning"] else "CRITICAL"
                findings.append(AgentFinding(
                    agent_name=self.NAME,
                    asset_id=asset.asset_id,
                    finding_type="performance_deviation",
                    severity=severity,
                    description=(
                        f"{asset.asset_id} is producing {abs(asset.performance_deviation):.1f}% less power "
                        f"than expected even though wind speed ({asset.wind_speed:.1f} m/s) is within "
                        f"optimal operating range. AI Analysis: {self._diagnose_wind(asset)}"
                    ),
                    data_source="SIMULATED SENSOR DATA",
                    timestamp=now,
                    details={
                        "efficiency": asset.efficiency,
                        "actual_mw": asset.actual_output_mw,
                        "expected_mw": asset.expected_output_mw,
                        "deviation_pct": asset.performance_deviation,
                        "wind_speed": asset.wind_speed,
                        "vibration": asset.vibration,
                        "generator_temp": asset.generator_temperature,
                    }
                ))
                activities.append(AgentActivity(
                    timestamp=now,
                    agent_name=self.NAME,
                    activity=f"Underperformance: {asset.asset_id} at {asset.efficiency:.1f}% efficiency despite {asset.wind_speed:.1f} m/s wind",
                    severity="warning" if severity == "WARNING" else "alert",
                ))

            # Vibration alert
            if asset.vibration > self.WIND_VIBRATION_NORMAL:
                findings.append(AgentFinding(
                    agent_name=self.NAME,
                    asset_id=asset.asset_id,
                    finding_type="abnormal_vibration",
                    severity="WARNING" if asset.vibration < 5.0 else "CRITICAL",
                    description=(
                        f"{asset.asset_id} vibration level {asset.vibration:.2f} mm/s exceeds normal "
                        f"threshold ({self.WIND_VIBRATION_NORMAL} mm/s). "
                        f"AI Analysis: Abnormal vibration may indicate mechanical imbalance, blade damage, "
                        f"or bearing wear. This is AI analysis — physical inspection required to confirm."
                    ),
                    data_source="SIMULATED SENSOR DATA",
                    timestamp=now,
                    details={"vibration": asset.vibration, "threshold": self.WIND_VIBRATION_NORMAL},
                ))

            # Temperature alert
            if asset.generator_temperature > self.WIND_TEMP_HIGH:
                findings.append(AgentFinding(
                    agent_name=self.NAME,
                    asset_id=asset.asset_id,
                    finding_type="high_generator_temperature",
                    severity="WARNING",
                    description=(
                        f"{asset.asset_id} generator temperature {asset.generator_temperature:.1f}°C "
                        f"is above normal operating range. AI Analysis: May indicate cooling system issue "
                        f"or increased mechanical friction."
                    ),
                    data_source="SIMULATED SENSOR DATA",
                    timestamp=now,
                    details={"generator_temp": asset.generator_temperature},
                ))

        return findings, activities

    def get_asset_health_list(
        self,
        solar_assets: List[SolarAsset],
        wind_assets: List[WindAsset],
        maintenance_risks: Dict[str, float] = None,
    ) -> List[AssetHealth]:
        """Combine all assets into unified health list."""
        health_list = []
        mr = maintenance_risks or {}

        for a in solar_assets:
            risk_score = mr.get(a.asset_id, self._estimate_solar_risk(a))
            health_list.append(AssetHealth(
                asset_id=a.asset_id,
                asset_type=AssetType.SOLAR,
                name=a.name,
                location=a.location,
                actual_output_mw=a.actual_output_mw,
                expected_output_mw=a.expected_output_mw,
                efficiency=a.efficiency,
                risk_score=risk_score,
                risk_level=self._score_to_risk(risk_score),
                status=a.status,
                lat=a.lat,
                lon=a.lon,
            ))

        for a in wind_assets:
            risk_score = mr.get(a.asset_id, self._estimate_wind_risk(a))
            health_list.append(AssetHealth(
                asset_id=a.asset_id,
                asset_type=AssetType.WIND,
                name=a.name,
                location=a.location,
                actual_output_mw=a.actual_output_mw,
                expected_output_mw=a.expected_output_mw,
                efficiency=a.efficiency,
                risk_score=risk_score,
                risk_level=self._score_to_risk(risk_score),
                status=a.status,
                lat=a.lat,
                lon=a.lon,
            ))

        return health_list

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _diagnose_solar(self, a: SolarAsset) -> str:
        causes = []
        if a.solar_irradiance < 400:
            causes.append("low solar irradiance")
        if a.panel_temperature > self.SOLAR_TEMP_HIGH:
            causes.append("elevated panel temperature causing thermal derating")
        if a.inverter_efficiency < 95:
            causes.append("reduced inverter efficiency")
        if not causes:
            causes.append("potential soiling, shading, or panel degradation")
        return f"AI Analysis (not confirmed): Possible causes include {', '.join(causes)}."

    def _diagnose_wind(self, a: WindAsset) -> str:
        causes = []
        if a.vibration > self.WIND_VIBRATION_NORMAL:
            causes.append("abnormal vibration suggesting mechanical issue")
        if a.generator_temperature > self.WIND_TEMP_HIGH:
            causes.append("elevated generator temperature")
        if a.turbine_rpm < 5:
            causes.append("lower than expected RPM")
        if not causes:
            causes.append("possible blade degradation or yaw misalignment")
        return f"Possible causes include {', '.join(causes)}. Physical inspection required to confirm."

    def _estimate_solar_risk(self, a: SolarAsset) -> float:
        score = 0.0
        if a.efficiency < 70:
            score += 40
        elif a.efficiency < 85:
            score += 20
        if a.panel_temperature > self.SOLAR_TEMP_HIGH:
            score += 20
        if a.inverter_efficiency < 95:
            score += 15
        score += max(0, 100 - a.efficiency) * 0.3
        return min(100, round(score, 1))

    def _estimate_wind_risk(self, a: WindAsset) -> float:
        score = 0.0
        if a.efficiency < 70:
            score += 40
        elif a.efficiency < 85:
            score += 20
        if a.vibration > self.WIND_VIBRATION_NORMAL:
            score += 25 + (a.vibration - self.WIND_VIBRATION_NORMAL) * 5
        if a.generator_temperature > self.WIND_TEMP_HIGH:
            score += 15
        score += max(0, 100 - a.efficiency) * 0.25
        return min(100, round(score, 1))

    def _score_to_risk(self, score: float) -> RiskLevel:
        if score >= 75:
            return RiskLevel.CRITICAL
        if score >= 55:
            return RiskLevel.HIGH
        if score >= 30:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
