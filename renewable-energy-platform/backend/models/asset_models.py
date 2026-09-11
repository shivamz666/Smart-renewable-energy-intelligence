"""
Pydantic data models for the Smart Renewable Energy Platform.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class AssetType(str, Enum):
    SOLAR = "solar"
    WIND = "wind"
    SUBSTATION = "substation"
    STORAGE = "storage"


class AssetStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HumanDecision(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IGNORED = "IGNORED"


class ScenarioType(str, Enum):
    UNDERPERFORMANCE = "underperformance"
    HIGH_GENERATION = "high_generation"
    WEATHER_DROP = "weather_drop"
    NORMAL = "normal"


class SolarAsset(BaseModel):
    asset_id: str
    name: str
    location: str
    lat: float
    lon: float
    capacity_mw: float
    actual_output_mw: float
    expected_output_mw: float
    solar_irradiance: float          # W/m²
    panel_temperature: float          # °C
    voltage: float                    # V
    current: float                    # A
    inverter_efficiency: float        # %
    efficiency: float                 # Actual/Expected * 100
    performance_deviation: float      # %
    status: AssetStatus
    last_updated: str


class WindAsset(BaseModel):
    asset_id: str
    name: str
    location: str
    lat: float
    lon: float
    capacity_mw: float
    actual_output_mw: float
    expected_output_mw: float
    wind_speed: float                 # m/s
    wind_direction: float             # degrees
    turbine_rpm: float
    generator_temperature: float      # °C
    vibration: float                  # mm/s
    turbine_efficiency: float         # %
    efficiency: float                 # Actual/Expected * 100
    performance_deviation: float      # %
    status: AssetStatus
    last_updated: str


class Substation(BaseModel):
    asset_id: str
    name: str
    location: str
    lat: float
    lon: float
    voltage_kv: float
    load_mva: float
    capacity_mva: float
    status: AssetStatus


class AssetHealth(BaseModel):
    asset_id: str
    asset_type: AssetType
    name: str
    location: str
    actual_output_mw: float
    expected_output_mw: float
    efficiency: float
    risk_score: float
    risk_level: RiskLevel
    status: AssetStatus
    lat: float
    lon: float


class WeatherData(BaseModel):
    location: str
    timestamp: str
    temperature: float          # °C
    wind_speed: float           # m/s
    wind_direction: float       # degrees
    solar_irradiance: float     # W/m²
    cloud_cover: float          # %
    humidity: float             # %
    condition: str              # Sunny / Partly Cloudy / Cloudy / etc.
    pressure: float             # hPa


class GridStatus(BaseModel):
    timestamp: str
    renewable_generation_mw: float
    total_demand_mw: float
    grid_export_mw: float
    grid_import_mw: float
    frequency_hz: float
    voltage_kv: float
    renewable_share_pct: float
    surplus_mw: float


class StorageStatus(BaseModel):
    storage_id: str
    name: str
    location: str
    capacity_mwh: float
    current_charge_mwh: float
    state_of_charge_pct: float
    charging_rate_mw: float
    discharging_rate_mw: float
    status: str


class MaintenanceRecord(BaseModel):
    record_id: str
    asset_id: str
    date: str
    type: str
    description: str
    technician: str
    outcome: str


class AgentFinding(BaseModel):
    agent_name: str
    asset_id: Optional[str] = None
    finding_type: str
    severity: str
    description: str
    data_source: str
    timestamp: str
    details: Dict[str, Any] = {}


class AgentRecommendation(BaseModel):
    rec_id: str
    timestamp: str
    agent_name: str
    asset_id: Optional[str] = None
    recommendation_type: str
    title: str
    description: str
    reasoning: List[str]
    confidence: float               # 0-100
    risk_level: RiskLevel
    human_decision: HumanDecision = HumanDecision.PENDING
    decision_timestamp: Optional[str] = None
    decision_note: Optional[str] = None
    safety_note: str = "⚠️ This is a recommendation only. No physical action has been taken. Operator approval required."


class DecisionLogEntry(BaseModel):
    log_id: str
    timestamp: str
    agent_name: str
    asset_id: Optional[str] = None
    finding: str
    recommendation: str
    confidence: float
    human_decision: HumanDecision
    decision_timestamp: Optional[str] = None
    rec_id: Optional[str] = None


class GenerationDataPoint(BaseModel):
    timestamp: str
    solar_mw: float
    wind_mw: float
    total_mw: float
    expected_mw: float
    demand_mw: float


class ForecastPoint(BaseModel):
    timestamp: str
    solar_forecast_mw: float
    wind_forecast_mw: float
    total_forecast_mw: float
    confidence: float


class MaintenanceRisk(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: AssetType
    location: str
    risk_score: float              # 0-100
    risk_level: RiskLevel
    performance_decline_pct: float
    possible_issue: str
    recommended_inspection: str
    priority: int                  # 1 = highest
    degradation_trend: str
    last_maintenance: Optional[str] = None
    fault_history: int = 0         # count of recent faults


class AgentActivity(BaseModel):
    timestamp: str
    agent_name: str
    activity: str
    details: Optional[str] = None
    severity: str = "info"         # info / warning / alert


class ParkSummary(BaseModel):
    timestamp: str
    overall_status: AssetStatus
    health_summary: str
    total_solar_mw: float
    total_wind_mw: float
    total_renewable_mw: float
    expected_total_mw: float
    park_efficiency: float
    co2_avoided_tons_per_hour: float
    healthy_assets: int
    warning_assets: int
    critical_assets: int
    high_risk_assets: int
    active_recommendations: int
    grid_status: Optional[GridStatus] = None
    weather_summary: Optional[str] = None
