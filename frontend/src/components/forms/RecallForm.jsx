import { useState } from "react"
import { checkRecall, generateRecallNotify, nhtsaRecallLookup } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function RecallForm({ onSubmit, onSubmitStart, loading }) {
  const [mode, setMode] = useState("lookup")
  const [lookup, setLookup] = useState({ make: "", model: "", year: "", vin: "" })
  const [notify, setNotify] = useState({ customer: "", vehicle: "", recall_campaign: "", component: "", description: "", remedy: "", urgency: "high" })
  const [liveRecalls, setLiveRecalls] = useState(null)
  const [liveLoading, setLiveLoading] = useState(false)
  const setL = (k) => (e) => setLookup(f => ({ ...f, [k]: e.target.value }))
  const setN = (k) => (e) => setNotify(f => ({ ...f, [k]: e.target.value }))

  // Pre-fill notify tab from a live recall result
  const prefillFromRecall = (recall, vehicleLabel) => {
    setNotify(n => ({
      ...n,
      vehicle: vehicleLabel,
      recall_campaign: recall.campaign,
      component: recall.component,
      description: recall.description,
      remedy: recall.remedy,
      urgency: "high",
    }))
    setMode("notify")
  }

  const handleLiveLookup = async () => {
    setLiveLoading(true)
    setLiveRecalls(null)
    try {
      const data = await nhtsaRecallLookup({ vin: lookup.vin, make: lookup.make, model: lookup.model, year: lookup.year })
      setLiveRecalls(data)
    } catch (e) {
      setLiveRecalls({ success: false, error: e.message, recalls: [] })
    } finally {
      setLiveLoading(false)
    }
  }

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
          <Field label="VIN (recommended — most accurate)">
            <input style={inputStyle} value={lookup.vin} onChange={setL("vin")} placeholder="17-character VIN" maxLength={17} />
          </Field>
          <p style={{ fontSize: 11, color: "#555", margin: "-8px 0 16px", textAlign: "center" }}>— or search by vehicle —</p>
          <div style={{ display: "flex", gap: 8 }}>
            <div style={{ flex: 2 }}><Field label="Make"><input style={inputStyle} value={lookup.make} onChange={setL("make")} placeholder="e.g. Toyota" /></Field></div>
            <div style={{ flex: 2 }}><Field label="Model"><input style={inputStyle} value={lookup.model} onChange={setL("model")} placeholder="e.g. Camry" /></Field></div>
            <div style={{ flex: 1 }}><Field label="Year"><input style={inputStyle} value={lookup.year} onChange={setL("year")} placeholder="2019" /></Field></div>
          </div>

          {/* Live NHTSA lookup button */}
          <button
            type="button"
            onClick={handleLiveLookup}
            disabled={liveLoading || (!lookup.vin && !(lookup.make && lookup.model && lookup.year))}
            style={{ width: "100%", padding: "11px 0", marginBottom: 16, borderRadius: 3, border: "1px solid #3a8a3a", background: liveLoading ? "#1a3a1a" : "#1a2a1a", color: "#4ADE80", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}
          >
            {liveLoading ? "⏳ Checking NHTSA Database..." : "🔍 Check Live NHTSA Recall Database"}
          </button>

          {/* Live results */}
          {liveRecalls && (
            <div style={{ marginBottom: 16, background: "#0B0B0D", border: "1px solid #222", borderRadius: 4, padding: "14px 16px" }}>
              {liveRecalls.success === false ? (
                <p style={{ color: "#E05252", fontSize: 12, margin: 0 }}>⚠ {liveRecalls.error}</p>
              ) : liveRecalls.recalls?.length === 0 ? (
                <p style={{ color: "#4ADE80", fontSize: 12, margin: 0 }}>✓ No open recalls found for this vehicle.</p>
              ) : (
                <>
                  <p style={{ color: "#E05252", fontSize: 12, fontWeight: 700, margin: "0 0 10px" }}>
                    ⚠ {liveRecalls.count} active recall{liveRecalls.count !== 1 ? "s" : ""} found
                  </p>
                  {liveRecalls.recalls.map((r, i) => (
                    <div key={i} style={{ borderTop: i > 0 ? "1px solid #1a1a1e" : "none", paddingTop: i > 0 ? 10 : 0, marginTop: i > 0 ? 10 : 0 }}>
                      <p style={{ fontSize: 12, color: "#CCC", fontWeight: 700, margin: "0 0 4px" }}>
                        Campaign: {r.campaign} — {r.component}
                      </p>
                      <p style={{ fontSize: 11, color: "#888", margin: "0 0 6px", lineHeight: 1.5 }}>{r.description}</p>
                      <button
                        type="button"
                        onClick={() => prefillFromRecall(r, `${lookup.year} ${lookup.make} ${lookup.model}`.trim() || "Vehicle")}
                        style={{ fontSize: 10, fontWeight: 700, color: gold, background: "none", border: `1px solid ${gold}55`, padding: "4px 10px", borderRadius: 3, cursor: "pointer", textTransform: "uppercase", letterSpacing: "0.08em" }}
                      >
                        Generate Notice →
                      </button>
                    </div>
                  ))}
                </>
              )}
            </div>
          )}
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
