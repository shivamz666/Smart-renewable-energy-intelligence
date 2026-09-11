import React, { useState, useEffect, useCallback } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import {
  Sun, Wind, Zap, Activity, BarChart2, Wrench, Grid, MessageSquare,
  ClipboardList, PlayCircle, Shield, AlertTriangle, CheckCircle,
  RefreshCw, MapPin, Cpu, ChevronRight, TrendingUp, TrendingDown, Minus
} from 'lucide-react'
import { getDashboard, runScenario, resetScenario } from './api'

// Pages
import DashboardPage from './pages/DashboardPage'
import MaintenancePage from './pages/MaintenancePage'
import GridPage from './pages/GridPage'
import AgentsPage from './pages/AgentsPage'
import DecisionLogPage from './pages/DecisionLogPage'
import ChatPage from './pages/ChatPage'
import ScenariosPage from './pages/ScenariosPage'

// ─── Context ──────────────────────────────────────────────────────────────────

export const AppContext = React.createContext(null)

// ─── App ─────────────────────────────────────────────────────────────────────

export default function App() {
  const [state, setState] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastRefresh, setLastRefresh] = useState(null)
  const [scenario, setScenario] = useState('normal')
  const [scenarioRunning, setScenarioRunning] = useState(false)

  const fetchData = useCallback(async () => {
    try {
      const res = await getDashboard()
      setState(res.data)
      setLastRefresh(new Date())
      setError(null)
    } catch (e) {
      setError('Unable to connect to backend. Make sure the Python server is running.')
    } finally {
      setLoading(false)
    }
  }, [])

  // Auto-refresh every 30 seconds
  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [fetchData])

  const handleRunScenario = async (s) => {
    setScenarioRunning(true)
    setScenario(s)
    try {
      const res = await runScenario(s)
      setState(res.data)
      setLastRefresh(new Date())
    } catch (e) {
      console.error(e)
    } finally {
      setScenarioRunning(false)
    }
  }

  const handleResetScenario = async () => {
    setScenarioRunning(true)
    try {
      await resetScenario()
      setScenario('normal')
      await fetchData()
    } catch (e) {
      console.error(e)
    } finally {
      setScenarioRunning(false)
    }
  }

  const contextValue = {
    state,
    loading,
    error,
    lastRefresh,
    scenario,
    scenarioRunning,
    refresh: fetchData,
    runScenario: handleRunScenario,
    resetScenario: handleResetScenario,
  }

  return (
    <AppContext.Provider value={contextValue}>
      <BrowserRouter>
        <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg)' }}>
          <Sidebar />
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <TopBar state={state} loading={loading} lastRefresh={lastRefresh} onRefresh={fetchData} scenario={scenario} />
            <main style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
              {error && <ErrorBanner message={error} />}
              {loading && !state ? (
                <LoadingScreen />
              ) : (
                <Routes>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/maintenance" element={<MaintenancePage />} />
                  <Route path="/grid" element={<GridPage />} />
                  <Route path="/agents" element={<AgentsPage />} />
                  <Route path="/log" element={<DecisionLogPage />} />
                  <Route path="/chat" element={<ChatPage />} />
                  <Route path="/scenarios" element={<ScenariosPage />} />
                </Routes>
              )}
            </main>
          </div>
        </div>
      </BrowserRouter>
    </AppContext.Provider>
  )
}

// ─── Sidebar ─────────────────────────────────────────────────────────────────

function Sidebar() {
  const { state } = React.useContext(AppContext)
  const activeRecs = state?.active_recommendations?.length || 0
  const highRisk = state?.maintenance_risks?.filter(r => r.risk_level === 'HIGH' || r.risk_level === 'CRITICAL').length || 0

  const navItems = [
    { to: '/',            icon: <BarChart2 size={18}/>, label: 'Dashboard' },
    { to: '/maintenance', icon: <Wrench size={18}/>,    label: 'Maintenance', badge: highRisk },
    { to: '/grid',        icon: <Grid size={18}/>,      label: 'Grid & Energy', badge: activeRecs },
    { to: '/agents',      icon: <Cpu size={18}/>,       label: 'Agent Activity' },
    { to: '/log',         icon: <ClipboardList size={18}/>, label: 'Decision Log' },
    { to: '/chat',        icon: <MessageSquare size={18}/>, label: 'AI Assistant' },
    { to: '/scenarios',   icon: <PlayCircle size={18}/>, label: 'Demo Scenarios' },
  ]

  return (
    <nav style={{
      width: 220, background: 'var(--surface)', borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', flexShrink: 0
    }}>
      {/* Logo */}
      <div style={{ padding: '20px 16px 16px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <div style={{
            background: 'linear-gradient(135deg, #f59e0b, #38bdf8)',
            borderRadius: 8, width: 32, height: 32,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Zap size={18} color="#fff" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text)', lineHeight: 1.2 }}>
              Renewable AI
            </div>
            <div style={{ fontSize: 10, color: 'var(--muted)' }}>Intelligence Platform</div>
          </div>
        </div>
        <div style={{
          fontSize: 9, color: '#f59e0b', background: 'rgba(245,158,11,0.1)',
          border: '1px solid rgba(245,158,11,0.3)', borderRadius: 4,
          padding: '2px 6px', textAlign: 'center', fontWeight: 600
        }}>
          DEMO / SIMULATED DATA
        </div>
      </div>

      {/* Nav */}
      <div style={{ flex: 1, padding: '12px 8px' }}>
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '9px 12px', borderRadius: 8, marginBottom: 2,
              color: isActive ? '#fff' : 'var(--muted)',
              background: isActive ? 'rgba(56,189,248,0.15)' : 'transparent',
              borderLeft: isActive ? '3px solid var(--accent)' : '3px solid transparent',
              textDecoration: 'none', fontSize: 13, fontWeight: isActive ? 600 : 400,
              transition: 'all 0.15s',
            })}
          >
            {item.icon}
            <span style={{ flex: 1 }}>{item.label}</span>
            {item.badge > 0 && (
              <span style={{
                background: 'var(--red)', color: '#fff', borderRadius: 10,
                fontSize: 10, fontWeight: 700, padding: '1px 6px', minWidth: 18, textAlign: 'center'
              }}>
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </div>

      {/* Safety banner */}
      <div style={{
        margin: '0 8px 12px', padding: '10px 12px',
        background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)',
        borderRadius: 8, fontSize: 10, color: '#a5b4fc'
      }}>
        <Shield size={12} style={{ marginRight: 6, verticalAlign: 'middle' }} />
        <strong>Human-in-the-Loop</strong>
        <br />AI recommendations require operator approval
      </div>
    </nav>
  )
}

// ─── TopBar ───────────────────────────────────────────────────────────────────

function TopBar({ state, loading, lastRefresh, onRefresh, scenario }) {
  const kpis = state?.kpis || {}
  const park = state?.park_summary || {}

  return (
    <header style={{
      background: 'var(--surface)', borderBottom: '1px solid var(--border)',
      padding: '0 20px', height: 64, display: 'flex', alignItems: 'center', gap: 20,
      flexShrink: 0
    }}>
      <div style={{ flex: 1 }}>
        <h1 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text)' }}>
          Smart Renewable Energy Intelligence
        </h1>
        <div style={{ fontSize: 11, color: 'var(--muted)', display: 'flex', gap: 12, marginTop: 1 }}>
          <span>
            <MapPin size={10} style={{ marginRight: 3, verticalAlign: 'middle' }} />
            Kutch & Banaskantha, Gujarat
          </span>
          <span style={{ color: '#f59e0b' }}>● DEMO / SIMULATED DATA</span>
          {scenario !== 'normal' && (
            <span style={{ color: '#a855f7' }}>
              ▶ Scenario: {scenario.replace('_', ' ').toUpperCase()}
            </span>
          )}
        </div>
      </div>

      {/* Quick stats */}
      {kpis.total_renewable_mw !== undefined && (
        <>
          <QuickStat label="Solar" value={`${kpis.solar_generation_mw?.toFixed(1)} MW`} color="#f59e0b" icon={<Sun size={14}/>} />
          <QuickStat label="Wind" value={`${kpis.wind_generation_mw?.toFixed(1)} MW`} color="#38bdf8" icon={<Wind size={14}/>} />
          <QuickStat label="Efficiency" value={`${kpis.park_efficiency_pct?.toFixed(1)}%`} color="#22c55e" icon={<Activity size={14}/>} />
          <div style={{ width: 1, height: 32, background: 'var(--border)' }} />
        </>
      )}

      {/* Park status */}
      {park.overall_status && (
        <div style={{
          padding: '4px 12px', borderRadius: 6, fontSize: 12, fontWeight: 700,
          ...(park.overall_status === 'HEALTHY'
            ? { background: 'rgba(34,197,94,0.15)', color: '#22c55e', border: '1px solid rgba(34,197,94,0.3)' }
            : { background: 'rgba(234,179,8,0.15)', color: '#eab308', border: '1px solid rgba(234,179,8,0.3)' }
          )
        }}>
          {park.overall_status === 'HEALTHY' ? '✅ HEALTHY' : '⚠️ ATTENTION'}
        </div>
      )}

      <button
        onClick={onRefresh}
        disabled={loading}
        style={{
          background: 'var(--surface2)', border: '1px solid var(--border)', color: 'var(--muted)',
          borderRadius: 8, padding: '6px 10px', display: 'flex', alignItems: 'center', gap: 6,
          fontSize: 12, transition: 'all 0.15s'
        }}
      >
        <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
        {lastRefresh ? lastRefresh.toLocaleTimeString() : 'Loading...'}
      </button>
    </header>
  )
}

function QuickStat({ label, value, color, icon }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, color, fontSize: 13, fontWeight: 700 }}>
        {icon} {value}
      </div>
      <div style={{ fontSize: 10, color: 'var(--muted)' }}>{label}</div>
    </div>
  )
}

function ErrorBanner({ message }) {
  return (
    <div style={{
      background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
      borderRadius: 8, padding: '12px 16px', marginBottom: 16,
      display: 'flex', alignItems: 'center', gap: 10, color: '#fca5a5'
    }}>
      <AlertTriangle size={16} color="#ef4444" />
      <span>{message}</span>
    </div>
  )
}

function LoadingScreen() {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', height: '60vh', gap: 16
    }}>
      <div style={{
        background: 'linear-gradient(135deg, #f59e0b, #38bdf8)',
        borderRadius: 16, width: 56, height: 56,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        animation: 'pulse 2s ease-in-out infinite'
      }}>
        <Zap size={28} color="#fff" />
      </div>
      <div style={{ color: 'var(--text)', fontSize: 16, fontWeight: 600 }}>
        Initializing AI Agents...
      </div>
      <div style={{ color: 'var(--muted)', fontSize: 13 }}>
        Connecting to Kutch & Banaskantha data streams
      </div>
      <div className="spinner" />
    </div>
  )
}
