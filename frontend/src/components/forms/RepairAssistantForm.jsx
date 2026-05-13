import { useState } from "react"
import { repairAssistantDiagnose } from "../../api/client"

const gold = "#D4A017"
const inputStyle = {
  width: "100%", background: "#111113", border: "1px solid #222",
  borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13,
  fontFamily: "'Barlow', sans-serif", outline: "none", boxSizing: "border-box",
}
const labelStyle = {
  fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em",
  textTransform: "uppercase", marginBottom: 6, display: "block",
}
const rowStyle = { display: "flex", gap: 10 }

function Field({ label, style, children }) {
  return (
    <div style={{ marginBottom: 16, ...style }}>
      <label style={labelStyle}>{label}</label>
      {children}
    </div>
  )
}

const EXAMPLE_SYMPTOMS = [
  "Rough idle, shaking at startup, worse in cold weather",
  "Check engine light on, poor acceleration, slight fuel smell",
  "Shuddering between 40–55 mph, RPMs don't drop on highway",
  "Grinding noise from front left when braking",
  "Hard start in the morning, stalls at first stop sign",
]

export default function RepairAssistantForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({
    vehicle_year: "",
    vehicle_make: "",
    vehicle_model: "",
    mileage: "",
    symptoms: "",
    obd_codes: "",
  })

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const fillExample = () => {
    const symptom = EXAMPLE_SYMPTOMS[Math.floor(Math.random() * EXAMPLE_SYMPTOMS.length)]
    setForm(f => ({ ...f, symptoms: symptom }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.symptoms.trim() && !form.obd_codes.trim()) return
    onSubmitStart && onSubmitStart()
    try {
      const res = await repairAssistantDiagnose(form)
      onSubmit && onSubmit(res)
    } catch (err) {
      onSubmit && onSubmit({ error: err.message })
    }
  }

  const hasInput = form.symptoms.trim() || form.obd_codes.trim()

  return (
    <form onSubmit={handleSubmit}>
      {/* Vehicle info row */}
      <div style={rowStyle}>
        <Field label="Year" style={{ flex: "0 0 72px" }}>
          <input
            style={inputStyle} value={form.vehicle_year} onChange={set("vehicle_year")}
            placeholder="2019" maxLength={4}
          />
        </Field>
        <Field label="Make" style={{ flex: 1 }}>
          <input
            style={inputStyle} value={form.vehicle_make} onChange={set("vehicle_make")}
            placeholder="e.g. Chevrolet"
          />
        </Field>
        <Field label="Model" style={{ flex: 1 }}>
          <input
            style={inputStyle} value={form.vehicle_model} onChange={set("vehicle_model")}
            placeholder="e.g. Silverado"
          />
        </Field>
      </div>

      <Field label="Mileage (optional)">
        <input
          style={inputStyle} value={form.mileage} onChange={set("mileage")}
          placeholder="e.g. 87,500"
        />
      </Field>

      {/* OBD codes */}
      <Field label="OBD Trouble Codes (optional)">
        <input
          style={inputStyle} value={form.obd_codes} onChange={set("obd_codes")}
          placeholder="e.g. P0300, P0171, P0420  —  comma-separated"
        />
      </Field>

      {/* Symptoms */}
      <Field label="Reported Symptoms">
        <div style={{ position: "relative" }}>
          <textarea
            style={{ ...inputStyle, height: 110, resize: "vertical" }}
            value={form.symptoms}
            onChange={set("symptoms")}
            placeholder="Describe what the customer reported and what the technician observed…&#10;e.g. Rough idle at cold start, shaking between 45–55 mph, slight fuel smell near engine bay"
          />
          {!form.symptoms && (
            <button
              type="button"
              onClick={fillExample}
              style={{
                position: "absolute", bottom: 8, right: 8,
                padding: "3px 9px", borderRadius: 2, border: "1px solid #333",
                background: "#1A1A1E", color: "#666", fontSize: 10,
                fontWeight: 700, letterSpacing: "0.07em", cursor: "pointer",
                fontFamily: "'Barlow', sans-serif",
              }}
            >
              EXAMPLE
            </button>
          )}
        </div>
      </Field>

      {/* Info callout */}
      <div style={{
        marginBottom: 16, padding: "10px 14px", borderRadius: 3,
        background: "#0D1117", border: "1px solid #1A2030",
        display: "flex", gap: 10, alignItems: "flex-start",
      }}>
        <span style={{ fontSize: 14, lineHeight: 1, marginTop: 1 }}>🔬</span>
        <div>
          <p style={{ fontSize: 11, color: "#4A7AB5", fontWeight: 700, margin: "0 0 2px", letterSpacing: "0.06em" }}>
            DUAL OUTPUT — MECHANIC + ADVISOR
          </p>
          <p style={{ fontSize: 11, color: "#555", margin: 0, lineHeight: 1.5 }}>
            Results include a <strong style={{ color: "#888" }}>technical diagnosis</strong> for the tech (ranked causes, tests, parts) and a <strong style={{ color: "#888" }}>plain-language script</strong> for the service advisor to read to the customer.
          </p>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !hasInput}
        style={{
          width: "100%", marginTop: 4, padding: "14px 0",
          borderRadius: 3, border: `1px solid ${hasInput ? gold + "66" : "#222"}`,
          background: loading
            ? `${gold}88`
            : hasInput
              ? `linear-gradient(135deg, ${gold}, ${gold}CC)`
              : "#1A1A1E",
          color: hasInput ? "#0B0B0D" : "#444",
          fontSize: 13, fontWeight: 800, cursor: loading || !hasInput ? "default" : "pointer",
          fontFamily: "'Barlow Condensed', sans-serif",
          letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic",
          transition: "all 0.2s",
        }}
      >
        {loading ? "Diagnosing..." : "Run Diagnosis →"}
      </button>
    </form>
  )
}

RepairAssistantForm.apiFunc = repairAssistantDiagnose
