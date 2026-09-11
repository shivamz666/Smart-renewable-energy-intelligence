import React, { useContext, useState } from 'react'
import { Wrench, AlertTriangle, Clock, ChevronRight, Wind, Sun, TrendingDown } from 'lucide-react'
import { AppContext } from '../App'

const fmt = (v, d=1) => v != null ? Number(v).toFixed(d) : '—'
const RISK_COLOR = { LOW: '#22c55e', MEDIUM: '#eab308', HIGH: '#ef4444', CRITICAL: '#ef4444' }
const RISK_BG    = { LOW: 'rgba(34,197,94,0.1)', MEDIUM: 'rgba(234,179,8,0.1)', HIGH: 'rgba(239,68,68,0.1)', CRITICAL: 'rgba(239,68,68,0.15)' }

export default function MaintenancePage() {
  const { state } = useContext(AppContext)
  const [selected, setSelected] = useState(null)

  if (!state) return null
  const risks = state.maintenance_risks || []
  const highRisk = risks.filter(r => r.risk_level === 'HIGH' || r.risk_level === 'CRITICAL')
  const medRisk   = risks.filter(r => r.risk_level === 'MEDIUM')

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Safety Notice */}
      <SafetyNotice />

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 }}>
        {[
          { label: 'Critical Risk Assets', value: risks.filter(r=>r.risk_level==='CRITICAL').length, color: '#ef4444' },
          { label: 'High Risk Assets',     value: highRisk.length,  color: '#f97316' },
          { label: 'Medium Risk Assets',   value: medRisk.length,   color: '#eab308' },
          { label: 'Total Monitored',      value: (state.solar_assets?.length||0) + (state.wind_assets?.length||0), color: 'var(--accent)' },
        ].map(s => (
          <div key={s.label} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 16 }}>
            <div style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 12, color: 'var(--muted)' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Risk List */}
      {highRisk.length > 0 && (
        <div>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: '#ef4444', marginBottom: 12 }}>
            🔴 HIGH / CRITICAL RISK — Operator Attention Required
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {highRisk.map(r => (
              <RiskCard key={r.asset_id} risk={r} selected={selected === r.asset_id}
                onClick={() => setSelected(selected === r.asset_id ? null : r.asset_id)} />
            ))}
          </div>
        </div>
      )}

      {medRisk.length > 0 && (
        <div>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: '#eab308', marginBottom: 12 }}>
            ⚠️ MEDIUM RISK — Monitor Closely
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {medRisk.map(r => (
              <RiskCard key={r.asset_id} risk={r} selected={selected === r.asset_id}
                onClick={() => setSelected(selected === r.asset_id ? null : r.asset_id)} compact />
            ))}
          </div>
        </div>
      )}

      {risks.length === 0 && (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--muted)' }}>
          ✅ No maintenance risks currently identified.
        </div>
      )}
    </div>
  )
}

function SafetyNotice() {
  return (
    <div style={{
      background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.25)',
      borderRadius: 12, padding: '12px 20px', display: 'flex', alignItems: 'center', gap: 12
    }}>
      <Wrench size={18} color="#818cf8" />
      <div>
        <div style={{ fontWeight: 700, fontSize: 13, color: '#818cf8' }}>
          🛡 DECISION SUPPORT — Maintenance Recommendations
        </div>
        <div style={{ fontSize: 12, color: 'var(--muted)' }}>
          The Predictive Maintenance Agent identifies risk patterns and suggests inspections.
          <strong style={{ color: 'var(--text)' }}> No maintenance orders are created or executed automatically.</strong>
          {' '}Operator must review and approve all actions.
        </div>
      </div>
    </div>
  )
}

function RiskCard({ risk, selected, onClick, compact = false }) {
  const col = RISK_COLOR[risk.risk_level] || '#eab308'
  const bg  = RISK_BG[risk.risk_level] || 'transparent'
  const isWind = risk.asset_type === 'wind'

  // Risk meter bar
  const meter = (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
      <span style={{ fontSize: 11, color: 'var(--muted)', width: 72, flexShrink: 0 }}>Risk Score</span>
      <div style={{ flex: 1, background: 'var(--border)', borderRadius: 4, height: 6, overflow: 'hidden' }}>
        <div style={{ width: `${risk.risk_score}%`, background: col, height: '100%', borderRadius: 4, transition: 'width 0.5s' }} />
      </div>
      <span style={{ color: col, fontWeight: 700, fontSize: 13, width: 50, textAlign: 'right' }}>
        {fmt(risk.risk_score, 0)}/100
      </span>
    </div>
  )

  return (
    <div style={{
      background: 'var(--surface)', border: `1px solid ${selected ? col : 'var(--border)'}`,
      borderLeft: `4px solid ${col}`, borderRadius: 12, overflow: 'hidden',
      transition: 'border-color 0.2s', cursor: 'pointer'
    }} onClick={onClick}>
      <div style={{ padding: '14px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ background: bg, borderRadius: 8, padding: 8 }}>
              {isWind ? <Wind size={18} color={col} /> : <Sun size={18} color={col} />}
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15 }}>{risk.asset_id}</div>
              <div style={{ fontSize: 12, color: 'var(--muted)' }}>{risk.asset_name}</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span style={{
              background: bg, color: col, border: `1px solid ${col}`,
              borderRadius: 6, padding: '3px 10px', fontSize: 11, fontWeight: 700
            }}>
              {risk.risk_level}
            </span>
            <ChevronRight size={16} color="var(--muted)"
              style={{ transform: selected ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }} />
          </div>
        </div>

        {meter}

        <div style={{ display: 'flex', gap: 20, fontSize: 12, color: 'var(--muted)', marginTop: 8 }}>
          <span>
            <TrendingDown size={11} style={{ marginRight: 3, verticalAlign: 'middle', color: '#ef4444' }} />
            Performance decline: <strong style={{ color: '#ef4444' }}>{fmt(risk.performance_decline_pct)}%</strong>
          </span>
          <span>
            <Clock size={11} style={{ marginRight: 3, verticalAlign: 'middle' }} />
            Last maintenance: <strong>{risk.last_maintenance || 'Unknown'}</strong>
          </span>
          <span>
            ⚠️ Faults (30d): <strong style={{ color: risk.fault_history > 0 ? '#f97316' : 'var(--text)' }}>{risk.fault_history}</strong>
          </span>
        </div>
      </div>

      {/* Expanded detail */}
      {selected && (
        <div style={{
          borderTop: `1px solid ${col}40`,
          background: `${col}08`, padding: '16px 20px',
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16
        }}>
          <div>
            <Label>Possible Issue (AI Analysis)</Label>
            <p style={{ fontSize: 12, color: 'var(--text)', marginTop: 4, lineHeight: 1.6 }}>
              {risk.possible_issue}
            </p>
          </div>
          <div>
            <Label>Recommended Inspection</Label>
            <p style={{ fontSize: 12, color: 'var(--text)', marginTop: 4, lineHeight: 1.6 }}>
              {risk.recommended_inspection}
            </p>
          </div>
          <div>
            <Label>Degradation Trend</Label>
            <p style={{ fontSize: 12, color: '#f97316', marginTop: 4 }}>{risk.degradation_trend}</p>
          </div>
          <div>
            <Label>Location</Label>
            <p style={{ fontSize: 12, color: 'var(--text)', marginTop: 4, textTransform: 'capitalize' }}>{risk.location}</p>
          </div>

          {/* Action buttons — display only, no equipment control */}
          <div style={{ gridColumn: '1 / -1' }}>
            <div style={{
              background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)',
              borderRadius: 8, padding: '10px 14px', marginTop: 8, fontSize: 11, color: '#fbbf24'
            }}>
              <strong>⚠️ AI Analysis Notice:</strong> The above represents AI-calculated risk patterns based on simulated sensor data.
              This is NOT a confirmed physical fault. Physical inspection by qualified personnel is required to validate these findings.
              No maintenance order has been created or executed.
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 12 }}>
              <button style={{
                background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)',
                color: '#ef4444', borderRadius: 8, padding: '8px 16px', fontSize: 12, fontWeight: 700
              }}>
                📋 View Full Analysis
              </button>
              <button style={{
                background: 'var(--surface2)', border: '1px solid var(--border)',
                color: 'var(--muted)', borderRadius: 8, padding: '8px 16px', fontSize: 12
              }}>
                📊 Performance History
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function Label({ children }) {
  return <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{children}</div>
}
