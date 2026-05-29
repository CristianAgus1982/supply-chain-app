import { useState } from "react"
import { TrendingUp, TrendingDown, Truck } from "lucide-react"

const ICONS = { DEMAND_SPIKE: TrendingUp, DEMAND_DROP: TrendingDown, SUPPLY_RISK: Truck }
const LABELS = { DEMAND_SPIKE:"Demand Spike", DEMAND_DROP:"Demand Drop", SUPPLY_RISK:"Supply Risk" }

function AlertRow({ a }) {
  const Icon = ICONS[a.alert_type] || Truck
  return (
    <div className={`alert-row ${a.alert_type}`}>
      <Icon size={18} style={{marginTop:2,flexShrink:0,color:"#64748b"}} />
      <div className="alert-body">
        <div className="alert-title-row">
          <span>Product {a.product_id}</span>
          <span className={`badge ${a.alert_type}`}>{LABELS[a.alert_type]}</span>
          <span className={`badge ${a.severity}`}>{a.severity}</span>
        </div>
        <div className="alert-detail">
          Predicted <strong>{a.predicted}</strong> units · recent avg {a.recent_avg}
          &nbsp;(<span style={{color: a.change_pct>=0?"#16a34a":"#dc2626"}}>
            {a.change_pct>0?"+":""}{a.change_pct}%
          </span>)
        </div>
        <div className="alert-action">{a.action}</div>
      </div>
    </div>
  )
}

export default function AlertsPanel({ alerts }) {
  const [f, setF] = useState("ALL")
  const shown = f === "ALL" ? alerts : alerts.filter(a => a.severity === f)
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          Active Alerts <span style={{color:"#ef4444"}}>({alerts.length})</span>
        </div>
        <div className="filters">
          {["ALL","HIGH","MEDIUM"].map(v => (
            <button key={v} className={`filter-btn${f===v?" active":""}`}
              onClick={() => setF(v)}>{v}</button>
          ))}
        </div>
      </div>
      <div className="alert-list">
        {shown.length === 0
          ? <div className="empty">No alerts for this filter</div>
          : shown.map((a,i) => <AlertRow key={i} a={a} />)
        }
      </div>
    </div>
  )
}
