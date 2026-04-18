import { useState } from "react"
import { generateWaitTime } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function WaitTimeForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ status: "all", service_type: "" })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await generateWaitTime(form); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Status Update Type">
        <select style={inputStyle} value={form.status} onChange={set("status")}>
          <option value="all">All Status Updates</option>
          <option value="drop_off_confirmation">Drop-Off Confirmation</option>
          <option value="inspection_update">Inspection Update</option>
          <option value="repair_in_progress">Repair In Progress</option>
          <option value="ready_for_pickup">Ready for Pickup</option>
          <option value="delayed_notification">Delay Notification</option>
        </select>
      </Field>
      <Field label="Service Type">
        <input style={inputStyle} value={form.service_type} onChange={set("service_type")} placeholder="e.g. Brake job, Transmission service" />
      </Field>
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
WaitTimeForm.apiFunc = generateWaitTime
