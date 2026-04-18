import { useState } from "react"
import { generateEstimate } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function EstimatesForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ customer: "", vehicle: "", items: "" })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await generateEstimate(form); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Customer Name">
        <input style={inputStyle} value={form.customer} onChange={set("customer")} placeholder="e.g. James Rivera" />
      </Field>
      <Field label="Vehicle">
        <input style={inputStyle} value={form.vehicle} onChange={set("vehicle")} placeholder="e.g. 2017 Honda Accord EX" />
      </Field>
      <Field label="Estimate Line Items">
        <textarea style={{ ...inputStyle, height: 140, resize: "vertical" }} value={form.items} onChange={set("items")} placeholder={'JSON array of line items:\n[{"part": "Front brake pads", "part_cost": 45, "labor_hours": 1.5, "labor_cost": 120, "urgency": "high"}]'} />
      </Field>
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
EstimatesForm.apiFunc = generateEstimate
