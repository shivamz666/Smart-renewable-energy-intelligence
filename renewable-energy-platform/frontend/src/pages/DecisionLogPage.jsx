import React, { useContext, useEffect, useState } from 'react'
import { ClipboardList, RefreshCw } from 'lucide-react'
import { AppContext } from '../App'
import { getDecisionLog } from '../api'

const fmt = v => v != null ? Number(v).toFixed(0) : '—'
const fmtTs = ts => { try { return new Date(ts).toLocaleString([], { dateStyle:'short', timeStyle:'medium' }) } catch { return ts || '—' } }

const DECISION_COLORS = {
  PENDING:  { bg: 'rgba(234,179,8,0.1)',  color: '#eab308', label: '⏳ Pending' },
  APPROVED: { bg: 'rgba(34,197,94,0.1)',  color: '#22c55e', label: '✅ Approved' },
  REJECTED: { bg: 'rgba(239,68,68,0.1)',  color: '#ef4444', label: '❌ Rejected' },
  IGNORED:  { bg: 'rgba(148,163,184,0.1)',color: '#94a3b8', label: '⊘ Ignored' },
}

export default function DecisionLogPage() {
  const { state } = useContext(AppContext)
  const [log, setLog] = useState([])
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState('all')

  const loadLog = async () => {
    setLoading(true)
    try {
      const res = await getDecisionLog()
      setLog(res.data.log || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadLog() }, [state])

  const filtered = filter === 'all' ? log : log.filter(e => e.human_decision === filter.toUpperCase())

  const counts = {
    all: log.length,
    pending: log.filter(e => e.human_decision === 'PENDING').length,
    approved: log.filter(e => e.human_decision === 'APPROVED').length,
    rejected: log.filter(e => e.human_decision === 'REJECTED').length,
  }

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
            <ClipboardList size={20} color="var(--accent)" />
            AI Decision Log
          </div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 4 }}>
            Complete audit trail of all AI findings, recommendations, and operator decisions.
            Transparency and auditability of AI-assisted operations.
          </div>
        </div>
        <button onClick={loadLog} disabled={loading} style={{
          background: 'var(--surface2)', border: '1px solid var(--border)', color: 'var(--muted)',
          borderRadius: 8, padding: '8px 14px', display: 'flex', alignItems: 'center', gap: 6, fontSize: 12
        }}>
          <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          Refresh
        </button>
      </div>

      {/* Summary stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 }}>
        {[
          { label: 'Total Entries', value: counts.all,     color: 'var(--accent)' },
          { label: 'Pending',       value: counts.pending, color: '#eab308' },
          { label: 'Approved',      value: counts.approved,color: '#22c55e' },
          { label: 'Rejected',      value: counts.rejected,color: '#ef4444' },
        ].map(s => (
          <div key={s.label} style={{
            background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 16
          }}>
            <div style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 12, color: 'var(--muted)' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 8 }}>
        {['all', 'pending', 'approved', 'rejected'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            padding: '5px 14px', borderRadius: 6, fontSize: 11, fontWeight: 600,
            background: filter === f ? 'rgba(56,189,248,0.15)' : 'var(--surface)',
            color: filter === f ? 'var(--accent)' : 'var(--muted)',
            border: `1px solid ${filter === f ? 'rgba(56,189,248,0.4)' : 'var(--border)'}`,
          }}>
            {f.charAt(0).toUpperCase() + f.slice(1)} ({counts[f] ?? 0})
          </button>
        ))}
      </div>

      {/* Table */}
      <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ background: 'var(--surface2)' }}>
              <tr>
                {['Time', 'Agent', 'Asset', 'Finding', 'Recommendation', 'Confidence', 'Operator Decision'].map(h => (
                  <th key={h} style={{
                    padding: '10px 14px', textAlign: 'left',
                    color: 'var(--muted)', fontSize: 11, fontWeight: 600, whiteSpace: 'nowrap'
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: 32, textAlign: 'center', color: 'var(--muted)' }}>
                    No log entries yet. Run a scenario to generate recommendations.
                  </td>
                </tr>
              ) : filtered.map((entry, i) => {
                const dec = DECISION_COLORS[entry.human_decision] || DECISION_COLORS.PENDING
                return (
                  <tr key={entry.log_id || i} style={{
                    borderTop: '1px solid var(--border)',
                    background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)'
                  }}>
                    <td style={{ padding: '10px 14px', fontSize: 11, color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                      {fmtTs(entry.timestamp)}
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: 12, fontWeight: 600, color: 'var(--accent)', whiteSpace: 'nowrap' }}>
                      {entry.agent_name?.replace(' Agent', '')}
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: 12, fontWeight: 600 }}>
                      {entry.asset_id || <span style={{ color: 'var(--muted)' }}>Grid</span>}
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: 12, color: 'var(--muted)', maxWidth: 240 }}>
                      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {entry.finding}
                      </div>
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: 12, fontWeight: 600, maxWidth: 200 }}>
                      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {entry.recommendation}
                      </div>
                    </td>
                    <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                      <ConfBadge value={entry.confidence} />
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <span style={{
                        background: dec.bg, color: dec.color,
                        border: `1px solid ${dec.color}40`,
                        borderRadius: 6, padding: '3px 10px',
                        fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap'
                      }}>
                        {dec.label}
                      </span>
                      {entry.decision_timestamp && (
                        <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 3 }}>
                          {fmtTs(entry.decision_timestamp)}
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit note */}
      <div style={{
        background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.2)',
        borderRadius: 10, padding: '12px 16px', fontSize: 12, color: '#a5b4fc'
      }}>
        🛡 <strong>Auditability:</strong> All AI agent findings, recommendations, and operator decisions are logged for full transparency.
        No AI recommendation is executed without explicit human approval.
        This log supports regulatory compliance and operational oversight.
      </div>
    </div>
  )
}

function ConfBadge({ value }) {
  const col = value >= 80 ? '#22c55e' : value >= 60 ? '#eab308' : '#ef4444'
  return (
    <span style={{
      background: `${col}15`, color: col, border: `1px solid ${col}30`,
      borderRadius: 4, padding: '2px 8px', fontSize: 11, fontWeight: 600
    }}>
      {fmt(value)}%
    </span>
  )
}
