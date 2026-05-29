import { useState, useEffect } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
         ReferenceLine, ResponsiveContainer, Cell } from "recharts"
import { getShap } from "../api/client"

export default function ShapPanel({ productIds }) {
  const [pid, setPid]     = useState(1)
  const [data, setData]   = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    getShap(pid).then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false))
  }, [pid])

  const chart = data?.top_contributions
    ? [...data.top_contributions]
        .sort((a,b) => Math.abs(b.shap_value)-Math.abs(a.shap_value))
        .slice(0,10)
        .map(c => ({ name: c.feature.replace(/_/g," ").slice(0,20),
                     shap: parseFloat(c.shap_value.toFixed(2)),
                     dir: c.direction }))
    : []

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <div className="card-title">Why this prediction?</div>
          <div className="card-sub" style={{marginBottom:0}}>
            SHAP feature contributions
          </div>
        </div>
        <select className="shap-select" value={pid}
          onChange={e => setPid(Number(e.target.value))}>
          {(productIds||[1,2,3,4,5,6,7,8,9,10]).map(id => (
            <option key={id} value={id}>Product {id}</option>
          ))}
        </select>
      </div>
      {data && (
        <div className="shap-meta">
          Prediction: <strong>{data.prediction} units</strong>
          &nbsp;· base value: {data.base_value}
        </div>
      )}
      {loading
        ? <div className="empty">Loading SHAP values...</div>
        : (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chart} layout="vertical"
              margin={{top:4,right:20,left:110,bottom:4}}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f4f8" />
              <XAxis type="number" tick={{fontSize:11}} />
              <YAxis type="category" dataKey="name" tick={{fontSize:10}} width:={105} />
              <Tooltip formatter={v => [`${v>0?"+":""}${v}`,"SHAP"]} />
              <ReferenceLine x={0} stroke="#94a3b8" />
              <Bar dataKey="shap" radius={[0,4,4,0]}>
                {chart.map((c,i) => (
                  <Cell key={i} fill={c.dir==="UP"?"#10b981":"#ef4444"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )
      }
    </div>
  )
}
