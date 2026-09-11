"""Quick smoke test for the backend pipeline."""
from backend.orchestrator.orchestrator import orchestrator

result = orchestrator.run()
kpis = result["kpis"]
park = result["park_summary"]

print("=== SMOKE TEST ===")
print("Solar MW:    ", kpis["solar_generation_mw"])
print("Wind MW:     ", kpis["wind_generation_mw"])
print("Total MW:    ", kpis["total_renewable_mw"])
print("Efficiency:  ", kpis["park_efficiency_pct"], "%")
print("Park status: ", park["overall_status"])
print("Healthy:     ", park["healthy_assets"])
print("Warning:     ", park["warning_assets"])
print("Critical:    ", park["critical_assets"])
print("Findings:    ", len(result["all_findings"]))
print("Maint risks: ", len(result["maintenance_risks"]))
print("Active recs: ", len(result["active_recommendations"]))
print("6h forecast: ", len(result["forecast_6h"]), "points")
print("Activities:  ", len(result["agent_activities"]))
print()

# Check WT-07 specifically
wt07 = next((a for a in result["wind_assets"] if a["asset_id"] == "WT-07"), None)
if wt07:
    print("WT-07 efficiency:   ", wt07["efficiency"], "%")
    print("WT-07 vibration:    ", wt07["vibration"], "mm/s")
    print("WT-07 gen temp:     ", wt07["generator_temperature"], "C")
    print("WT-07 status:       ", wt07["status"])

# Check maintenance risks
print()
print("Top 3 maintenance risks:")
for r in result["maintenance_risks"][:3]:
    print(f"  {r['asset_id']}: {r['risk_score']}/100 {r['risk_level']}")

# Test scenario
print()
print("Running underperformance scenario...")
result2 = orchestrator.run_scenario("underperformance")
wt07s = next((a for a in result2["wind_assets"] if a["asset_id"] == "WT-07"), None)
if wt07s:
    print("WT-07 scenario efficiency:", wt07s["efficiency"], "%")
print("Scenario activities:", len(result2.get("scenario_steps", [])))

# Test Granite mock
from backend.granite.granite_client import granite_client
granite_client.set_context(result)
resp = granite_client.chat("What is the current park health summary?", result)
print()
print("Granite response source:", resp["source"])
print("Granite response length:", len(resp["response"]), "chars")

print()
print("=== ALL SYSTEMS OK ===")
