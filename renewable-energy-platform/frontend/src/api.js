import axios from 'axios'

const BASE = '/api'

const api = axios.create({ baseURL: BASE, timeout: 15000 })

export const getDashboard = () => api.get('/dashboard')
export const getWeather = () => api.get('/weather')
export const getHistoricalGeneration = (hours = 24) => api.get(`/generation/historical?hours=${hours}`)
export const getForecast = (hours = 6) => api.get(`/generation/forecast?hours=${hours}`)
export const getMaintenanceRisks = () => api.get('/maintenance/risks')
export const getGridStatus = () => api.get('/grid/status')
export const getRecommendations = () => api.get('/recommendations')
export const submitDecision = (rec_id, decision, note) =>
  api.post('/recommendations/decide', { rec_id, decision, note })
export const getDecisionLog = () => api.get('/decisions/log')
export const getAgentActivity = () => api.get('/agents/activity')
export const sendChatMessage = (message) => api.post('/chat', { message })
export const runScenario = (scenario) => api.post('/scenario/run', { scenario })
export const resetScenario = () => api.post('/scenario/reset')
export const getHealth = () => api.get('/health')
