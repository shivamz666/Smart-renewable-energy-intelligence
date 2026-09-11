import React, { useContext, useState } from 'react'
import {
  Sun, Wind, Zap, Activity, TrendingUp, TrendingDown, Battery,
  ThermometerSun, Eye, AlertTriangle, CheckCircle, MapPin, BarChart2
} from 'lucide-react'
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { AppContext } from '../App'

const fmt = (v, d=1) => v != null ? Number(v).toFixed(d) : '—'
const fmtTs = (ts) => { try { return new Date(ts).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) } catch { return ts } }

export default function DashboardPage() {
  const { state, loading } = useContext(AppContext)
  const [histHours, setHistHours] = useState(24)

  if (!state) return null
  const { kpis, park_summary: park, solar_assets, wind_assets, substations,
          asset_health, kutch_weather: kw, banas_weather: bw,
          grid_status: grid, all_findings, forecast_6h } = state

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Park Health Banner */}
      <ParkHealthBanner park={park} />

      {/* KPI Cards */}
      <KPICards kpis={kpis} grid={grid} />

      {/* Generation Chart + Weather */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 16 }}>
        <GenerationChart forecast={forecast_6h} state={state} />
        <WeatherPanel kw={kw} bw={bw} />
      </div>

      {/* Asset Health Table */}
      <AssetHealthTable assets={asset_health} />

      {/* Park Map */}
      <ParkMap assets={asset_health} substations={substations} />
    </div>
  )
}

// ─── Park Health Banner ───────────────────────────────────────────────────────

function ParkHealthBanner({ park }) {
  if (!park) return null
  const isHealthy = park.overall_status === 'HEALTHY'
  return (
    <div style={{
      background: isHealthy ? 'rgba(34,197,94,0.08)' : 'rgba(234,179,8,0.08)',
      border: `1px solid ${isHealthy ? 'rgba(34,197,94,0.25)' : 'rgba(234,179,8,0.25)'}`,
      borderRadius: 12, padding: '14px 20px',
      display: 'flex', alignItems: 'flex-start', gap: 16
    }}>
      <div style={{
        background: isHealthy ? 'rgba(34,197,94,0.2)' : 'rgba(234,179,8,0.2)',
        borderRadius: 8, padding: 8, flexShrink: 0
      }}>
        {isHealthy
          ? <CheckCircle size={20} color="#22c55e" />
          : <AlertTriangle size={20} color="#eab308" />}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4, color: isHealthy ? '#22c55e' : '#eab308' }}>
          🤖 Dashboard Agent — Park Summary
        </div>
        <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.6 }}>{park.health_summary}</div>
        <div style={{ display: 'flex', gap: 20, marginTop: 8, fontSize: 11, color: 'var(--muted)' }}>
          <span>✅ Healthy: <strong style={{color:'#22c55e'}}>{park.healthy_assets}</strong></span>
          <span>⚠️ Warning: <strong style={{color:'#eab308'}}>{park.warning_assets}</strong></span>
          <span>🔴 Critical: <strong style={{color:'#ef4444'}}>{park.critical_assets}</strong></span>
          <span>🔧 High Risk: <strong style={{color:'#f97316'}}>{park.high_risk_assets}</strong></span>
          <span style={{marginLeft:'auto'}}>CO₂ Avoided: <strong style={{color:'#22c55e'}}>{fmt(park.co2_avoided_tons_per_hour)} t/hr</strong></span>
        </div>
      </div>
      <div style={{ fontSize: 10, color: 'var(--muted)', flexShrink: 0 }}>
        DATA SOURCE:<br/>SIMULATED
      </div>
    </div>
  )
}

// ─── KPI Cards ────────────────────────────────────────────────────────────────

function KPICards({ kpis, grid }) {
  if (!kpis) return null
  const cards = [
    { label: 'Solar Generation', value: `${fmt(kpis.solar_generation_mw)} MW`,    icon: <Sun size={20}/>,          color: '#f59e0b', sub: 'Photovoltaic output' },
    { label: 'Wind Generation',  value: `${fmt(kpis.wind_generation_mw)} MW`,     icon: <Wind size={20}/>,         color: '#38bdf8', sub: 'Turbine output' },
    { label: 'Total Renewable',  value: `${fmt(kpis.total_renewable_mw)} MW`,     icon: <Zap size={20}/>,          color: '#a855f7', sub: `Expected: ${fmt(kpis.expected_generation_mw)} MW` },
    { label: 'Park Efficiency',  value: `${fmt(kpis.park_efficiency_pct)}%`,      icon: <Activity size={20}/>,     color: effColor(kpis.park_efficiency_pct), sub: 'Actual / Expected' },
    { label: 'Grid Demand',      value: `${fmt(kpis.grid_demand_mw)} MW`,         icon: <BarChart2 size={20}/>,    color: '#64748b', sub: `Export: ${fmt(kpis.grid_export_mw)} MW` },
    { label: 'Storage Available',value: `${fmt(kpis.storage_available_mwh)} MWh`, icon: <Battery size={20}/>,     color: '#22c55e', sub: `SoC: ${fmt(kpis.storage_soc_pct)}%` },
    { label: 'CO₂ Avoided',     value: `${fmt(kpis.co2_avoided_tons_hr)} t/hr`,  icon: <ThermometerSun size={20}/>,color:'#22c55e', sub: 'vs grid average' },
    { label: 'Renewable Share',  value: `${fmt(kpis.renewable_share_pct)}%`,      icon: <TrendingUp size={20}/>,   color: '#22c55e', sub: 'of grid demand' },
  ]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
      {cards.map(c => (
        <div key={c.label} style={{
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 12, padding: '16px', position: 'relative', overflow: 'hidden'
        }}>
          <div style={{ position: 'absolute', top: 12, right: 12, color: c.color, opacity: 0.3 }}>
            {c.icon}
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 6 }}>{c.label}</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: c.color, marginBottom: 4 }}>{c.value}</div>
          <div style={{ fontSize: 11, color: 'var(--muted)' }}>{c.sub}</div>
        </div>
      ))}
    </div>
  )
}

function effColor(v) {
  if (v >= 90) return '#22c55e'
  if (v >= 75) return '#eab308'
  return '#ef4444'
}

// ─── Generation Chart ─────────────────────────────────────────────────────────

function GenerationChart({ forecast, state }) {
  const [view, setView] = useState('forecast')
  const historical = state?.historical || []

  // Combine recent historical with forecast
  const historical24 = (state?.generation_summary || [])
  const chartData = forecast?.slice(0, 8).map(f => ({
    name: fmtTs(f.timestamp),
    solar: f.solar_forecast_mw,
    wind: f.wind_forecast_mw,
    total: f.total_forecast_mw,
    confidence: f.confidence,
  })) || []

  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Generation Forecast</div>
          <div style={{ fontSize: 11, color: 'var(--muted)' }}>DATA SOURCE: SIMULATED FORECAST DATA</div>
        </div>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="solar" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="wind" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="total" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="name" tick={{ fill: 'var(--muted)', fontSize: 11 }} />
            <YAxis tick={{ fill: 'var(--muted)', fontSize: 11 }} unit=" MW" />
            <Tooltip
              contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: 'var(--text)' }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area type="monotone" dataKey="solar" name="Solar (MW)" stroke="#f59e0b" fill="url(#solar)" strokeWidth={2} />
            <Area type="monotone" dataKey="wind"  name="Wind (MW)"  stroke="#38bdf8" fill="url(#wind)"  strokeWidth={2} />
            <Area type="monotone" dataKey="total" name="Total (MW)" stroke="#a855f7" fill="url(#total)" strokeWidth={2} strokeDasharray="5 5" />
          </AreaChart>
        </ResponsiveContainer>
      ) : (
        <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>
          No forecast data available
        </div>
      )}
    </div>
  )
}

// ─── Weather Panel ────────────────────────────────────────────────────────────

function WeatherPanel({ kw, bw }) {
  const [loc, setLoc] = useState('kutch')
  const w = loc === 'kutch' ? kw : bw
  if (!w) return null

  const items = [
    { label: 'Condition',    value: w.condition,                              icon: '🌤️' },
    { label: 'Temperature',  value: `${fmt(w.temperature)}°C`,               icon: '🌡️' },
    { label: 'Wind Speed',   value: `${fmt(w.wind_speed, 2)} m/s`,           icon: '💨' },
    { label: 'Irradiance',   value: `${fmt(w.solar_irradiance, 0)} W/m²`,   icon: '☀️' },
    { label: 'Cloud Cover',  value: `${fmt(w.cloud_cover, 0)}%`,             icon: '☁️' },
    { label: 'Humidity',     value: `${fmt(w.humidity, 0)}%`,                icon: '💧' },
    { label: 'Pressure',     value: `${fmt(w.pressure, 0)} hPa`,            icon: '📊' },
  ]

  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ fontWeight: 700, fontSize: 14 }}>Weather Conditions</div>
        <div style={{ display: 'flex', gap: 6 }}>
          {['kutch', 'banaskantha'].map(l => (
            <button key={l} onClick={() => setLoc(l)} style={{
              padding: '4px 10px', borderRadius: 6, fontSize: 11, fontWeight: 600,
              background: loc === l ? 'rgba(56,189,248,0.2)' : 'var(--surface2)',
              color: loc === l ? 'var(--accent)' : 'var(--muted)',
              border: `1px solid ${loc === l ? 'rgba(56,189,248,0.4)' : 'var(--border)'}`,
            }}>
              {l === 'kutch' ? 'Kutch' : 'Banas'}
            </button>
          ))}
        </div>
      </div>
      <div style={{ fontSize: 10, color: '#f59e0b', marginBottom: 12 }}>SIMULATED WEATHER DATA</div>

      {items.map(item => (
        <div key={item.label} style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '7px 0', borderBottom: '1px solid var(--border)'
        }}>
          <span style={{ color: 'var(--muted)', fontSize: 12 }}>{item.icon} {item.label}</span>
          <span style={{ fontWeight: 600, fontSize: 13 }}>{item.value}</span>
        </div>
      ))}

      {/* Solar impact */}
      <div style={{
        marginTop: 12, padding: '8px 12px',
        background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)',
        borderRadius: 8, fontSize: 11
      }}>
        <div style={{ color: '#f59e0b', fontWeight: 600, marginBottom: 2 }}>⚡ Weather Impact</div>
        <div style={{ color: 'var(--muted)' }}>
          {w.solar_irradiance > 700
            ? 'Excellent solar generation conditions'
            : w.solar_irradiance > 400
            ? 'Moderate solar conditions'
            : 'Poor solar conditions — generation reduced'}
        </div>
      </div>
    </div>
  )
}

// ─── Asset Health Table ───────────────────────────────────────────────────────

function AssetHealthTable({ assets }) {
  const [filter, setFilter] = useState('all')
  const [sort, setSort] = useState({ key: 'efficiency', dir: 'asc' })
  const [page, setPage] = useState(0)
  const PER_PAGE = 12

  if (!assets?.length) return null

  const filtered = assets.filter(a => {
    if (filter === 'all') return true
    if (filter === 'warning') return a.status === 'WARNING'
    if (filter === 'critical') return a.status === 'CRITICAL'
    if (filter === 'solar') return a.asset_type === 'solar'
    if (filter === 'wind') return a.asset_type === 'wind'
    return true
  })

  const sorted = [...filtered].sort((a, b) => {
    const va = a[sort.key] ?? 0
    const vb = b[sort.key] ?? 0
    return sort.dir === 'asc' ? va - vb : vb - va
  })

  const paged = sorted.slice(page * PER_PAGE, (page + 1) * PER_PAGE)
  const totalPages = Math.ceil(sorted.length / PER_PAGE)

  const statusIcon = (s) => s === 'HEALTHY' ? '🟢' : s === 'WARNING' ? '🟡' : '🔴'
  const riskBadge = (r) => {
    const cls = r === 'LOW' ? 'badge-low' : r === 'MEDIUM' ? 'badge-medium' : r === 'HIGH' ? 'badge-high' : 'badge-critical-risk'
    return <span className={cls} style={{ fontSize: 10, padding: '2px 7px', borderRadius: 4, fontWeight: 700 }}>{r}</span>
  }
  const statusBadge = (s) => {
    const cls = s === 'HEALTHY' ? 'badge-healthy' : s === 'WARNING' ? 'badge-warning' : 'badge-critical'
    return <span className={cls} style={{ fontSize: 10, padding: '2px 7px', borderRadius: 4, fontWeight: 700 }}>{statusIcon(s)} {s}</span>
  }

  const SortHeader = ({ label, field }) => (
    <th
      onClick={() => setSort(s => ({ key: field, dir: s.key === field && s.dir === 'desc' ? 'asc' : 'desc' }))}
      style={{ padding: '10px 12px', textAlign: 'left', cursor: 'pointer', whiteSpace: 'nowrap',
               color: sort.key === field ? 'var(--accent)' : 'var(--muted)', fontSize: 11, fontWeight: 600,
               userSelect: 'none' }}
    >
      {label} {sort.key === field ? (sort.dir === 'asc' ? '↑' : '↓') : ''}
    </th>
  )

  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden' }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Asset Health</div>
          <div style={{ fontSize: 11, color: 'var(--muted)' }}>{filtered.length} assets • Click header to sort</div>
        </div>
        <div style={{ display: 'flex', gap: 6, marginLeft: 'auto', flexWrap: 'wrap' }}>
          {['all','solar','wind','warning','critical'].map(f => (
            <button key={f} onClick={() => { setFilter(f); setPage(0) }} style={{
              padding: '4px 10px', borderRadius: 6, fontSize: 11, fontWeight: 600,
              background: filter === f ? 'rgba(56,189,248,0.2)' : 'var(--surface2)',
              color: filter === f ? 'var(--accent)' : 'var(--muted)',
              border: `1px solid ${filter === f ? 'rgba(56,189,248,0.4)' : 'var(--border)'}`,
            }}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ background: 'var(--surface2)' }}>
            <tr>
              <SortHeader label="Asset" field="asset_id" />
              <th style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--muted)', fontSize: 11, fontWeight: 600 }}>Type</th>
              <th style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--muted)', fontSize: 11, fontWeight: 600 }}>Location</th>
              <SortHeader label="Actual (MW)" field="actual_output_mw" />
              <SortHeader label="Expected (MW)" field="expected_output_mw" />
              <SortHeader label="Efficiency %" field="efficiency" />
              <SortHeader label="Risk" field="risk_score" />
              <th style={{ padding: '10px 12px', textAlign: 'left', color: 'var(--muted)', fontSize: 11, fontWeight: 600 }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((a, i) => (
              <tr key={a.asset_id} style={{
                borderTop: '1px solid var(--border)',
                background: a.status === 'CRITICAL' ? 'rgba(239,68,68,0.04)' : a.status === 'WARNING' ? 'rgba(234,179,8,0.03)' : 'transparent',
              }}>
                <td style={{ padding: '10px 12px', fontWeight: 700, fontSize: 13 }}>
                  {a.asset_type === 'solar' ? <Sun size={12} style={{ marginRight: 4, color: '#f59e0b', verticalAlign: 'middle' }} /> : <Wind size={12} style={{ marginRight: 4, color: '#38bdf8', verticalAlign: 'middle' }} />}
                  {a.asset_id}
                </td>
                <td style={{ padding: '10px 12px', color: 'var(--muted)', fontSize: 12 }}>
                  {a.asset_type === 'solar' ? '☀️ Solar' : '💨 Wind'}
                </td>
                <td style={{ padding: '10px 12px', color: 'var(--muted)', fontSize: 12 }}>
                  <MapPin size={11} style={{ marginRight: 3, verticalAlign: 'middle' }} />
                  {a.location === 'kutch' ? 'Kutch' : 'Banas'}
                </td>
                <td style={{ padding: '10px 12px', fontWeight: 600 }}>{fmt(a.actual_output_mw, 3)}</td>
                <td style={{ padding: '10px 12px', color: 'var(--muted)' }}>{fmt(a.expected_output_mw, 3)}</td>
                <td style={{ padding: '10px 12px' }}>
                  <span style={{ color: effColor(a.efficiency), fontWeight: 700 }}>{fmt(a.efficiency)}%</span>
                </td>
                <td style={{ padding: '10px 12px' }}>{riskBadge(a.risk_level)}</td>
                <td style={{ padding: '10px 12px' }}>{statusBadge(a.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'center', gap: 8 }}>
          {Array.from({ length: totalPages }, (_, i) => (
            <button key={i} onClick={() => setPage(i)} style={{
              width: 28, height: 28, borderRadius: 6, border: `1px solid ${page === i ? 'var(--accent)' : 'var(--border)'}`,
              background: page === i ? 'rgba(56,189,248,0.2)' : 'var(--surface2)',
              color: page === i ? 'var(--accent)' : 'var(--muted)', fontSize: 12,
            }}>{i + 1}</button>
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Park Map ────────────────────────────────────────────────────────────────

function ParkMap({ assets, substations }) {
  if (!assets?.length) return null

  // Simple SVG map representation
  const solarAssets = assets.filter(a => a.asset_type === 'solar')
  const windAssets  = assets.filter(a => a.asset_type === 'wind')

  // Normalize lat/lon to SVG coordinates
  const lats = [...assets.map(a => a.lat), ...(substations || []).map(s => s.lat)]
  const lons = [...assets.map(a => a.lon), ...(substations || []).map(s => s.lon)]
  const minLat = Math.min(...lats), maxLat = Math.max(...lats)
  const minLon = Math.min(...lons), maxLon = Math.max(...lons)

  const W = 900, H = 320, PAD = 40
  const toX = lon => PAD + ((lon - minLon) / (maxLon - minLon || 1)) * (W - PAD * 2)
  const toY = lat => H - PAD - ((lat - minLat) / (maxLat - minLat || 1)) * (H - PAD * 2)

  const statusColor = s => s === 'HEALTHY' ? '#22c55e' : s === 'WARNING' ? '#eab308' : '#ef4444'

  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Live Park Map</div>
          <div style={{ fontSize: 11, color: 'var(--muted)' }}>Kutch & Banaskantha — Visual monitoring only. No direct control.</div>
        </div>
        <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--muted)', alignItems: 'center' }}>
          <span>🟢 Healthy</span><span>🟡 Warning</span><span>🔴 Critical</span>
          <span>☀️ Solar</span><span>💨 Wind</span><span>⚡ Substation</span>
        </div>
      </div>

      <div style={{ background: '#0d1929', borderRadius: 8, overflow: 'hidden', position: 'relative' }}>
        {/* Location labels */}
        <div style={{ position: 'absolute', top: 8, left: 12, fontSize: 10, color: '#38bdf8', fontWeight: 700 }}>
          📍 KUTCH
        </div>
        <div style={{ position: 'absolute', top: 8, right: 12, fontSize: 10, color: '#a855f7', fontWeight: 700 }}>
          📍 BANASKANTHA
        </div>
        <div style={{ position: 'absolute', bottom: 6, left: '50%', transform: 'translateX(-50%)',
                      fontSize: 9, color: 'rgba(255,255,255,0.3)' }}>
          MONITORING VIEW ONLY — NOT A CONTROL INTERFACE
        </div>

        <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: 'block' }}>
          {/* Grid lines */}
          {[0.25, 0.5, 0.75].map(f => (
            <React.Fragment key={f}>
              <line x1={W * f} y1={0} x2={W * f} y2={H} stroke="rgba(255,255,255,0.04)" strokeWidth={1} />
              <line x1={0} y1={H * f} x2={W} y2={H * f} stroke="rgba(255,255,255,0.04)" strokeWidth={1} />
            </React.Fragment>
          ))}

          {/* Substations */}
          {substations?.map(s => {
            const x = toX(s.lon), y = toY(s.lat)
            return (
              <g key={s.asset_id}>
                <polygon
                  points={`${x},${y-10} ${x+10},${y+6} ${x-10},${y+6}`}
                  fill="rgba(250,204,21,0.15)" stroke="#fbbf24" strokeWidth={1.5}
                />
                <text x={x} y={y+18} textAnchor="middle" fill="#fbbf24" fontSize={8} fontWeight={600}>{s.asset_id}</text>
              </g>
            )
          })}

          {/* Solar assets */}
          {solarAssets.map(a => {
            const x = toX(a.lon), y = toY(a.lat)
            const col = statusColor(a.status)
            return (
              <g key={a.asset_id}>
                <circle cx={x} cy={y} r={a.status !== 'HEALTHY' ? 7 : 5}
                  fill={`${col}22`} stroke={col} strokeWidth={1.5}
                />
                <text x={x} y={y+1} textAnchor="middle" dominantBaseline="middle"
                  fill={col} fontSize={7}>☀</text>
                {a.status !== 'HEALTHY' && (
                  <circle cx={x} cy={y} r={10} fill="none" stroke={col} strokeWidth={1}
                    opacity={0.4} className="animate-pulse-slow" />
                )}
                <title>{a.asset_id}: {a.efficiency?.toFixed(1)}% efficiency — {a.status}</title>
              </g>
            )
          })}

          {/* Wind assets */}
          {windAssets.map(a => {
            const x = toX(a.lon), y = toY(a.lat)
            const col = statusColor(a.status)
            return (
              <g key={a.asset_id}>
                <rect x={x-4} y={y-4} width={8} height={8}
                  fill={`${col}22`} stroke={col} strokeWidth={1.5} rx={2}
                />
                <text x={x} y={y+1} textAnchor="middle" dominantBaseline="middle"
                  fill={col} fontSize={7}>⊛</text>
                {a.status !== 'HEALTHY' && (
                  <rect x={x-8} y={y-8} width={16} height={16}
                    fill="none" stroke={col} strokeWidth={1} rx={4}
                    opacity={0.4} className="animate-pulse-slow" />
                )}
                <title>{a.asset_id}: {a.efficiency?.toFixed(1)}% efficiency — {a.status}</title>
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}
