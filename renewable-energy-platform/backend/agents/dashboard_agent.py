"""
Renewable Energy Dashboard Agent
Combines information from all other agents to generate a unified park summary.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models.asset_models import (
    AssetHealth, AssetStatus, GridStatus, StorageStatus, WeatherData,
    MaintenanceRisk, AgentRecommendation, ParkSummary, RiskLevel
)


class DashboardAgent:
    """
    Agent 5: Renewable Energy Dashboard Agent
    Aggregates and synthesizes data from all agents for unified view.
    """
    NAME = "Dashboard Agent"

    CO2_FACTOR = 0.82  # tons CO₂/MWh avoided (Indian grid average)

    def generate_park_summary(
        self,
        asset_health: List[AssetHealth],
        grid: GridStatus,
        storage: List[StorageStatus],
        weather_k: WeatherData,
        weather_b: WeatherData,
        maintenance_risks: List[MaintenanceRisk],
        recommendations: List[AgentRecommendation],
    ) -> ParkSummary:
        """Generate comprehensive park health summary."""

        # Asset counts
        healthy = sum(1 for a in asset_health if a.status == AssetStatus.HEALTHY)
        warning = sum(1 for a in asset_health if a.status == AssetStatus.WARNING)
        critical = sum(1 for a in asset_health if a.status == AssetStatus.CRITICAL)
        high_risk = sum(1 for r in maintenance_risks if r.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL))

        # Generation
        solar_total = sum(a.actual_output_mw for a in asset_health if "SP-" in a.asset_id or a.asset_type.value == "solar")
        wind_total = sum(a.actual_output_mw for a in asset_health if "WT-" in a.asset_id or a.asset_type.value == "wind")
        expected_total = sum(a.expected_output_mw for a in asset_health)
        actual_total = solar_total + wind_total

        park_eff = (actual_total / expected_total * 100) if expected_total > 0 else 0

        # Overall park status
        if critical > 0 or high_risk >= 3:
            overall = AssetStatus.WARNING
        elif warning > 3 or high_risk >= 1:
            overall = AssetStatus.WARNING
        else:
            overall = AssetStatus.HEALTHY

        # CO2 avoided
        co2 = actual_total * self.CO2_FACTOR

        # Health narrative
        narrative = self._build_narrative(
            overall, healthy, warning, critical, high_risk,
            solar_total, wind_total, park_eff, recommendations
        )

        # Weather summary
        avg_irr = (weather_k.solar_irradiance + weather_b.solar_irradiance) / 2
        avg_wind = (weather_k.wind_speed + weather_b.wind_speed) / 2
        weather_summary = f"{weather_k.condition} | Irradiance: {avg_irr:.0f} W/m² | Wind: {avg_wind:.1f} m/s"

        return ParkSummary(
            timestamp=datetime.now().isoformat(),
            overall_status=overall,
            health_summary=narrative,
            total_solar_mw=round(solar_total, 2),
            total_wind_mw=round(wind_total, 2),
            total_renewable_mw=round(actual_total, 2),
            expected_total_mw=round(expected_total, 2),
            park_efficiency=round(park_eff, 2),
            co2_avoided_tons_per_hour=round(co2, 2),
            healthy_assets=healthy,
            warning_assets=warning,
            critical_assets=critical,
            high_risk_assets=high_risk,
            active_recommendations=len(recommendations),
            grid_status=grid,
            weather_summary=weather_summary,
        )

    def _build_narrative(
        self,
        status: AssetStatus,
        healthy: int,
        warning: int,
        critical: int,
        high_risk: int,
        solar_mw: float,
        wind_mw: float,
        efficiency: float,
        recommendations: List[AgentRecommendation],
    ) -> str:
        total = healthy + warning + critical
        status_label = "GOOD" if status == AssetStatus.HEALTHY else "ATTENTION REQUIRED"

        parts = [f"Overall park health: {status_label}."]

        if solar_mw > 0:
            parts.append(f"Solar assets generating {solar_mw:.1f} MW.")
        if wind_mw > 0:
            parts.append(f"Wind assets generating {wind_mw:.1f} MW.")

        parts.append(f"Park efficiency: {efficiency:.1f}%.")

        if critical > 0:
            parts.append(f"{critical} asset(s) in CRITICAL state requiring immediate attention.")
        if warning > 0:
            parts.append(f"{warning} asset(s) showing WARNING performance.")
        if high_risk > 0:
            parts.append(f"{high_risk} asset(s) have high maintenance risk.")
        if healthy == total:
            parts.append("All assets operating within normal parameters.")

        if recommendations:
            parts.append(f"{len(recommendations)} active AI recommendation(s) awaiting operator review.")

        return " ".join(parts)

    def get_kpi_cards(
        self,
        asset_health: List[AssetHealth],
        grid: GridStatus,
        storage: List[StorageStatus],
    ) -> Dict[str, Any]:
        """Generate KPI card data for dashboard."""
        solar_mw = sum(a.actual_output_mw for a in asset_health if "SP-" in a.asset_id)
        wind_mw = sum(a.actual_output_mw for a in asset_health if "WT-" in a.asset_id)
        expected_mw = sum(a.expected_output_mw for a in asset_health)
        actual_mw = solar_mw + wind_mw
        efficiency = (actual_mw / expected_mw * 100) if expected_mw > 0 else 0
        co2 = actual_mw * self.CO2_FACTOR
        total_storage = sum(s.capacity_mwh for s in storage)
        current_charge = sum(s.current_charge_mwh for s in storage)

        return {
            "solar_generation_mw": round(solar_mw, 2),
            "wind_generation_mw": round(wind_mw, 2),
            "total_renewable_mw": round(actual_mw, 2),
            "expected_generation_mw": round(expected_mw, 2),
            "park_efficiency_pct": round(efficiency, 2),
            "grid_demand_mw": round(grid.total_demand_mw, 2),
            "grid_export_mw": round(grid.grid_export_mw, 2),
            "grid_import_mw": round(grid.grid_import_mw, 2),
            "storage_available_mwh": round(total_storage - current_charge, 2),
            "storage_soc_pct": round(current_charge / total_storage * 100, 1) if total_storage > 0 else 0,
            "co2_avoided_tons_hr": round(co2, 2),
            "renewable_share_pct": grid.renewable_share_pct,
            "data_source": "SIMULATED DATA",
        }
