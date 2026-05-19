import { useState } from "react"
import { generateAppointments } from "../../api/client"
import ServiceSelect from "../ServiceSelect"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

const CHANNELS = [
  { key: "sms",          label: "SMS" },
  { key: "email",        label: "Email" },
  { key: "phone_script", label: "Phone Script" },
]

export default function AppointmentsForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ touchpoint: "all", customer_name: "", service_type: "" })
  const [channels, setChannels] = useState({ sms: true, email: true, phone_script: true })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const toggleChannel = (key) => {
    setChannels(c => {
      const next = { ...c, [key]: !c[key] }
      const anyOn = Object.values(next).some(Boolean)
      return anyOn ? next : c // prevent all-off
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    const selected = Object.entries(channels).filter(([, v]) => v).map(([k]) => k).join(",")
    try {
      const res = await generateAppointments({ ...form, channels: selected })
      onSubmit && onSubmit(res)
    } catch (err) {
      onSubmit && onSubmit({ error: err.message })
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Touchpoint">
        <select style={inputStyle} value={form.touchpoint} onChange={set("touchpoint")}>
          <option value="all">All Touchpoints</option>
          <option value="booking_confirmation">Booking Confirmation</option>
          <option value="day_before_reminder">Day-Before Reminder</option>
          <option value="morning_reminder">Morning-Of Reminder</option>
          <option value="day_after_thank_you">Post-Visit Thank-You</option>
          <option value="review_request">Review Request</option>
          <option value="thirty_day_followup">30-Day Follow-Up</option>
          <option value="six_month_maintenance">6-Month Maintenance</option>
        </select>
      </Field>

      <Field label="Customer Name">
        <input style={inputStyle} value={form.customer_name} onChange={set("customer_name")} placeholder="e.g. John Doe (Optional)" />
      </Field>

      <Field label="Service Type">
        <ServiceSelect
          value={form.service_type}
          onChange={(val) => setForm(f => ({ ...f, service_type: val }))}
          placeholder="Select or add a service..."
        />
      </Field>

      <Field label="Channels">
        <div style={{ display: "flex", gap: 8 }}>
          {CHANNELS.map(({ key, label }) => {
            const on = channels[key]
            return (
              <button
                key={key}
                type="button"
                onClick={() => toggleChannel(key)}
                style={{
                  flex: 1, padding: "10px 0", borderRadius: 3,
                  border: `1px solid ${on ? gold + "88" : "#222"}`,
                  background: on ? `${gold}18` : "#111113",
                  color: on ? gold : "#444",
                  fontSize: 11, fontWeight: 800, cursor: "pointer",
                  fontFamily: "'Barlow', sans-serif", letterSpacing: "0.1em",
                  textTransform: "uppercase", transition: "all 0.15s",
                }}
              >
                {label}
              </button>
            )
          })}
        </div>
      </Field>

      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
AppointmentsForm.apiFunc = generateAppointments
