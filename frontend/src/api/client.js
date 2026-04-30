const API = import.meta.env.VITE_API_URL || 
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://abs-shop-command-center.onrender.com')
import { supabase } from '../supabase'

async function getHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  const headers = { 'Content-Type': 'application/json' }
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`
  }
  return headers
}

async function post(path, data) {
  const headers = await getHeaders()
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

async function get(path) {
  const headers = await getHeaders()
  const res = await fetch(`${API}${path}`, { headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function getHealth() {
  return get('/api/health')
}

export async function getProfile() {
  return get('/api/profile')
}

export async function saveProfile(data) {
  return post('/api/profile', data)
}

export async function runSetup(data) {
  return post('/api/setup', data)
}

export async function generateAppointments(data) {
  return post('/api/appointments/generate', data)
}

export async function generateWelcomeKit(data) {
  return post('/api/welcome-kit/generate', data)
}

export async function generateWaitTime(data) {
  return post('/api/wait-time/generate', data)
}

export async function generateDeclined(data) {
  return post('/api/declined/generate', data)
}

export async function generateServiceHistory(data) {
  return post('/api/service-history/generate', data)
}

export async function generateEstimate(data) {
  return post('/api/estimates/generate', data)
}

export async function generateInspection(data) {
  return post('/api/inspection/generate', data)
}

export async function checkRecall(data) {
  return post('/api/recall/lookup', data)
}

export async function generateRecallNotify(data) {
  return post('/api/recall/notify', data)
}

export async function equipmentAction(data) {
  return post('/api/equipment/action', data)
}

export async function generateSop(data) {
  return post('/api/sop/generate', data)
}

export async function partsInventory(data) {
  return post('/api/parts/action', data)
}

export async function generatePO(data) {
  return post('/api/parts/purchase-order', data)
}

export async function warrantyClaims(data) {
  return post('/api/warranty/action', data)
}

export async function warrantyReport(data) {
  return post('/api/warranty/report', data)
}

export async function logExpense(data) {
  return post('/api/expenses/action', data)
}

export async function expenseReport(data) {
  return post('/api/expenses/report', data)
}

export async function generateSeasonal(data) {
  return post('/api/seasonal/generate', data)
}

export async function trackReferral(data) {
  return post('/api/referrals/action', data)
}

export async function generateRewards(data) {
  return post('/api/referrals/rewards', data)
}

export async function techSummary(data) {
  return post('/api/tech-productivity/generate', data)
}

export async function generateMilestone(data) {
  return post('/api/milestones/generate', data)
}

export async function getServicePrices() {
  return get('/api/service-prices/')
}

export async function saveServicePrices(data) {
  return post('/api/service-prices/', data)
}

export async function getSops() {
  return get('/api/sop/')
}

export async function saveSops(data) {
  return post('/api/sop/', data)
}

export async function getVehicleSpecs(query) {
  return get(`/api/knowledge-base/vehicle-lookup?q=${encodeURIComponent(query)}`)
}
