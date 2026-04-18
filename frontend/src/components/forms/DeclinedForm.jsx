import { useState } from "react"
import { generateDeclined } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function DeclinedForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ service: "", urgency: "medium", touches: "1,2,3,4" })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await generateDeclined(form); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Declined Service">
        <input style={inputStyle} value={form.service} onChange={set("service")} placeholder="e.g. Rear brake pad replacement" />
      </Field>
      <Field label="Urgency Level">
        <select style={inputStyle} value={form.urgency} onChange={set("urgency")}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="safety-critical">Safety Critical</option>
        </select>
      </Field>
      <Field label="Follow-Up Touches (comma-separated days)">
        <input style={inputStyle} value={form.touches} onChange={set("touches")} placeholder="e.g. 1,2,3,4" />
      </Field>
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
DeclinedForm.apiFunc = generateDeclined
