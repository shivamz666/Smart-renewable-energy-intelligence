"""
Weather-Based Generation Forecasting Agent
Uses simulated weather data to forecast solar and wind generation.
DATA: DEMO / SIMULATED DATA — clearly labeled throughout.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import math
import random
from ..models.asset_models import (
    WeatherData, ForecastPoint, AgentFinding, AgentActivity, RiskLevel
)


class ForecastingAgent:
    """
    Agent 3: Weather-Based Generation Forecasting
    Generates 6-hour and 24-hour forecasts for solar and wind generation.
    All forecasts are based on simulated weather data.
    DATA SOURCE: DEMO / SIMULATED DATA
    """
    NAME = "Weather & Forecasting Agent"

    # Gujarat average solar irradiance benchmark
    IRRADIANCE_GOOD = 700    # W/m²
    IRRADIANCE_MEDIUM = 400  # W/m²

    WIND_GOOD = 7.0    # m/s
    WIND_MEDIUM = 4.5  # m/s

    def analyze_weather_impact(
        self,
        kutch_weather: WeatherData,
        banas_weather: WeatherData,
    ) -> Tuple[List[AgentFinding], List[AgentActivity]]:
        """Analyze weather and detect conditions affecting generation."""
        findings = []
        activities = []
        now = datetime.now().isoformat()

        for weather in [kutch_weather, banas_weather]:
            # Cloud cover alert
            if weather.cloud_cover > 70:
                findings.append(AgentFinding(
                    agent_name=self.NAME,
                    asset_id=None,
                    finding_type="weather_alert",
                    severity="WARNING",
                    description=(
                        f"{weather.location.capitalize()}: High cloud cover ({weather.cloud_cover:.0f}%) "
                        f"is significantly reducing solar irradiance ({weather.solar_irradiance:.0f} W/m²). "
                        f"Solar generation will be below expected levels."
                    ),
                    data_source="SIMULATED WEATHER DATA",
                    timestamp=now,
                    details={
                        "location": weather.location,
                        "cloud_cover": weather.cloud_cover,
                        "irradiance": weather.solar_irradiance,
                    }
                ))
                activities.append(AgentActivity(
                    timestamp=now,
                    agent_name=self.NAME,
                    activity=f"Weather alert: High cloud cover in {weather.location} — solar generation reduced",
                    severity="warning",
                ))

            # Strong wind alert (positive)
            if weather.wind_speed > 10:
                activities.append(AgentActivity(
                    timestamp=now,
                    agent_name=self.NAME,
                    activity=f"Favorable wind conditions in {weather.location}: {weather.wind_speed:.1f} m/s — high wind generation expected",
                    severity="info",
                ))

            # Favorable solar
            if weather.solar_irradiance > self.IRRADIANCE_GOOD:
                activities.append(AgentActivity(
                    timestamp=now,
                    agent_name=self.NAME,
                    activity=f"Good solar irradiance in {weather.location}: {weather.solar_irradiance:.0f} W/m²",
                    severity="info",
                ))

        return findings, activities

    def generate_6h_forecast(
        self,
        kutch_weather: WeatherData,
        banas_weather: WeatherData,
        scenario: str = "normal",
    ) -> List[Dict[str, Any]]:
        """Generate 6-hour generation forecast."""
        forecast = []
        now = datetime.now()
        avg_irr = (kutch_weather.solar_irradiance + banas_weather.solar_irradiance) / 2
        avg_wind = (kutch_weather.wind_speed + banas_weather.wind_speed) / 2
        total_solar_cap = 196.0  # MW total solar capacity
        total_wind_cap = 36.0    # MW total wind capacity

        for i in range(1, 7):
            t = now + timedelta(hours=i)
            h = t.hour

            # Solar factor
            sol_factor = max(0, math.sin(math.pi * (h - 6) / 13)) if 6 <= h <= 19 else 0
            irr_factor = avg_irr / 950
            solar_f = total_solar_cap * sol_factor * irr_factor

            # Wind factor
            win_factor = self._wind_power_factor(avg_wind)
            wind_f = total_wind_cap * win_factor

            # Apply scenario
            if scenario == "weather_drop":
                solar_f *= max(0.2, 1 - i * 0.12)
                conf = 80 - i * 3
            elif scenario == "high_generation":
                solar_f *= 1.15
                wind_f *= 1.2
                conf = 90 - i * 1.5
            else:
                conf = 92 - i * 2

            # Add noise
            solar_f *= random.uniform(0.96, 1.04)
            wind_f *= random.uniform(0.95, 1.05)

            forecast.append({
                "hour": i,
                "timestamp": t.isoformat(),
                "label": t.strftime("%H:%M"),
                "solar_forecast_mw": round(max(0, solar_f), 2),
                "wind_forecast_mw": round(max(0, wind_f), 2),
                "total_forecast_mw": round(max(0, solar_f + wind_f), 2),
                "confidence": round(max(50, conf), 1),
                "data_source": "SIMULATED FORECAST DATA",
            })
        return forecast

    def generate_24h_forecast(
        self,
        kutch_weather: WeatherData,
        banas_weather: WeatherData,
        scenario: str = "normal",
    ) -> List[Dict[str, Any]]:
        """Generate 24-hour generation forecast."""
        forecast = []
        now = datetime.now()
        avg_irr = (kutch_weather.solar_irradiance + banas_weather.solar_irradiance) / 2
        avg_wind = (kutch_weather.wind_speed + banas_weather.wind_speed) / 2
        total_solar_cap = 196.0
        total_wind_cap = 36.0

        for i in range(1, 25):
            t = now + timedelta(hours=i)
            h = t.hour
            sol_factor = max(0, math.sin(math.pi * (h - 6) / 13)) if 6 <= h <= 19 else 0
            irr_factor = avg_irr / 950
            solar_f = total_solar_cap * sol_factor * irr_factor
            win_factor = self._wind_power_factor(avg_wind)
            wind_f = total_wind_cap * win_factor

            if scenario == "weather_drop" and i <= 6:
                solar_f *= max(0.2, 1 - i * 0.1)

            conf = max(50, 90 - i * 1.8)
            solar_f *= random.uniform(0.93, 1.07)
            wind_f *= random.uniform(0.93, 1.07)

            forecast.append({
                "hour": i,
                "timestamp": t.isoformat(),
                "label": t.strftime("%d %b %H:%M"),
                "solar_forecast_mw": round(max(0, solar_f), 2),
                "wind_forecast_mw": round(max(0, wind_f), 2),
                "total_forecast_mw": round(max(0, solar_f + wind_f), 2),
                "confidence": round(max(40, conf), 1),
                "data_source": "SIMULATED FORECAST DATA",
            })
        return forecast

    def get_generation_summary(
        self,
        forecast_6h: List[Dict],
        current_solar: float,
        current_wind: float,
    ) -> Dict[str, Any]:
        """Summarize generation outlook."""
        avg_total_6h = sum(f["total_forecast_mw"] for f in forecast_6h) / max(1, len(forecast_6h))
        trend = "stable"
        if avg_total_6h > (current_solar + current_wind) * 1.1:
            trend = "increasing"
        elif avg_total_6h < (current_solar + current_wind) * 0.9:
            trend = "decreasing"

        return {
            "current_solar_mw": round(current_solar, 2),
            "current_wind_mw": round(current_wind, 2),
            "current_total_mw": round(current_solar + current_wind, 2),
            "forecast_avg_6h_mw": round(avg_total_6h, 2),
            "generation_trend": trend,
            "data_source": "SIMULATED DATA",
        }

    def _wind_power_factor(self, wind_speed: float) -> float:
        if wind_speed < 3 or wind_speed > 25:
            return 0.0
        if wind_speed >= 12:
            return 1.0
        return ((wind_speed - 3) / (12 - 3)) ** 2.5
