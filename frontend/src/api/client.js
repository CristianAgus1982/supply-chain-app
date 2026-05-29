const BASE_URL = "http://localhost:8000"

export async function getLatestForecasts() {
  const r = await fetch(`${BASE_URL}/forecast/latest`)
  if (!r.ok) throw new Error("Failed to fetch forecasts")
  return r.json()
}

export async function getAlerts(severity = null) {
  const url = severity
    ? `${BASE_URL}/alerts?severity=${severity}`
    : `${BASE_URL}/alerts`
  const r = await fetch(url)
  if (!r.ok) throw new Error("Failed to fetch alerts")
  return r.json()
}

export async function getAlertsSummary() {
  const r = await fetch(`${BASE_URL}/alerts/summary`)
  if (!r.ok) throw new Error("Failed to fetch summary")
  return r.json()
}

export async function getShap(productId) {
  const r = await fetch(`${BASE_URL}/forecast/shap/${productId}`)
  if (!r.ok) throw new Error("Failed to fetch SHAP")
  return r.json()
}

export async function getHealth() {
  const r = await fetch(`${BASE_URL}/`)
  if (!r.ok) throw new Error("API not reachable")
  return r.json()
}
