import { useState } from "react"
import { generateWelcomeKit } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function WelcomeKitForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ component: "all", discount: "10% off your next service", referral_offer: "$25 off for you and your referral" })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await generateWelcomeKit(form); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Component">
        <select style={inputStyle} value={form.component} onChange={set("component")}>
          <option value="all">Full Welcome Kit (All)</option>
          <option value="thank_you_letter">Thank-You Letter</option>
          <option value="shop_overview">Shop Overview</option>
          <option value="maintenance_guide">Maintenance Guide</option>
          <option value="new_customer_offer">New Customer Offer</option>
          <option value="referral_card">Referral Card</option>
          <option value="welcome_email">Welcome Email</option>
        </select>
      </Field>
      <Field label="New Customer Discount">
        <input style={inputStyle} value={form.discount} onChange={set("discount")} placeholder="e.g. 10% off your next service" />
      </Field>
      <Field label="Referral Offer">
        <input style={inputStyle} value={form.referral_offer} onChange={set("referral_offer")} placeholder="e.g. $25 off for you and your referral" />
      </Field>
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
WelcomeKitForm.apiFunc = generateWelcomeKit
