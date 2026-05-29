import { useState, useEffect } from "react"
import { getLatestForecasts, getAlerts, getAlertsSummary } from "./api/client"
import KPICards      from "./components/KPICards"
import ForecastChart from "./components/ForecastChart"
import AlertsPanel   from "./components/AlertsPanel"
import ShapPanel     from "./components/ShapPanel"

export default function App() {
  const [forecasts, setForecasts] = useState([])
  const [alerts,    setAlerts]    = useState([])
  const [summary,   setSummary]   = useState(null)
  const [status,    setStatus]    = useState("loading")
  const [updated,   setUpdated]   = useState(null)

  async function fetchAll() {
    setStatus("loading")
    try {
      const [fc, al, sm] = await Promise.all([
        getLatestForecasts(),
        getAlerts().then(r => r.alerts),
        getAlertsSummary(),
      ])
      setForecasts(fc); setAlerts(al); setSummary(sm)
      setStatus("ok"); setUpdated(new Date().toLocaleTimeString())
    } catch(e) { setStatus("error") }
  }

  useEffect(() => { fetchAll() }, [])
  const productIds = forecasts.map(f => f.product_id)

  return (
    <div>
      <header className="header">
        <div className="header-left">
          <h1>Supply Chain Planning</h1>
          <p>XGBoost Demand Forecasting Dashboard</p>
        </div>
        <div className="header-right">
          <div className="status">
            <div className={`dot ${status}`} />
            <span>
              {status==="ok" ? `API connected · ${updated}` :
               status==="error" ? "API unreachable" : "Connecting..."}
            </span>
          </div>
          <button className="btn" onClick={fetchAll}>Refresh</button>
        </div>
      </header>
      {status==="error" && (
        <div className="error-banner">
          Cannot connect to FastAPI. Make sure the server is running on localhost:8000
        </div>
      )}
      <main className="main">
        <KPICards forecasts={forecasts} summary={summary} />
        <ForecastChart forecasts={forecasts} />
        <div className="bottom-grid">
          <AlertsPanel alerts={alerts} />
          <ShapPanel productIds={productIds} />
        </div>
      </main>
    </div>
  )
}
