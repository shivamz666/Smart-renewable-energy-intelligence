"""
Data Simulator for Smart Renewable Energy Platform.
Generates realistic simulated sensor data for Kutch and Banaskantha locations.
All data is clearly labeled as DEMO / SIMULATED DATA.
"""
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..models.asset_models import (
    SolarAsset, WindAsset, Substation, WeatherData, GridStatus, StorageStatus,
    MaintenanceRecord, AssetStatus, AssetHealth, AssetType, GenerationDataPoint,
    ForecastPoint, RiskLevel
)


# ─── Static asset definitions ────────────────────────────────────────────────

SOLAR_ASSETS_DEF = [
    # Kutch Solar Farm (12 panels)
    {"id": "SP-01", "name": "Kutch Solar Array 1",  "loc": "kutch",       "cap": 10.0, "lat": 23.75, "lon": 69.85},
    {"id": "SP-02", "name": "Kutch Solar Array 2",  "loc": "kutch",       "cap": 10.0, "lat": 23.74, "lon": 69.86},
    {"id": "SP-03", "name": "Kutch Solar Array 3",  "loc": "kutch",       "cap": 8.0,  "lat": 23.73, "lon": 69.84},
    {"id": "SP-04", "name": "Kutch Solar Array 4",  "loc": "kutch",       "cap": 8.0,  "lat": 23.76, "lon": 69.87},
    {"id": "SP-05", "name": "Kutch Solar Array 5",  "loc": "kutch",       "cap": 12.0, "lat": 23.72, "lon": 69.88},
    {"id": "SP-06", "name": "Kutch Solar Array 6",  "loc": "kutch",       "cap": 12.0, "lat": 23.77, "lon": 69.83},
    {"id": "SP-07", "name": "Kutch Solar Array 7",  "loc": "kutch",       "cap": 10.0, "lat": 23.71, "lon": 69.90},
    {"id": "SP-08", "name": "Kutch Solar Array 8",  "loc": "kutch",       "cap": 10.0, "lat": 23.78, "lon": 69.82},
    {"id": "SP-09", "name": "Kutch Solar Array 9",  "loc": "kutch",       "cap": 8.0,  "lat": 23.70, "lon": 69.91},
    {"id": "SP-10", "name": "Kutch Solar Array 10", "loc": "kutch",       "cap": 8.0,  "lat": 23.79, "lon": 69.81},
    {"id": "SP-11", "name": "Kutch Solar Array 11", "loc": "kutch",       "cap": 6.0,  "lat": 23.69, "lon": 69.92},
    {"id": "SP-12", "name": "Kutch Solar Array 12", "loc": "kutch",       "cap": 6.0,  "lat": 23.80, "lon": 69.80},
    # Banaskantha Solar Farm (8 panels)
    {"id": "SP-13", "name": "Banas Solar Array 1",  "loc": "banaskantha", "cap": 10.0, "lat": 24.18, "lon": 72.44},
    {"id": "SP-14", "name": "Banas Solar Array 2",  "loc": "banaskantha", "cap": 10.0, "lat": 24.17, "lon": 72.45},
    {"id": "SP-15", "name": "Banas Solar Array 3",  "loc": "banaskantha", "cap": 8.0,  "lat": 24.16, "lon": 72.43},
    {"id": "SP-16", "name": "Banas Solar Array 4",  "loc": "banaskantha", "cap": 8.0,  "lat": 24.19, "lon": 72.46},
    {"id": "SP-17", "name": "Banas Solar Array 5",  "loc": "banaskantha", "cap": 12.0, "lat": 24.15, "lon": 72.47},
    {"id": "SP-18", "name": "Banas Solar Array 6",  "loc": "banaskantha", "cap": 12.0, "lat": 24.20, "lon": 72.42},
    {"id": "SP-19", "name": "Banas Solar Array 7",  "loc": "banaskantha", "cap": 6.0,  "lat": 24.14, "lon": 72.48},
    {"id": "SP-20", "name": "Banas Solar Array 8",  "loc": "banaskantha", "cap": 6.0,  "lat": 24.21, "lon": 72.41},
]

WIND_ASSETS_DEF = [
    # Kutch Wind Farm (9 turbines)
    {"id": "WT-01", "name": "Kutch Wind Turbine 1",  "loc": "kutch",       "cap": 2.5, "lat": 23.74, "lon": 69.83},
    {"id": "WT-02", "name": "Kutch Wind Turbine 2",  "loc": "kutch",       "cap": 2.5, "lat": 23.75, "lon": 69.84},
    {"id": "WT-03", "name": "Kutch Wind Turbine 3",  "loc": "kutch",       "cap": 2.0, "lat": 23.76, "lon": 69.82},
    {"id": "WT-04", "name": "Kutch Wind Turbine 4",  "loc": "kutch",       "cap": 2.0, "lat": 23.73, "lon": 69.85},
    {"id": "WT-05", "name": "Kutch Wind Turbine 5",  "loc": "kutch",       "cap": 3.0, "lat": 23.77, "lon": 69.81},
    {"id": "WT-06", "name": "Kutch Wind Turbine 6",  "loc": "kutch",       "cap": 3.0, "lat": 23.72, "lon": 69.86},
    {"id": "WT-07", "name": "Kutch Wind Turbine 7",  "loc": "kutch",       "cap": 2.5, "lat": 23.78, "lon": 69.80},  # Problem turbine
    {"id": "WT-08", "name": "Kutch Wind Turbine 8",  "loc": "kutch",       "cap": 2.0, "lat": 23.71, "lon": 69.87},
    {"id": "WT-09", "name": "Kutch Wind Turbine 9",  "loc": "kutch",       "cap": 2.0, "lat": 23.79, "lon": 69.79},
    # Banaskantha Wind Farm (6 turbines)
    {"id": "WT-10", "name": "Banas Wind Turbine 1",  "loc": "banaskantha", "cap": 2.5, "lat": 24.17, "lon": 72.43},
    {"id": "WT-11", "name": "Banas Wind Turbine 2",  "loc": "banaskantha", "cap": 2.5, "lat": 24.18, "lon": 72.44},
    {"id": "WT-12", "name": "Banas Wind Turbine 3",  "loc": "banaskantha", "cap": 2.0, "lat": 24.19, "lon": 72.45},
    {"id": "WT-13", "name": "Banas Wind Turbine 4",  "loc": "banaskantha", "cap": 2.0, "lat": 24.16, "lon": 72.42},
    {"id": "WT-14", "name": "Banas Wind Turbine 5",  "loc": "banaskantha", "cap": 3.0, "lat": 24.20, "lon": 72.46},
    {"id": "WT-15", "name": "Banas Wind Turbine 6",  "loc": "banaskantha", "cap": 2.5, "lat": 24.15, "lon": 72.41},
]

SUBSTATIONS_DEF = [
    {"id": "SS-01", "name": "Kutch Main Substation",        "loc": "kutch",       "cap_mva": 200, "lat": 23.74, "lon": 69.85},
    {"id": "SS-02", "name": "Banas Main Substation",        "loc": "banaskantha", "cap_mva": 150, "lat": 24.18, "lon": 72.44},
    {"id": "SS-03", "name": "Kutch-Banas Interconnect",     "loc": "kutch",       "cap_mva": 100, "lat": 23.80, "lon": 70.20},
]


class DataSimulator:
    """
    Simulates realistic renewable energy sensor data.
    DATA SOURCE: DEMO / SIMULATED DATA
    """

    def __init__(self):
        self._scenario: str = "normal"
        self._scenario_step: int = 0
        self._historical_cache: Optional[List[Dict]] = None
        random.seed(42)

    def set_scenario(self, scenario: str):
        self._scenario = scenario
        self._scenario_step = 0

    def _time_factor(self) -> float:
        """Solar irradiance factor based on hour of day."""
        hour = datetime.now().hour
        if hour < 6 or hour > 19:
            return 0.0
        return math.sin(math.pi * (hour - 6) / 13) * 0.9 + random.uniform(-0.05, 0.05)

    def _get_weather_base(self, location: str) -> Dict:
        hour = datetime.now().hour
        base_irr = max(0, self._time_factor() * 950)
        base_wind = random.uniform(5.5, 8.5)
        base_temp = 32 + math.sin(math.pi * hour / 12) * 6 + random.uniform(-2, 2)
        base_cloud = random.uniform(10, 30)

        if location == "kutch":
            base_wind += 1.5
            base_irr *= 1.05
        else:
            base_temp -= 2

        return {
            "irradiance": max(0, base_irr),
            "wind_speed": base_wind,
            "temperature": base_temp,
            "cloud_cover": base_cloud,
            "humidity": random.uniform(35, 65),
            "wind_direction": random.uniform(200, 280),
            "pressure": random.uniform(1008, 1018),
        }

    def get_weather(self, location: str) -> WeatherData:
        w = self._get_weather_base(location)

        # Apply scenario modifiers
        if self._scenario == "weather_drop":
            w["cloud_cover"] = min(95, w["cloud_cover"] + 55)
            w["irradiance"] = max(50, w["irradiance"] * 0.3)
            condition = "Heavy Cloud Cover"
        elif self._scenario == "high_generation":
            w["cloud_cover"] = max(5, w["cloud_cover"] - 15)
            w["irradiance"] = min(1050, w["irradiance"] * 1.2)
            w["wind_speed"] = min(15, w["wind_speed"] * 1.3)
            condition = "Clear & Windy"
        else:
            if w["cloud_cover"] < 20:
                condition = "Clear & Sunny"
            elif w["cloud_cover"] < 50:
                condition = "Partly Cloudy"
            else:
                condition = "Cloudy"

        return WeatherData(
            location=location,
            timestamp=datetime.now().isoformat(),
            temperature=round(w["temperature"], 1),
            wind_speed=round(w["wind_speed"], 2),
            wind_direction=round(w["wind_direction"], 1),
            solar_irradiance=round(w["irradiance"], 1),
            cloud_cover=round(w["cloud_cover"], 1),
            humidity=round(w["humidity"], 1),
            condition=condition,
            pressure=round(w["pressure"], 1),
        )

    def _solar_output(self, cap_mw: float, irradiance: float, temp: float) -> float:
        """Calculate solar output with temperature derating."""
        stc_irr = 1000.0
        temp_coeff = -0.004  # -0.4%/°C
        ref_temp = 25.0
        base = cap_mw * (irradiance / stc_irr)
        temp_factor = 1 + temp_coeff * (temp - ref_temp)
        return max(0, base * temp_factor)

    def _wind_output(self, cap_mw: float, wind_speed: float) -> float:
        """Power curve model: cut-in=3m/s, rated=12m/s, cut-out=25m/s."""
        if wind_speed < 3 or wind_speed > 25:
            return 0.0
        if wind_speed >= 12:
            return cap_mw
        # Cubic interpolation between cut-in and rated
        ratio = (wind_speed - 3) / (12 - 3)
        return cap_mw * (ratio ** 2.5)

    def get_solar_assets(self) -> List[SolarAsset]:
        assets = []
        for d in SOLAR_ASSETS_DEF:
            w = self._get_weather_base(d["loc"])

            # Apply scenario modifiers
            noise = random.uniform(0.95, 1.05)
            if self._scenario == "weather_drop":
                w["irradiance"] = max(50, w["irradiance"] * 0.3)
                noise *= 0.5
            elif self._scenario == "high_generation":
                w["irradiance"] = min(1050, w["irradiance"] * 1.2)
                noise *= 1.05

            expected = self._solar_output(d["cap"], w["irradiance"], w["temperature"])
            actual = expected * noise * random.uniform(0.92, 1.0)

            # Inject degradation for some panels
            if d["id"] in ["SP-05", "SP-11", "SP-17"]:
                actual *= 0.82
            if d["id"] == "SP-07" and self._scenario == "weather_drop":
                actual *= 0.55

            eff = (actual / expected * 100) if expected > 0 else 100.0
            dev = ((actual - expected) / expected * 100) if expected > 0 else 0.0

            status = AssetStatus.HEALTHY
            if eff < 70:
                status = AssetStatus.CRITICAL
            elif eff < 85:
                status = AssetStatus.WARNING

            panel_temp = w["temperature"] + (w["irradiance"] / 1000) * 28
            inverter_eff = random.uniform(96.0, 99.0)

            assets.append(SolarAsset(
                asset_id=d["id"],
                name=d["name"],
                location=d["loc"],
                lat=d["lat"],
                lon=d["lon"],
                capacity_mw=d["cap"],
                actual_output_mw=round(actual, 3),
                expected_output_mw=round(expected, 3),
                solar_irradiance=round(w["irradiance"], 1),
                panel_temperature=round(panel_temp, 1),
                voltage=round(600 + random.uniform(-20, 20), 1),
                current=round((actual * 1000) / 600 if actual > 0 else 0, 2),
                inverter_efficiency=round(inverter_eff, 2),
                efficiency=round(eff, 2),
                performance_deviation=round(dev, 2),
                status=status,
                last_updated=datetime.now().isoformat(),
            ))
        return assets

    def get_wind_assets(self) -> List[WindAsset]:
        assets = []
        for d in WIND_ASSETS_DEF:
            w = self._get_weather_base(d["loc"])
            noise = random.uniform(0.95, 1.05)

            if self._scenario == "high_generation":
                w["wind_speed"] = min(15, w["wind_speed"] * 1.3)
            elif self._scenario == "underperformance" and d["id"] == "WT-07":
                pass  # WT-07 underperforms despite normal wind

            expected = self._wind_output(d["cap"], w["wind_speed"])
            actual = expected * noise * random.uniform(0.93, 1.0)

            # Inject underperformance for WT-07 (the problem turbine)
            if d["id"] == "WT-07":
                actual *= 0.78 if self._scenario == "underperformance" else 0.85
            if d["id"] in ["WT-03", "WT-12"]:
                actual *= 0.88

            eff = (actual / expected * 100) if expected > 0 else 100.0
            dev = ((actual - expected) / expected * 100) if expected > 0 else 0.0

            status = AssetStatus.HEALTHY
            if eff < 70:
                status = AssetStatus.CRITICAL
            elif eff < 85:
                status = AssetStatus.WARNING

            gen_temp = 65 + random.uniform(-5, 10)
            if d["id"] == "WT-07":
                gen_temp += 15  # Elevated temperature

            vibration = random.uniform(0.5, 2.0)
            if d["id"] == "WT-07":
                vibration += random.uniform(1.5, 3.5)  # Abnormal vibration

            assets.append(WindAsset(
                asset_id=d["id"],
                name=d["name"],
                location=d["loc"],
                lat=d["lat"],
                lon=d["lon"],
                capacity_mw=d["cap"],
                actual_output_mw=round(actual, 3),
                expected_output_mw=round(expected, 3),
                wind_speed=round(w["wind_speed"], 2),
                wind_direction=round(w["wind_direction"], 1),
                turbine_rpm=round(8 + (w["wind_speed"] / 15) * 12, 1),
                generator_temperature=round(gen_temp, 1),
                vibration=round(vibration, 3),
                turbine_efficiency=round(eff, 2),
                efficiency=round(eff, 2),
                performance_deviation=round(dev, 2),
                status=status,
                last_updated=datetime.now().isoformat(),
            ))
        return assets

    def get_substations(self) -> List[Substation]:
        result = []
        for d in SUBSTATIONS_DEF:
            load = random.uniform(60, 90) * d["cap_mva"] / 100
            result.append(Substation(
                asset_id=d["id"],
                name=d["name"],
                location=d["loc"],
                lat=d["lat"],
                lon=d["lon"],
                voltage_kv=random.uniform(219, 221),
                load_mva=round(load, 1),
                capacity_mva=d["cap_mva"],
                status=AssetStatus.HEALTHY,
            ))
        return result

    def get_storage(self) -> List[StorageStatus]:
        capacities = [
            ("BESS-01", "Kutch Battery Storage 1",  "kutch",       50.0),
            ("BESS-02", "Kutch Battery Storage 2",  "kutch",       30.0),
            ("BESS-03", "Banas Battery Storage 1",  "banaskantha", 40.0),
        ]
        result = []
        soc_mod = 1.3 if self._scenario == "high_generation" else 1.0
        for sid, name, loc, cap in capacities:
            soc = min(100, random.uniform(35, 70) * soc_mod)
            current_charge = cap * soc / 100
            result.append(StorageStatus(
                storage_id=sid,
                name=name,
                location=loc,
                capacity_mwh=cap,
                current_charge_mwh=round(current_charge, 2),
                state_of_charge_pct=round(soc, 1),
                charging_rate_mw=round(random.uniform(0, 8), 2),
                discharging_rate_mw=round(random.uniform(0, 5), 2),
                status="OPERATIONAL",
            ))
        return result

    def get_grid_status(self, solar_mw: float, wind_mw: float) -> GridStatus:
        hour = datetime.now().hour
        base_demand = 55 + 25 * math.sin(math.pi * (hour - 8) / 14)
        demand = max(30, base_demand + random.uniform(-5, 5))

        if self._scenario == "high_generation":
            demand *= 0.85

        total_renewable = solar_mw + wind_mw
        surplus = total_renewable - demand
        export = max(0, surplus * 0.6)
        imp = max(0, -surplus * 0.4)

        return GridStatus(
            timestamp=datetime.now().isoformat(),
            renewable_generation_mw=round(total_renewable, 2),
            total_demand_mw=round(demand, 2),
            grid_export_mw=round(export, 2),
            grid_import_mw=round(imp, 2),
            frequency_hz=round(50.0 + random.uniform(-0.05, 0.05), 3),
            voltage_kv=round(220 + random.uniform(-2, 2), 1),
            renewable_share_pct=round(min(100, total_renewable / demand * 100), 1),
            surplus_mw=round(surplus, 2),
        )

    def get_historical_generation(self, hours: int = 24) -> List[GenerationDataPoint]:
        """Generate historical time-series generation data."""
        points = []
        now = datetime.now()
        for i in range(hours, 0, -1):
            t = now - timedelta(hours=i)
            h = t.hour
            sol_factor = max(0, math.sin(math.pi * (h - 6) / 13)) if 6 <= h <= 19 else 0
            win_factor = 0.6 + 0.4 * math.sin(math.pi * h / 12 + 1)
            solar = sol_factor * 155 * random.uniform(0.88, 1.0)
            wind = win_factor * 35 * random.uniform(0.85, 1.05)
            expected = (sol_factor * 165 + win_factor * 37)
            demand = 55 + 25 * math.sin(math.pi * (h - 8) / 14) + random.uniform(-3, 3)
            points.append(GenerationDataPoint(
                timestamp=t.isoformat(),
                solar_mw=round(solar, 2),
                wind_mw=round(wind, 2),
                total_mw=round(solar + wind, 2),
                expected_mw=round(expected, 2),
                demand_mw=round(max(30, demand), 2),
            ))
        return points

    def get_forecast(self, hours: int = 24) -> List[ForecastPoint]:
        """Generate generation forecast for next N hours."""
        points = []
        now = datetime.now()
        for i in range(1, hours + 1):
            t = now + timedelta(hours=i)
            h = t.hour
            sol_factor = max(0, math.sin(math.pi * (h - 6) / 13)) if 6 <= h <= 19 else 0
            win_factor = 0.6 + 0.4 * math.sin(math.pi * h / 12 + 1)

            if self._scenario == "weather_drop":
                sol_factor *= (0.5 - i * 0.04) if i <= 6 else 0.3
            if self._scenario == "high_generation":
                win_factor *= 1.25

            solar_f = sol_factor * 160 * random.uniform(0.9, 1.05)
            wind_f = win_factor * 36 * random.uniform(0.9, 1.05)
            conf = max(60, 95 - i * 1.5)
            points.append(ForecastPoint(
                timestamp=t.isoformat(),
                solar_forecast_mw=round(solar_f, 2),
                wind_forecast_mw=round(wind_f, 2),
                total_forecast_mw=round(solar_f + wind_f, 2),
                confidence=round(conf, 1),
            ))
        return points

    def get_maintenance_history(self) -> List[MaintenanceRecord]:
        """Return 7-day maintenance history."""
        records = []
        base = datetime.now() - timedelta(days=7)
        entries = [
            ("WT-07", "Scheduled Inspection",   2, "Vibration levels slightly elevated",     "Rahul Sharma",     "Monitoring required"),
            ("WT-07", "Oil Change",              4, "Routine lubrication service",            "Amit Patel",       "Completed"),
            ("SP-05", "Panel Cleaning",          1, "Dust accumulation removed",              "Priya Desai",      "Completed"),
            ("WT-03", "Blade Inspection",        3, "Minor surface erosion noted",            "Suresh Mehta",     "Next scheduled in 30 days"),
            ("SP-11", "Inverter Diagnostic",     5, "Inverter efficiency below threshold",    "Vikram Singh",     "Component replaced"),
            ("WT-12", "Gearbox Check",           6, "Oil leak identified and sealed",         "Anita Joshi",      "Follow-up in 7 days"),
            ("SP-17", "Electrical Inspection",   7, "Connection resistance slightly high",    "Ravi Kumar",       "Connections re-torqued"),
        ]
        for i, (aid, mtype, day_offset, desc, tech, outcome) in enumerate(entries):
            records.append(MaintenanceRecord(
                record_id=f"MR-{1000+i}",
                asset_id=aid,
                date=(base + timedelta(days=day_offset)).date().isoformat(),
                type=mtype,
                description=desc,
                technician=tech,
                outcome=outcome,
            ))
        return records


# Singleton instance
simulator = DataSimulator()
