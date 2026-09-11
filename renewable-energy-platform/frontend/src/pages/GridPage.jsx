import React, { useContext, useState } from 'react'
import { Shield, Check, X, Eye, AlertTriangle, Zap, Battery, TrendingUp } from 'lucide-react'
import { AppContext } from '../App'
import { submitDecision } from '../api'
import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, ReferenceLine
} from 'recharts'

const fmt = (v, d=1) => v != null ? Number(v).toFixed(d) : '—'
const fmtTs = ts => { try { return new Date(ts).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}) } catch { return ts } }

export default function GridPage() {
  const { state, refresh } = useContext(AppContext)
  const [deciding, setDeciding] = useState(null)
  const [decisionNote, setDecisionNote] = useState('')
  const [decisionResult, setDecisionResult] = useState(null)

  if (!state) return null
  const { grid_status: grid, storage, active_recommendations: recs, forecast_6h } = state
  const kpis = state.kpis || {}
  const gridRecs = recs?.filter(r =>
    r.recommendation_type === 'store_excess_energy' ||
    r.recommendation_type === 'discharge_storage' ||
    r.recommendation_type === 'prepare_for_generation_drop'
  ) || []

  const handleDecision = async (rec_id, decision) => {
    setDeciding(rec_id)
    try {
      const res = await submitDecision(rec_id, decision, decisionNote)
      setDecisionResult({ rec_id, decision, ...res.data })
      await refresh()
    } catch (e) {
      console.error(e)
    } finally {
      setDeciding(null)
      setDecisionNote('')
    }
  }

  // Build chart data combining current + forecast
  const chartData = forecast_6h?.slice(0, 8).map(f => ({
    name: fmtTs(f.timestamp),
    generation: f.total_forecast_mw,
    solar: f.solar_forecast_mw,
    wind: f.wind_forecast_mw,
    demand: grid?.total_demand_mw || 0,
    surplus: f.total_forecast_mw - (grid?.total_demand_mw || 0),
  })) || []

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Safety Banner */}
      <div style={{
        background: 'rgba(99,102,241,0.08)', border: '2px solid rgba(99,102,241,0.3)',
        borderRadius: 12, padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 14
      }}>
        <Shield size={22} color="#818cf8" />
        <div>
          <div style={{ fontWeight: 700, fontSize: 14, color: '#818cf8' }}>
            🛡 HUMAN-IN-THE-LOOP: AI recommendations require operator approval
          </div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
            This page provides grid decision support only.
            <strong style={{ color: 'var(--text)' }}> No grid commands, battery operations, or switching actions are issued by this system.</strong>
            {' '}All physical actions require authorized manual execution.
          </div>
        </div>
      </div>

      {/* Current Situation */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <GridSituationCard grid={grid} kpis={kpis} storage={storage} />
        <StorageCard storage={storage} />
      </div>

      {/* Generation vs Demand Chart */}
      <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 20 }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>Generation vs Demand Forecast</div>
        <div style={{ fontSize: 11, color: '#f59e0b', marginBottom: 14 }}>DATA SOURCE: SIMULATED FORECAST DATA</div>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="genGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="name" tick={{ fill: 'var(--muted)', fontSize: 11 }} />
            <YAxis tick={{ fill: 'var(--muted)', fontSize: 11 }} unit=" MW" />
            <Tooltip contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area type="monotone" dataKey="generation" name="Renewable Gen (MW)" stroke="#38bdf8" fill="url(#genGrad)" strokeWidth={2} />
            <Line type="monotone" dataKey="demand" name="Grid Demand (MW)" stroke="#f97316" strokeWidth={2} strokeDasharray="6 3" dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* AI Recommendations */}
      <div>
        <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 12 }}>
          🤖 AI Grid Recommendations
        </h3>
        {gridRecs.length === 0 ? (
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: 12, padding: 24, textAlign: 'center', color: 'var(--muted)'
          }}>
            ✅ No active grid recommendations. Park conditions are balanced.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {gridRecs.map(rec => (
              <RecommendationCard
                key={rec.rec_id}
                rec={rec}
                deciding={deciding === rec.rec_id}
                decisionNote={decisionNote}
                onNoteChange={setDecisionNote}
                onDecide={handleDecision}
              />
            ))}
          </div>
        )}
      </div>

      {decisionResult && (
        <div style={{
          background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.3)',
          borderRadius: 12, padding: '12px 20px', fontSize: 12, color: '#86efac'
        }}>
          ✅ {decisionResult.safety_note}
        </div>
      )}
    </div>
  )
}

function GridSituationCard({ grid, kpis }) {
  if (!grid) return null
  const surplus = grid.surplus_mw || 0
  const isSurplus = surplus > 0

  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 20 }}>
      <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>Current Grid Situation</div>
      <div style={{ fontSize: 10, color: '#f59e0b', marginBottom: 14 }}>DATA SOURCE: SIMULATED DATA</div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <GridRow label="Renewable Generation" value={`${fmt(grid.renewable_generation_mw)} MW`} color="#22c55e" />
        <GridRow label="Grid Demand" value={`${fmt(grid.total_demand_mw)} MW`} color="#64748b" />
        <GridRow label={isSurplus ? 'Surplus' : 'Deficit'} value={`${fmt(Math.abs(surplus))} MW`} color={isSurplus ? '#22c55e' : '#ef4444'} bold />
        <GridRow label="Renewable Share" value={`${fmt(grid.renewable_share_pct)}%`} color="#38bdf8" />
        <GridRow label="Grid Export" value={`${fmt(grid.grid_export_mw)} MW`} color="#a855f7" />
        <GridRow label="Frequency" value={`${grid.frequency_hz?.toFixed(3)} Hz`} color={Math.abs(grid.frequency_hz - 50) < 0.1 ? '#22c55e' : '#ef4444'} />
      </div>

      <div style={{
        marginTop: 14, padding: '10px 14px',
        background: isSurplus ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
        border: `1px solid ${isSurplus ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)'}`,
        borderRadius: 8, fontSize: 12,
        color: isSurplus ? '#86efac' : '#fca5a5'
      }}>
        {isSurplus
          ? `⬆️ Renewable surplus of ${fmt(surplus)} MW — consider storage or export`
          : `⬇️ Generation deficit of ${fmt(Math.abs(surplus))} MW — storage discharge may help`}
      </div>
    </div>
  )
}

function StorageCard({ storage }) {
  if (!storage?.length) return null
  const totalCap = storage.reduce((s, b) => s + b.capacity_mwh, 0)
  const totalCharge = storage.reduce((s, b) => s + b.current_charge_mwh, 0)
  const avgSoc = totalCap > 0 ? (totalCharge / totalCap) * 100 : 0

  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 20 }}>
      <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
        <Battery size={16} style={{ marginRight: 6, verticalAlign: 'middle', color: '#22c55e' }} />
        Battery Storage Status
      </div>
      <div style={{ fontSize: 10, color: '#f59e0b', marginBottom: 14 }}>DATA SOURCE: SIMULATED DATA</div>

      {/* Aggregate SoC */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontSize: 12, color: 'var(--muted)' }}>Total SoC</span>
          <span style={{ fontWeight: 700, color: '#22c55e' }}>{fmt(avgSoc)}%</span>
        </div>
        <div style={{ background: 'var(--border)', borderRadius: 4, height: 8, overflow: 'hidden' }}>
          <div style={{ width: `${avgSoc}%`, background: avgSoc > 70 ? '#22c55e' : avgSoc > 30 ? '#eab308' : '#ef4444', height: '100%', borderRadius: 4, transition: 'width 0.5s' }} />
        </div>
        <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
          {fmt(totalCharge, 1)} / {fmt(totalCap, 1)} MWh
        </div>
      </div>

      {/* Individual batteries */}
      {storage.map(b => (
        <div key={b.storage_id} style={{ marginBottom: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <span style={{ fontSize: 12, fontWeight: 600 }}>{b.name}</span>
            <span style={{ fontSize: 12, color: '#22c55e' }}>{fmt(b.state_of_charge_pct)}%</span>
          </div>
          <div style={{ background: 'var(--border)', borderRadius: 3, height: 5, overflow: 'hidden' }}>
            <div style={{
              width: `${b.state_of_charge_pct}%`,
              background: b.state_of_charge_pct > 70 ? '#22c55e' : b.state_of_charge_pct > 30 ? '#eab308' : '#ef4444',
              height: '100%', borderRadius: 3
            }} />
          </div>
          <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 2 }}>
            {fmt(b.current_charge_mwh, 1)} / {b.capacity_mwh} MWh
            {b.charging_rate_mw > 0 && <span style={{ color: '#22c55e', marginLeft: 8 }}>↑ {fmt(b.charging_rate_mw)} MW charging</span>}
            {b.discharging_rate_mw > 0 && <span style={{ color: '#f97316', marginLeft: 8 }}>↓ {fmt(b.discharging_rate_mw)} MW discharging</span>}
          </div>
        </div>
      ))}
    </div>
  )
}

function RecommendationCard({ rec, deciding, decisionNote, onNoteChange, onDecide }) {
  const [showDetails, setShowDetails] = useState(false)
  const isPending = rec.human_decision === 'PENDING'
  const isApproved = rec.human_decision === 'APPROVED'
  const isRejected = rec.human_decision === 'REJECTED'

  const recTypeLabel = {
    store_excess_energy: '💾 Store Excess Energy',
    discharge_storage: '⚡ Discharge Storage',
    prepare_for_generation_drop: '☁️ Prepare for Generation Drop',
    maintenance: '🔧 Maintenance',
  }[rec.recommendation_type] || rec.recommendation_type

  return (
    <div style={{
      background: 'var(--surface)', border: `2px solid ${isPending ? 'rgba(234,179,8,0.4)' : isApproved ? 'rgba(34,197,94,0.4)' : 'rgba(239,68,68,0.4)'}`,
      borderRadius: 12, overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
          <div>
            <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>{rec.agent_name}</div>
            <div style={{ fontWeight: 700, fontSize: 15 }}>{rec.title}</div>
            <div style={{ fontSize: 11, color: 'var(--accent)', marginTop: 2 }}>{recTypeLabel}</div>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <ConfidenceBadge value={rec.confidence} />
            <StatusBadge status={rec.human_decision} />
          </div>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.6 }}>{rec.description}</p>
      </div>

      {/* Reasoning */}
      {showDetails && (
        <div style={{ padding: '14px 20px', background: 'var(--surface2)', borderBottom: '1px solid var(--border)' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', marginBottom: 8 }}>
            Why this recommendation?
          </div>
          <ul style={{ paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
            {rec.reasoning?.map((r, i) => (
              <li key={i} style={{ fontSize: 12, color: 'var(--text)' }}>{r}</li>
            ))}
          </ul>
          <div style={{
            marginTop: 12, padding: '8px 12px',
            background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)',
            borderRadius: 6, fontSize: 11, color: '#fbbf24'
          }}>
            {rec.safety_note}
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        {isPending ? (
          <>
            <div style={{ fontSize: 12, color: '#eab308', fontWeight: 600, marginRight: 8 }}>
              ⏳ Awaiting Operator Decision
            </div>
            <button
              onClick={() => onDecide(rec.rec_id, 'APPROVED')}
              disabled={deciding}
              style={{
                background: 'rgba(34,197,94,0.15)', border: '1px solid rgba(34,197,94,0.4)',
                color: '#22c55e', borderRadius: 8, padding: '8px 16px',
                fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6
              }}
            >
              {deciding ? <span className="spinner" style={{width:14,height:14}} /> : <Check size={14} />}
              Approve Recommendation
            </button>
            <button
              onClick={() => onDecide(rec.rec_id, 'REJECTED')}
              disabled={deciding}
              style={{
                background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.35)',
                color: '#ef4444', borderRadius: 8, padding: '8px 16px',
                fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6
              }}
            >
              <X size={14} /> Reject
            </button>
            <button
              onClick={() => setShowDetails(v => !v)}
              style={{
                background: 'var(--surface2)', border: '1px solid var(--border)',
                color: 'var(--muted)', borderRadius: 8, padding: '8px 14px',
                fontSize: 12, display: 'flex', alignItems: 'center', gap: 6
              }}
            >
              <Eye size={14} /> {showDetails ? 'Hide' : 'Review Details'}
            </button>
          </>
        ) : (
          <div style={{ fontSize: 12, color: isApproved ? '#22c55e' : '#ef4444' }}>
            {isApproved ? '✅ Recommendation Approved — Manual execution required by authorized personnel'
                        : '❌ Recommendation Rejected'}
            <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>
              🛡 No physical action has been taken by this system
            </div>
          </div>
        )}

        <div style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--muted)' }}>
          {new Date(rec.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

function GridRow({ label, value, color, bold }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontSize: 12, color: 'var(--muted)' }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: bold ? 700 : 600, color: color || 'var(--text)' }}>{value}</span>
    </div>
  )
}

function ConfidenceBadge({ value }) {
  const col = value >= 80 ? '#22c55e' : value >= 60 ? '#eab308' : '#ef4444'
  return (
    <span style={{
      background: `${col}15`, color: col, border: `1px solid ${col}40`,
      borderRadius: 6, padding: '3px 8px', fontSize: 11, fontWeight: 600
    }}>
      {fmt(value, 0)}% conf
    </span>
  )
}

function StatusBadge({ status }) {
  const cfg = {
    PENDING: { label: 'Pending', cls: 'badge-pending' },
    APPROVED: { label: 'Approved', cls: 'badge-approved' },
    REJECTED: { label: 'Rejected', cls: 'badge-rejected' },
    IGNORED: { label: 'Ignored', cls: 'badge-ignored' },
  }[status] || { label: status, cls: 'badge-pending' }

  return (
    <span className={cfg.cls} style={{ borderRadius: 6, padding: '3px 10px', fontSize: 11, fontWeight: 700 }}>
      {cfg.label}
    </span>
  )
}

function fmt(v, d=1) {
  return v != null ? Number(v).toFixed(d) : '—'
}
