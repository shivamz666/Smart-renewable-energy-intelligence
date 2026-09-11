import React, { useContext, useEffect, useRef, useState } from 'react'
import { Cpu, Activity, AlertTriangle, Info, CheckCircle, RefreshCw } from 'lucide-react'
import { AppContext } from '../App'
import { getAgentActivity } from '../api'

const AGENT_COLORS = {
  'Performance Monitoring Agent': '#38bdf8',
  'Predictive Maintenance Agent': '#f97316',
  'Weather & Forecasting Agent':   '#22c55e',
  'Grid Analysis Agent':           '#a855f7',
  'Dashboard Agent':               '#eab308',
  'IBM Granite AI':                '#f472b6',
}

const SEVERITY_STYLES = {
  info:    { bg: 'rgba(56,189,248,0.06)',  border: 'rgba(56,189,248,0.2)',  dot: '#38bdf8' },
  warning: { bg: 'rgba(234,179,8,0.06)',   border: 'rgba(234,179,8,0.2)',   dot: '#eab308' },
  alert:   { bg: 'rgba(239,68,68,0.08)',   border: 'rgba(239,68,68,0.25)',  dot: '#ef4444' },
}

const fmtTs = ts => {
  try { return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) }
  catch { return ts }
}

export default function AgentsPage() {
  const { state } = useContext(AppContext)
  const [activities, setActivities] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  const loadActivities = async () => {
    setLoading(true)
    try {
      const res = await getAgentActivity()
      setActivities(res.data.activities || [])
    } catch (e) {
      // Use state activities as fallback
      setActivities(state?.agent_activities || [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (state?.agent_activities) {
      setActivities(state.agent_activities)
    }
  }, [state])

  const filtered = filter === 'all'
    ? activities
    : activities.filter(a => a.severity === filter || a.agent_name.toLowerCase().includes(filter))

  const agentNames = [...new Set(activities.map(a => a.agent_name))]

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Header */}
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: 12, padding: '16px 20px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
      }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Cpu size={20} color="var(--accent)" />
            Agent Activity Feed
          </div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 4 }}>
            Real-time view of AI agents working together. Demonstrating Agentic AI workflow collaboration.
          </div>
        </div>
        <button onClick={loadActivities} disabled={loading} style={{
          background: 'var(--surface2)', border: '1px solid var(--border)', color: 'var(--muted)',
          borderRadius: 8, padding: '8px 14px', display: 'flex', alignItems: 'center', gap: 6, fontSize: 12
        }}>
          <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          Refresh
        </button>
      </div>

      {/* Agent Legend */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        {Object.entries(AGENT_COLORS).map(([name, color]) => (
          <div key={name} style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: 8, padding: '6px 12px', display: 'flex', alignItems: 'center', gap: 7,
            fontSize: 11
          }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
            <span style={{ color: 'var(--muted)' }}>{name}</span>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div style={{ display: 'flex', gap: 8 }}>
        {['all', 'info', 'warning', 'alert'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            padding: '5px 14px', borderRadius: 6, fontSize: 11, fontWeight: 600,
            background: filter === f ? 'rgba(56,189,248,0.15)' : 'var(--surface)',
            color: filter === f ? 'var(--accent)' : 'var(--muted)',
            border: `1px solid ${filter === f ? 'rgba(56,189,248,0.4)' : 'var(--border)'}`,
          }}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
        <div style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--muted)', lineHeight: '28px' }}>
          {filtered.length} events
        </div>
      </div>

      {/* Timeline */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2, position: 'relative' }}>
        {/* Vertical line */}
        <div style={{
          position: 'absolute', left: 23, top: 0, bottom: 0,
          width: 1, background: 'var(--border)'
        }} />

        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40, color: 'var(--muted)' }}>
            Run a demo scenario to see agent activity here.
          </div>
        ) : (
          filtered.map((a, i) => {
            const col = AGENT_COLORS[a.agent_name] || '#64748b'
            const style = SEVERITY_STYLES[a.severity] || SEVERITY_STYLES.info
            return (
              <div key={i} className="fade-in" style={{
                display: 'flex', alignItems: 'flex-start', gap: 12, padding: '8px 0'
              }}>
                {/* Timeline dot */}
                <div style={{
                  width: 14, height: 14, borderRadius: '50%',
                  background: style.dot, flexShrink: 0, marginTop: 4,
                  zIndex: 1, border: '2px solid var(--bg)',
                  boxShadow: a.severity === 'alert' ? `0 0 8px ${style.dot}` : 'none'
                }} />

                {/* Content */}
                <div style={{
                  flex: 1, background: style.bg,
                  border: `1px solid ${style.border}`,
                  borderRadius: 10, padding: '10px 14px',
                  borderLeft: `3px solid ${col}`
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: col }}>{a.agent_name}</span>
                    <span style={{ fontSize: 10, color: 'var(--muted)' }}>{fmtTs(a.timestamp)}</span>
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.5 }}>{a.activity}</div>
                  {a.details && (
                    <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4, fontStyle: 'italic' }}>{a.details}</div>
                  )}
                </div>
              </div>
            )
          })
        )}
        <div ref={bottomRef} />
      </div>

      {/* Architecture diagram */}
      <AgentArchitecture />
    </div>
  )
}

function AgentArchitecture() {
  return (
    <div style={{
      background: 'var(--surface)', border: '1px solid var(--border)',
      borderRadius: 12, padding: 20
    }}>
      <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 16 }}>
        🏗 Agentic AI Architecture
      </div>
      <div style={{ display: 'flex', justifyContent: 'center', overflowX: 'auto' }}>
        <div style={{ fontSize: 12, fontFamily: 'monospace', color: 'var(--muted)', lineHeight: 2.2, minWidth: 500 }}>
          <FlowNode label="Solar & Wind Assets + Sensor Data" color="#f59e0b" />
          <Arrow />
          <FlowNode label="Agent Orchestrator" color="var(--accent)" big />
          <Arrow triple />
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, flexWrap: 'wrap', margin: '8px 0' }}>
            <FlowNode label="⚡ Performance Monitor" color="#38bdf8" small />
            <FlowNode label="🌤 Forecasting" color="#22c55e" small />
            <FlowNode label="🔧 Maintenance" color="#f97316" small />
          </div>
          <Arrow />
          <FlowNode label="Grid Analysis Agent" color="#a855f7" />
          <Arrow />
          <FlowNode label="IBM Granite AI" color="#f472b6" big />
          <Arrow />
          <FlowNode label="AI Recommendation" color="#eab308" />
          <Arrow />
          <FlowNode label="👤 Human Operator Decision" color="#22c55e" big />
          <Arrow />
          <FlowNode label="✅ Approve / ❌ Reject" color="#64748b" />
          <div style={{ textAlign: 'center', marginTop: 12, fontSize: 10, color: 'rgba(99,102,241,0.8)', padding: '6px 20px', background: 'rgba(99,102,241,0.08)', borderRadius: 6, display: 'inline-block' }}>
            🛡 No physical equipment is controlled by the AI
          </div>
        </div>
      </div>
    </div>
  )
}

function FlowNode({ label, color, big, small }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 2 }}>
      <div style={{
        background: `${color}18`, border: `1px solid ${color}50`, borderRadius: 8,
        padding: small ? '4px 12px' : big ? '8px 24px' : '6px 20px',
        color, fontWeight: big ? 700 : 600, fontSize: small ? 11 : big ? 13 : 12,
        textAlign: 'center'
      }}>
        {label}
      </div>
    </div>
  )
}

function Arrow({ triple }) {
  if (triple) return (
    <div style={{ display: 'flex', justifyContent: 'center', gap: 80, color: 'var(--border)', fontSize: 18, lineHeight: 1 }}>
      ↓ ↓ ↓
    </div>
  )
  return <div style={{ textAlign: 'center', color: 'var(--border)', fontSize: 18 }}>↓</div>
}
