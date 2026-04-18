import { useState } from "react"
import { techSummary } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function TechForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({
    period: "week",
    date: "",
    technicians: '[{"name": "Alex Smith", "hours_clocked": 40, "hours_billed": 38, "jobs_completed": 12, "revenue_generated": 3200, "comebacks": 0}]',
  })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await techSummary(form); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Period">
        <select style={inputStyle} value={form.period} onChange={set("period")}>
          <option value="day">Daily</option>
          <option value="week">Weekly</option>
          <option value="month">Monthly</option>
        </select>
      </Field>
      <Field label="Date / Week Ending">
        <input style={inputStyle} type="date" value={form.date} onChange={set("date")} />
      </Field>
      <Field label="Technician Data (JSON array)">
        <textarea style={{ ...inputStyle, height: 160, resize: "vertical", fontFamily: "monospace", fontSize: 11 }} value={form.technicians} onChange={set("technicians")} />
      </Field>
      <p style={{ fontSize: 11, color: "#444", lineHeight: 1.5, margin: "0 0 16px" }}>
        Fields: name, hours_clocked, hours_billed, jobs_completed, revenue_generated, comebacks
      </p>
      <button type="submit" disabled={loading} style={{ width: "100%", padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate Summary →"}
      </button>
    </form>
  )
}
TechForm.apiFunc = techSummary
