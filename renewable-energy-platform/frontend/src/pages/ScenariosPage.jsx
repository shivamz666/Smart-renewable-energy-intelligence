import React, { useContext, useState } from 'react'
import { PlayCircle, RotateCcw, AlertTriangle, TrendingUp, Cloud, Wind, Sun, Zap, Check } from 'lucide-react'
import { AppContext } from '../App'

const SCENARIOS = [
  {
    id: 'underperformance',
    title: 'Wind Turbine Failure Risk',
    icon: <Wind size={24} color="#ef4444" />,
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.08)',
    border: 'rgba(239,68,68,0.3)',
    button: '▶ Run Underperformance Scenario',
    description: 'Simulate WT-07 producing significantly below expected output despite favorable wind conditions. Agents detect the anomaly, assess maintenance risk, and generate an operator alert.',
    steps: [
      { agent: 'Weather Agent', msg: 'Wind speed in Kutch remains favorable at 7.8 m/s — optimal conditions' },
      { agent: 'Performance Agent', msg: 'WT-07 output begins decreasing — 22% below expected' },
      { agent: 'Performance Agent', msg: 'Abnormal vibration (4.8 mm/s) and elevated temperature (88°C) detected' },
      { agent: 'Maintenance Agent', msg: 'WT-07 risk score increased to 82/100 — HIGH risk level' },
      { agent: 'Forecasting Agent', msg: 'Favorable wind confirmed for next 6 hours — issue is asset-specific' },
      { agent: 'Grid Agent', msg: 'Park generation recalculated with WT-07 degraded output' },
      { agent: 'IBM Granite AI', msg: 'AI recommendation generated for WT-07 — awaiting operator decision' },
    ],
    outcome: '"WT-07 requires operator attention due to abnormal performance despite favorable wind conditions."',
  },
  {
    id: 'high_generation',
    title: 'Renewable Energy Surplus',
    icon: <TrendingUp size={24} color="#22c55e" />,
    color: '#22c55e',
    bg: 'rgba(34,197,94,0.08)',
    border: 'rgba(34,197,94,0.3)',
    button: '▶ Run High Generation Scenario',
    description: 'Simulate exceptional solar and wind conditions with high generation exceeding grid demand. Agents detect surplus and recommend energy storage and export management.',
    steps: [
      { agent: 'Weather Agent', msg: 'Solar irradiance 945 W/m² and wind speed 11.2 m/s detected' },
      { agent: 'Performance Agent', msg: 'All solar arrays at 95%+ efficiency, wind farm 18% above baseline' },
      { agent: 'Forecasting Agent', msg: 'High generation forecast for next 6 hours — confidence 88%' },
      { agent: 'Grid Agent', msg: 'Renewable surplus ~25 MW above current demand detected' },
      { agent: 'Grid Agent', msg: 'Storage analysis: 68 MWh available across BESS units' },
      { agent: 'IBM Granite AI', msg: 'Surplus management recommendation generated' },
    ],
    outcome: '"Consider storing available excess energy and exporting the remaining suitable generation to the grid."',
  },
  {
    id: 'weather_drop',
    title: 'Weather-Driven Generation Drop',
    icon: <Cloud size={24} color="#94a3b8" />,
    color: '#94a3b8',
    bg: 'rgba(148,163,184,0.08)',
    border: 'rgba(148,163,184,0.3)',
    button: '▶ Run Weather Change Scenario',
    description: 'Simulate rapid cloud cover increase suppressing solar generation. Agents detect weather change, update forecasts, and recommend preparation for reduced generation.',
    steps: [
      { agent: 'Weather Agent', msg: 'Cloud cover rapidly increasing from 25% to 78%' },
      { agent: 'Weather Agent', msg: 'Solar irradiance dropping: 850 → 280 W/m²' },
      { agent: 'Performance Agent', msg: 'Solar generation declining — 40% below expected' },
      { agent: 'Forecasting Agent', msg: 'Updated forecast: suppressed solar for 2-3 hours, wind remains stable' },
      { agent: 'Grid Agent', msg: 'Grid impact analyzed — storage review recommended' },
      { agent: 'IBM Granite AI', msg: 'Weather-driven recommendation generated for operator' },
    ],
    outcome: '"Solar generation is expected to decline due to increased cloud cover. Consider reviewing wind generation and storage capacity."',
  },
]

export default function ScenariosPage() {
  const { scenario, scenarioRunning, runScenario, resetScenario } = useContext(AppContext)
  const [activeSteps, setActiveSteps] = useState({})
  const [completedScenario, setCompletedScenario] = useState(null)

  const handleRun = async (scId) => {
    setActiveSteps({})
    setCompletedScenario(null)

    // Animate steps
    const sc = SCENARIOS.find(s => s.id === scId)
    if (!sc) return

    // Run scenario on backend
    runScenario(scId)

    // Animate steps one by one
    for (let i = 0; i < sc.steps.length; i++) {
      await new Promise(r => setTimeout(r, 800))
      setActiveSteps(prev => ({ ...prev, [`${scId}-${i}`]: true }))
    }
    setCompletedScenario(scId)
  }

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Header */}
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: 12, padding: '16px 20px'
      }}>
        <div style={{ fontWeight: 700, fontSize: 16, display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <PlayCircle size={20} color="var(--accent)" />
          Demo Scenarios
        </div>
        <div style={{ fontSize: 13, color: 'var(--muted)' }}>
          Run pre-built scenarios to demonstrate the Agentic AI workflow.
          Each scenario showcases how multiple AI agents collaborate to detect issues and support operator decisions.
        </div>
        {scenario !== 'normal' && (
          <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ fontSize: 12, color: '#a855f7' }}>
              ▶ Active scenario: <strong>{scenario.replace('_', ' ').toUpperCase()}</strong>
            </div>
            <button onClick={resetScenario} disabled={scenarioRunning} style={{
              background: 'rgba(168,85,247,0.1)', border: '1px solid rgba(168,85,247,0.3)',
              color: '#a855f7', borderRadius: 6, padding: '4px 12px',
              fontSize: 11, display: 'flex', alignItems: 'center', gap: 6
            }}>
              <RotateCcw size={12} /> Reset to Normal
            </button>
          </div>
        )}
      </div>

      {/* Safety notice */}
      <div style={{
        background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.25)',
        borderRadius: 10, padding: '10px 16px', fontSize: 12, color: '#fbbf24',
        display: 'flex', alignItems: 'center', gap: 10
      }}>
        <AlertTriangle size={16} />
        <span>
          <strong>Demo Notice:</strong> These scenarios use SIMULATED data only.
          The Approve/Reject buttons in these scenarios simulate operator responses for demonstration purposes.
          No physical equipment is controlled.
        </span>
      </div>

      {/* Scenario Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 20 }}>
        {SCENARIOS.map(sc => {
          const isActive = scenario === sc.id
          const isComplete = completedScenario === sc.id
          const stepsVisible = Object.entries(activeSteps).filter(([k]) => k.startsWith(sc.id + '-')).length

          return (
            <div key={sc.id} style={{
              background: 'var(--surface)',
              border: `2px solid ${isActive ? sc.color : 'var(--border)'}`,
              borderRadius: 14, overflow: 'hidden', transition: 'border-color 0.3s'
            }}>
              {/* Card Header */}
              <div style={{ background: sc.bg, borderBottom: `1px solid ${sc.border}`, padding: '16px 20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                  <div style={{ background: `${sc.color}20`, borderRadius: 10, padding: 8 }}>{sc.icon}</div>
                  <div style={{ fontWeight: 700, fontSize: 15, color: sc.color }}>{sc.title}</div>
                  {isActive && (
                    <span style={{
                      marginLeft: 'auto', background: `${sc.color}20`, color: sc.color,
                      border: `1px solid ${sc.border}`, borderRadius: 12,
                      padding: '2px 10px', fontSize: 10, fontWeight: 700
                    }}>
                      ACTIVE
                    </span>
                  )}
                </div>
                <p style={{ fontSize: 12, color: 'var(--muted)', lineHeight: 1.6 }}>{sc.description}</p>
              </div>

              {/* Steps (shown during/after animation) */}
              {stepsVisible > 0 && (
                <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', marginBottom: 10 }}>
                    Agent Workflow
                  </div>
                  {sc.steps.map((step, i) => {
                    const visible = activeSteps[`${sc.id}-${i}`]
                    if (!visible) return null
                    return (
                      <div key={i} className="fade-in" style={{
                        display: 'flex', gap: 8, marginBottom: 8
                      }}>
                        <div style={{ width: 16, height: 16, borderRadius: '50%', background: `${sc.color}30`,
                          border: `1px solid ${sc.color}`, flexShrink: 0, marginTop: 2, fontSize: 8,
                          display: 'flex', alignItems: 'center', justifyContent: 'center', color: sc.color, fontWeight: 700
                        }}>
                          {i+1}
                        </div>
                        <div>
                          <div style={{ fontSize: 10, color: sc.color, fontWeight: 600 }}>{step.agent}</div>
                          <div style={{ fontSize: 12, color: 'var(--text)' }}>{step.msg}</div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              {/* Outcome */}
              {isComplete && (
                <div className="fade-in" style={{
                  margin: '0 20px 14px',
                  background: `${sc.color}10`, border: `1px solid ${sc.border}`,
                  borderRadius: 8, padding: '10px 14px', marginTop: 14
                }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: sc.color, marginBottom: 4 }}>🤖 Final AI Summary</div>
                  <p style={{ fontSize: 12, color: 'var(--text)', fontStyle: 'italic', lineHeight: 1.6 }}>{sc.outcome}</p>
                  <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 6 }}>
                    🛡 No physical action taken — awaiting operator decision
                  </div>
                </div>
              )}

              {/* Action button */}
              <div style={{ padding: '14px 20px' }}>
                <button
                  onClick={() => handleRun(sc.id)}
                  disabled={scenarioRunning}
                  style={{
                    width: '100%', background: `${sc.color}18`, border: `1px solid ${sc.border}`,
                    color: sc.color, borderRadius: 8, padding: '10px 16px',
                    fontSize: 13, fontWeight: 700, transition: 'all 0.2s',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                    opacity: scenarioRunning ? 0.6 : 1
                  }}
                >
                  {scenarioRunning && isActive
                    ? <><span className="spinner" style={{ width: 16, height: 16 }} /> Running...</>
                    : <><PlayCircle size={16} /> {sc.button}</>}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Key Message */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(56,189,248,0.08), rgba(168,85,247,0.08))',
        border: '1px solid rgba(56,189,248,0.2)', borderRadius: 14,
        padding: '20px 24px', textAlign: 'center'
      }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent)', marginBottom: 10 }}>
          🎯 Platform Key Message
        </div>
        <p style={{ fontSize: 14, color: 'var(--text)', lineHeight: 1.8, maxWidth: 700, margin: '0 auto', fontStyle: 'italic' }}>
          "Our Agentic AI system does not replace the renewable-energy operator. It continuously analyzes complex renewable-energy data,
          coordinates multiple specialized AI agents, identifies risks and opportunities, and provides explainable recommendations
          so human operators can make faster and better decisions."
        </p>
        <div style={{ marginTop: 14, display: 'flex', justifyContent: 'center', gap: 20, fontSize: 12, color: 'var(--muted)' }}>
          <span>🤖 5 AI Agents</span>
          <span>•</span>
          <span>🧠 IBM Granite LLM</span>
          <span>•</span>
          <span>👤 Human-in-the-Loop</span>
          <span>•</span>
          <span>🛡 Zero Autonomous Control</span>
        </div>
      </div>
    </div>
  )
}
