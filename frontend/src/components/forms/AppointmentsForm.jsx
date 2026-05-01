import { useState } from "react"
import { generateAppointments } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function AppointmentsForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ touchpoint: "all", customer_name: "", service_type: "", channels: "all" })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await generateAppointments(form); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Touchpoint">
        <select style={inputStyle} value={form.touchpoint} onChange={set("touchpoint")}>
          <option value="all">All Touchpoints</option>
          <option value="booking_confirmation">Booking Confirmation</option>
          <option value="day_before_reminder">Day-Before Reminder</option>
          <option value="day_of_notification">Day-Of Notification</option>
          <option value="post_service_thankyou">Post-Service Thank-You</option>
          <option value="thirty_day_followup">30-Day Follow-Up</option>
          <option value="six_month_maintenance">6-Month Maintenance</option>
        </select>
      </Field>
      <Field label="Customer Name">
        <input style={inputStyle} value={form.customer_name} onChange={set("customer_name")} placeholder="e.g. John Doe (Optional)" />
      </Field>
      <Field label="Service Type">
        <input style={inputStyle} value={form.service_type} onChange={set("service_type")} placeholder="e.g. Oil change, Brake repair, AC service" />
      </Field>
      <Field label="Channels">
        <select style={inputStyle} value={form.channels} onChange={set("channels")}>
          <option value="all">All Channels</option>
          <option value="sms">SMS Only</option>
          <option value="email">Email Only</option>
          <option value="phone_script">Phone Script Only</option>
        </select>
      </Field>
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
AppointmentsForm.apiFunc = generateAppointments
