import { useState } from "react"
import { generateInspection } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function InspectionForm({ onSubmit, onSubmitStart, loading }) {
  const [mode, setMode] = useState("form")
  const [form, setForm] = useState({ type: "multi_point", customer: "", vehicle: "", mileage: "", results: "" })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await generateInspection({ ...form, mode }); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const tabBtn = (v, label) => (
    <button type="button" onClick={() => setMode(v)} style={{ flex: 1, padding: "9px 0", border: "none", borderRadius: 2, background: mode === v ? gold : "#111113", color: mode === v ? "#0B0B0D" : "#666", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</button>
  )

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#0B0B0D", padding: 4, borderRadius: 3 }}>
        {tabBtn("form", "Form")}
        {tabBtn("report", "Report")}
      </div>
      {mode === "form" && (
        <Field label="Inspection Type">
          <select style={inputStyle} value={form.type} onChange={set("type")}>
            <option value="multi_point">Multi-Point</option>
            <option value="pre_purchase">Pre-Purchase</option>
            <option value="seasonal">Seasonal</option>
          </select>
        </Field>
      )}
      <Field label="Customer Name"><input style={inputStyle} value={form.customer} onChange={set("customer")} placeholder="e.g. David Kim" /></Field>
      <Field label="Vehicle"><input style={inputStyle} value={form.vehicle} onChange={set("vehicle")} placeholder="e.g. 2020 Ford F-150" /></Field>
      <Field label="Current Mileage"><input style={inputStyle} type="number" value={form.mileage} onChange={set("mileage")} placeholder="e.g. 45000" /></Field>
      {mode === "report" && (
        <Field label="Inspection Results (JSON)">
          <textarea style={{ ...inputStyle, height: 120, resize: "vertical" }} value={form.results} onChange={set("results")} placeholder={'[{"item": "Front brakes", "condition": "poor", "urgency": "high", "notes": "3mm remaining"}]'} />
        </Field>
      )}
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
InspectionForm.apiFunc = generateInspection
