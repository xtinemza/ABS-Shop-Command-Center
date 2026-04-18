import { useState } from "react"
import { checkRecall, generateRecallNotify } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function RecallForm({ onSubmit, onSubmitStart, loading }) {
  const [mode, setMode] = useState("lookup")
  const [lookup, setLookup] = useState({ make: "", model: "", year: "", vin: "" })
  const [notify, setNotify] = useState({ customer: "", vehicle: "", recall_campaign: "", component: "", description: "", remedy: "", urgency: "high" })
  const setL = (k) => (e) => setLookup(f => ({ ...f, [k]: e.target.value }))
  const setN = (k) => (e) => setNotify(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try {
      const res = mode === "lookup" ? await checkRecall(lookup) : await generateRecallNotify(notify)
      onSubmit && onSubmit(res)
    } catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const tabBtn = (v, label) => (
    <button type="button" onClick={() => setMode(v)} style={{ flex: 1, padding: "9px 0", border: "none", borderRadius: 2, background: mode === v ? gold : "#111113", color: mode === v ? "#0B0B0D" : "#666", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</button>
  )

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#0B0B0D", padding: 4, borderRadius: 3 }}>
        {tabBtn("lookup", "Look Up")}
        {tabBtn("notify", "Generate Notice")}
      </div>
      {mode === "lookup" ? (
        <>
          <Field label="Make"><input style={inputStyle} value={lookup.make} onChange={setL("make")} placeholder="e.g. Toyota" /></Field>
          <Field label="Model"><input style={inputStyle} value={lookup.model} onChange={setL("model")} placeholder="e.g. Camry" /></Field>
          <Field label="Year"><input style={inputStyle} value={lookup.year} onChange={setL("year")} placeholder="e.g. 2019" /></Field>
          <Field label="VIN (optional)"><input style={inputStyle} value={lookup.vin} onChange={setL("vin")} placeholder="17-character VIN" /></Field>
        </>
      ) : (
        <>
          <Field label="Customer Name"><input style={inputStyle} value={notify.customer} onChange={setN("customer")} placeholder="e.g. Lisa Chen" /></Field>
          <Field label="Vehicle"><input style={inputStyle} value={notify.vehicle} onChange={setN("vehicle")} placeholder="e.g. 2019 Toyota Camry" /></Field>
          <Field label="Recall Campaign ID"><input style={inputStyle} value={notify.recall_campaign} onChange={setN("recall_campaign")} placeholder="e.g. NHTSA-21V-123" /></Field>
          <Field label="Affected Component"><input style={inputStyle} value={notify.component} onChange={setN("component")} placeholder="e.g. Fuel pump" /></Field>
          <Field label="Description"><textarea style={{ ...inputStyle, height: 80, resize: "vertical" }} value={notify.description} onChange={setN("description")} placeholder="Brief description of the recall issue" /></Field>
          <Field label="Remedy"><input style={inputStyle} value={notify.remedy} onChange={setN("remedy")} placeholder="e.g. Replace fuel pump at no cost" /></Field>
          <Field label="Urgency">
            <select style={inputStyle} value={notify.urgency} onChange={setN("urgency")}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="safety-critical">Safety Critical</option>
            </select>
          </Field>
        </>
      )}
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : mode === "lookup" ? "Look Up Recalls →" : "Generate Notice →"}
      </button>
    </form>
  )
}
RecallForm.apiFunc = checkRecall
