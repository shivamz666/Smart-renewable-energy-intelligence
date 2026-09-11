# Smart Renewable Energy Intelligence Platform
## Agentic AI Decision Support for Solar-Wind Hybrid Parks — Kutch & Banaskantha, Gujarat

> **Challenge 14 — IBM Hackathon MVP**
> Domain: Energy & Sustainability

---

## 🎯 What This Platform Does

An **Agentic AI Decision-Support Platform** that monitors solar-wind hybrid renewable energy parks, detects performance anomalies, predicts maintenance needs, forecasts generation, and provides **explainable AI recommendations** to human operators.

**Key Principle:** The AI *recommends*. The human *decides*. No physical equipment is ever controlled automatically.

```
Renewable Assets → Sensor Data → 5 AI Agents → IBM Granite → AI Recommendation → Human Operator → Manual Execution
```

---

## ⚠️ Safety Notice

This is a **DECISION-SUPPORT SYSTEM ONLY**.

- ✅ AI can recommend actions
- ❌ AI cannot control wind turbines, solar inverters, batteries, substations, or any electrical equipment
- ✅ Human operator must approve all recommendations
- ✅ All data is clearly labeled: **DEMO / SIMULATED DATA**

---

## 🏗 Architecture

```
frontend/               React + Recharts dashboard
backend/
  main.py               FastAPI REST API
  config/settings.py    Environment-based configuration (no hardcoded keys)
  models/               Pydantic data models
  data/simulator.py     Realistic simulated sensor data
  agents/
    performance_agent.py   Asset performance monitoring & anomaly detection
    maintenance_agent.py   Predictive maintenance risk scoring
    forecasting_agent.py   Weather-based generation forecasting
    grid_agent.py          Grid analysis & recommendation
    dashboard_agent.py     Unified park summary
  orchestrator/          Agent coordination & decision log
  granite/               IBM Granite LLM client (with mock fallback)
```

---

## 🤖 AI Agents

| Agent | Function |
|-------|----------|
| Performance Monitoring | Detects underperformance, classifies HEALTHY/WARNING/CRITICAL |
| Predictive Maintenance | Risk scoring 0-100, identifies possible issues |
| Weather & Forecasting  | 6h/24h generation forecasts from simulated weather |
| Grid Analysis          | Surplus/deficit detection, storage/export recommendations |
| Dashboard Agent        | Unified park health summary and KPI aggregation |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Install Python dependencies

```bash
cd renewable-energy-platform
pip install -r requirements.txt
```

### 2. Start the backend

```bash
python run.py
```
Backend runs at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### 3. Install & start the frontend

```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: **http://localhost:3000**

---

## 🔑 IBM Granite Configuration (Optional)

The platform works without any API keys using the intelligent mock Granite implementation.

To connect real IBM WatsonX / Granite:

```bash
# Set environment variables (never hardcode!)
export GRANITE_API_KEY="your-ibm-cloud-api-key"
export GRANITE_PROJECT_ID="your-watsonx-project-id"
export GRANITE_API_URL="https://us-south.ml.cloud.ibm.com/ml/v1/text/generation"
export GRANITE_MODEL_ID="ibm/granite-13b-instruct-v2"
export USE_MOCK_GRANITE=false
```

---

## 📱 Platform Pages

| Page | Description |
|------|-------------|
| **Dashboard** | KPI cards, asset health table, park map, generation chart |
| **Maintenance** | Risk scores, degradation trends, inspection recommendations |
| **Grid & Energy** | Grid situation, storage status, operator decision buttons |
| **Agent Activity** | Real-time agent workflow feed + architecture diagram |
| **Decision Log** | Full audit trail of findings, recommendations, decisions |
| **AI Assistant** | IBM Granite chat for natural-language queries |
| **Demo Scenarios** | 3 pre-built scenarios to showcase AI capabilities |

---

## 🎬 Demo Scenarios

1. **Wind Turbine Failure Risk** — WT-07 underperforms despite good wind
2. **Renewable Energy Surplus** — High generation, grid storage recommendation
3. **Weather-Driven Drop** — Cloud cover causes solar generation decline

---

## 🛡 Human-in-the-Loop

Every AI recommendation shows:
- What the AI detected
- Why it made the recommendation  
- Confidence level
- Reasoning points
- **[Approve] [Reject] [Review Details]** buttons

The AI system stops at the recommendation stage. No automated execution.

---

## 📊 Simulated Data

| Asset | Count |
|-------|-------|
| Solar arrays | 20 (12 Kutch + 8 Banaskantha) |
| Wind turbines | 15 (9 Kutch + 6 Banaskantha) |
| Battery storage | 3 BESS units |
| Substations | 3 |
| Historical data | 7 days / 24h generation |

---

## 🏆 Technology Stack

- **Backend:** Python, FastAPI, Pydantic
- **Frontend:** React 18, Recharts, Vite
- **AI:** IBM Granite (WatsonX) with intelligent mock fallback
- **Deployment:** IBM Cloud compatible
- **Safety:** Human-in-the-loop architecture throughout

---

*IBM Hackathon 2024 — Challenge 14: Smart Renewable Energy Asset Monitoring*
