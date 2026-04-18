import { useState } from "react"
import { generateSop } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

const BUILT_IN_SOPS = [
  "Customer check-in procedure",
  "Vehicle inspection workflow",
  "Estimate creation and presentation",
  "Parts ordering and receiving",
  "Quality control and test drive",
  "Vehicle delivery procedure",
  "Warranty claim process",
  "Customer complaint handling",
  "Hazardous material handling",
  "End-of-day closing procedure",
  "New technician onboarding",
  "Loaner vehicle policy",
  "After-hours drop-off procedure",
  "Fleet account management",
  "Sublet repair authorization",
  "Towing coordination",
  "Cash and payment handling",
]

export default function SopForm({ onSubmit, onSubmitStart, loading }) {
  const [mode, setMode] = useState("built-in")
  const [procedure, setProcedure] = useState(BUILT_IN_SOPS[0])
  const [custom, setCustom] = useState({ title: "", description: "" })

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    const data = mode === "built-in" ? { mode: "built-in", procedure } : { mode: "custom", ...custom }
    try { const res = await generateSop(data); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const tabBtn = (v, label) => (
    <button type="button" onClick={() => setMode(v)} style={{ flex: 1, padding: "9px 0", border: "none", borderRadius: 2, background: mode === v ? gold : "#111113", color: mode === v ? "#0B0B0D" : "#666", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</button>
  )

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#0B0B0D", padding: 4, borderRadius: 3 }}>
        {tabBtn("built-in", "Built-In")}
        {tabBtn("custom", "Custom")}
      </div>
      {mode === "built-in" ? (
        <Field label="Select Procedure">
          <select style={inputStyle} value={procedure} onChange={e => setProcedure(e.target.value)}>
            {BUILT_IN_SOPS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </Field>
      ) : (
        <>
          <Field label="SOP Title">
            <input style={inputStyle} value={custom.title} onChange={e => setCustom(f => ({ ...f, title: e.target.value }))} placeholder="e.g. Saturday Closing Checklist" />
          </Field>
          <Field label="Description / Key Steps">
            <textarea style={{ ...inputStyle, height: 120, resize: "vertical" }} value={custom.description} onChange={e => setCustom(f => ({ ...f, description: e.target.value }))} placeholder="Describe the process and any key steps or requirements..." />
          </Field>
        </>
      )}
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate SOP →"}
      </button>
    </form>
  )
}
SopForm.apiFunc = generateSop
