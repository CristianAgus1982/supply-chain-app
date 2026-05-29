import { TrendingUp, AlertTriangle, Package, Activity } from "lucide-react"

function KPICard({ title, value, sub, iconColor, Icon }) {
  return (
    <div className="kpi-card">
      <div className={`kpi-icon ${iconColor}`}>
        <Icon size={22} color="white" />
      </div>
      <div>
        <div className="kpi-label">{title}</div>
        <div className="kpi-value">{value}</div>
        <div className="kpi-sub">{sub}</div>
      </div>
    </div>
  )
}

export default function KPICards({ forecasts, summary }) {
  const avg = forecasts.length
    ? Math.round(forecasts.reduce((s,f) => s + f.predicted_demand, 0) / forecasts.length) : 0
  const top = forecasts.length
    ? forecasts.reduce((a,b) => Math.abs(a.change_pct) > Math.abs(b.change_pct) ? a : b) : null
  return (
    <div className="kpi-grid">
      <KPICard title="Products Monitored" value={forecasts.length}
        sub="Active SKUs this week" iconColor="blue" Icon={Package} />
      <KPICard title="Active Alerts" value={summary?.total_alerts ?? 0}
        sub={`${summary?.by_severity?.HIGH ?? 0} HIGH · ${summary?.by_severity?.MEDIUM ?? 0} MEDIUM`}
        iconColor="red" Icon={AlertTriangle} />
      <KPICard title="Avg Predicted Demand" value={avg}
        sub="Units next week" iconColor="green" Icon={TrendingUp} />
      <KPICard title="Highest Variance" value={top ? `P${top.product_id}` : "-"}
        sub={top ? `${top.change_pct > 0 ? "+" : ""}${top.change_pct}% vs recent avg` : ""}
        iconColor="orange" Icon={Activity} />
    </div>
  )
}
