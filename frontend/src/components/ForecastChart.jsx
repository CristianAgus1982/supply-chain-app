import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
         ResponsiveContainer, Cell } from "recharts"

function Tip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{background:"white",border:"1px solid #e2e8f0",borderRadius:8,
                 padding:"10px 14px",fontSize:".82rem",boxShadow:"0 2px 8px rgba(0,0,0,.1)"}}>
      <p style={{fontWeight:700,marginBottom:4}}>Product {d.product_id}</p>
      <p style={{color:"#3b82f6"}}>Predicted: <strong>{d.predicted_demand} units</strong></p>
      <p style={{color:"#64748b"}}>Recent avg: {d.recent_avg}</p>
      <p style={{color:"#64748b"}}>CI: [{d.confidence_lower} – {d.confidence_upper}]</p>
      <p style={{color: d.change_pct >= 0 ? "#10b981" : "#ef4444"}}>
        {d.change_pct > 0 ? "+" : ""}{d.change_pct}% vs avg
      </p>
    </div>
  )
}

export default function ForecastChart({ forecasts }) {
  if (!forecasts.length) return (
    <div className="card"><p className="empty">Loading forecasts...</p></div>
  )
  return (
    <div className="card">
      <div className="card-title">Demand Forecast — Next Week</div>
      <div className="card-sub">
        Predicted units per product. 🟢 Above recent average · 🔴 Below recent average
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={forecasts} margin={{top:8,right:16,left:0,bottom:4}}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f4f8" />
          <XAxis dataKey="product_id" tickFormatter={v => `P${v}`} tick={{fontSize:12}} />
          <YAxis tick={{fontSize:12}} />
          <Tooltip content={<Tip />} />
          <Bar dataKey="predicted_demand" radius={[4,4,0,0]}>
            {forecasts.map(f => (
              <Cell key={f.product_id}
                fill={f.change_pct >= 0 ? "#10b981" : "#ef4444"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
