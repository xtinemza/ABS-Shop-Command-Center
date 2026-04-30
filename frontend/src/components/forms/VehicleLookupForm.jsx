import { useState } from "react"
import { getVehicleSpecs } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }

function Field({ label, children }) { 
  return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> 
}

export default function VehicleLookupForm({ onSubmit, onSubmitStart, loading }) {
  const [query, setQuery] = useState("")
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    
    setError(null)
    onSubmitStart && onSubmitStart()
    try {
      const res = await getVehicleSpecs(query)
      if (res.success) {
        // Format the vehicle specs to look like an AI output so it renders nicely in OutputPanel
        const v = res.vehicle
        let lines = []
        lines.push(`## ${v.name || "Vehicle Specifications"}`)
        lines.push("")
        
        if (v.engines && v.engines.length) {
          lines.push(`**Engines:** ${v.engines.join(", ")}`)
        }
        if (v.oil) lines.push(`**Oil Type:** ${v.oil} (Cap: ${v.oil_cap || 'Unknown'})`)
        if (v.coolant) lines.push(`**Coolant:** ${v.coolant}`)
        if (v.spark_plug) lines.push(`**Spark Plug:** ${v.spark_plug}`)
        lines.push("")
        
        if (v.torque && Object.keys(v.torque).length) {
          lines.push("### Torque Specs")
          Object.entries(v.torque).forEach(([k, val]) => lines.push(`- **${k}:** ${val}`))
          lines.push("")
        }
        
        if (v.intervals && Object.keys(v.intervals).length) {
          lines.push("### Maintenance Intervals")
          Object.entries(v.intervals).forEach(([k, val]) => lines.push(`- **${k}:** ${val}`))
          lines.push("")
        }
        
        if (v.known_issues && v.known_issues.length) {
          lines.push("### Known Issues & Recalls")
          v.known_issues.forEach(iss => lines.push(`- ${iss}`))
        }
        
        const output = lines.join("\n")
        onSubmit && onSubmit({ success: true, output, files: [], content: {} })
      } else {
        setError(res.error || "Vehicle not found.")
        onSubmit && onSubmit({ success: false, error: res.error || "Vehicle not found." })
      }
    } catch (err) {
      setError(err.message)
      onSubmit && onSubmit({ success: false, error: err.message })
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Vehicle Search (Year/Make/Model)">
        <input 
          style={inputStyle} 
          value={query} 
          onChange={e => setQuery(e.target.value)} 
          placeholder="e.g. 2018 Toyota Camry" 
          autoFocus
        />
      </Field>
      
      {error && <div style={{ color: "#E05252", fontSize: 13, marginBottom: 16 }}>{error}</div>}
      
      <button 
        type="submit" 
        disabled={loading || !query.trim()} 
        style={{ 
          width: "100%", padding: "14px 0", borderRadius: 3, 
          border: `1px solid ${gold}66`, 
          background: loading || !query.trim() ? `${gold}44` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, 
          color: loading || !query.trim() ? "#666" : "#0B0B0D", 
          fontSize: 13, fontWeight: 800, cursor: loading || !query.trim() ? "default" : "pointer", 
          fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", 
          textTransform: "uppercase", fontStyle: "italic" 
        }}
      >
        {loading ? "Searching..." : "Instant Lookup ⚡"}
      </button>
      
      <p style={{ fontSize: 11, color: "#666", marginTop: 12, textAlign: "center", fontStyle: "italic" }}>
        Direct database query. Uses 0 AI tokens.
      </p>
    </form>
  )
}
VehicleLookupForm.apiFunc = getVehicleSpecs
