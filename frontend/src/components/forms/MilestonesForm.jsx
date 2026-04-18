import { useState } from "react"
import { generateMilestone } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function MilestonesForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ milestone_type: "anniversary", customer_name: "", customer_phone: "", milestone_value: "", vehicle: "", last_service: "" })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await generateMilestone(form); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const placeholder = { anniversary: "e.g. 1 year", visit_count: "e.g. 10th visit", mileage: "e.g. 100,000 miles" }[form.milestone_type]

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Milestone Type">
        <select style={inputStyle} value={form.milestone_type} onChange={set("milestone_type")}>
          <option value="anniversary">Anniversary</option>
          <option value="visit_count">Visit Count</option>
          <option value="mileage">Mileage</option>
        </select>
      </Field>
      <Field label="Customer Name"><input style={inputStyle} value={form.customer_name} onChange={set("customer_name")} placeholder="e.g. Patricia Moore" /></Field>
      <Field label="Customer Phone"><input style={inputStyle} value={form.customer_phone} onChange={set("customer_phone")} placeholder="e.g. (303) 555-4321" /></Field>
      <Field label="Milestone Value"><input style={inputStyle} value={form.milestone_value} onChange={set("milestone_value")} placeholder={placeholder} /></Field>
      <Field label="Vehicle"><input style={inputStyle} value={form.vehicle} onChange={set("vehicle")} placeholder="e.g. 2016 Honda CR-V" /></Field>
      <Field label="Last Service Date"><input style={inputStyle} type="date" value={form.last_service} onChange={set("last_service")} /></Field>
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
MilestonesForm.apiFunc = generateMilestone
