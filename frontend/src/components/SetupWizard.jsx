import { useState } from "react"
import { runSetup } from "../api/client"

const gold = "#D4A017"

const inputStyle = {
  width: "100%",
  background: "#111113",
  border: "1px solid #222",
  borderRadius: 3,
  color: "#CCC",
  padding: "10px 12px",
  fontSize: 13,
  fontFamily: "'Barlow', sans-serif",
  outline: "none",
}

const labelStyle = {
  fontSize: 10, fontWeight: 700, color: "#555",
  letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6,
  display: "block",
}

function Field({ label, required, children }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={labelStyle}>
        {label}{required && <span style={{ color: gold, marginLeft: 3 }}>*</span>}
      </label>
      {children}
    </div>
  )
}

export default function SetupWizard({ onComplete }) {
  const [form, setForm] = useState({
    shop_name: "",
    owner_name: "",
    phone: "",
    street: "",
    city: "",
    state: "",
    zip: "",
    hours: "",
    services: "",
    business_type: "",
    website: "",
    tagline: "",
    tone: "Professional and friendly",
    google_review_link: "",
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.shop_name || !form.owner_name || !form.phone || !form.street || !form.city || !form.state || !form.zip) {
      setError("Please fill in all required fields.")
      return
    }
    if (!/^\d{5}$/.test(form.zip)) {
      setError("Please enter a valid 5-digit US Zip Code.")
      return
    }
    setLoading(true)
    setError("")
    try {
      await runSetup(form)
      onComplete()
    } catch (err) {
      setError(err.message || "Setup failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: "100vh", background: "#0B0B0D",
      display: "flex", alignItems: "center", justifyContent: "center",
      padding: 24,
      fontFamily: "'Barlow', sans-serif",
    }}>
      <div style={{
        width: "100%", maxWidth: 540,
        background: "#0E0E10",
        border: "1px solid #1A1A1E",
        borderRadius: 4,
        overflow: "hidden",
      }}>
        {/* Gold accent bar */}
        <div style={{ height: 3, background: `linear-gradient(90deg, ${gold}, #F5C542, ${gold})` }} />

        <div style={{ padding: "32px 36px 36px" }}>
          {/* Header */}
          <div style={{ marginBottom: 28 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10 }}>
              <span style={{ fontSize: 28 }}>⚙️</span>
              <div>
                <h1 style={{
                  fontFamily: "'Barlow Condensed', sans-serif",
                  fontWeight: 800, fontStyle: "italic",
                  fontSize: 24, color: "#F2F2F4",
                  textTransform: "uppercase", letterSpacing: "0.03em",
                  lineHeight: 1, margin: 0,
                }}>Shop Command Center</h1>
                <p style={{ fontSize: 11, color: gold, fontWeight: 700, letterSpacing: "0.14em", textTransform: "uppercase", margin: "4px 0 0" }}>
                  First-Time Setup
                </p>
              </div>
            </div>
            <p style={{ fontSize: 13, color: "#666", lineHeight: 1.6, margin: 0 }}>
              Enter your shop details once — every module will use them automatically.
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
              <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
              <span style={{ fontSize: 9, fontWeight: 800, color: "#555", letterSpacing: "0.14em", textTransform: "uppercase" }}>Shop Info</span>
            </div>

            <Field label="Shop Name" required>
              <input style={inputStyle} value={form.shop_name} onChange={set("shop_name")} placeholder="e.g. Precision Auto Care" />
            </Field>
            <Field label="Owner / Manager Name" required>
              <input style={inputStyle} value={form.owner_name} onChange={set("owner_name")} placeholder="e.g. Mike Johnson" />
            </Field>
            <Field label="Phone Number" required>
              <input style={inputStyle} value={form.phone} onChange={set("phone")} placeholder="e.g. (303) 555-1234" />
            </Field>
            <Field label="Street Address" required>
              <input style={inputStyle} value={form.street} onChange={set("street")} placeholder="e.g. 1234 Main St" />
            </Field>
            
            <div style={{ display: "flex", gap: 12 }}>
              <div style={{ flex: 2 }}>
                <Field label="City" required>
                  <input style={inputStyle} value={form.city} onChange={set("city")} placeholder="e.g. Denver" />
                </Field>
              </div>
              <div style={{ flex: 1 }}>
                <Field label="State" required>
                  <select style={inputStyle} value={form.state} onChange={set("state")}>
                    <option value="">Select...</option>
                    {["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"].map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </Field>
              </div>
              <div style={{ flex: 1 }}>
                <Field label="Zip Code" required>
                  <input style={inputStyle} value={form.zip} onChange={set("zip")} placeholder="e.g. 80201" maxLength={5} />
                </Field>
              </div>
            </div>

            <div style={{ marginTop: 8, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
              <span style={{ fontSize: 9, fontWeight: 800, color: "#555", letterSpacing: "0.14em", textTransform: "uppercase" }}>Operations</span>
            </div>

            <Field label="Hours">
              <input style={inputStyle} value={form.hours} onChange={set("hours")} placeholder="e.g. Mon-Fri 8am-6pm, Sat 8am-2pm" />
            </Field>
            <Field label="Services Offered (comma-separated)">
              <textarea
                style={{ ...inputStyle, height: 72, resize: "vertical" }}
                value={form.services}
                onChange={set("services")}
                placeholder="e.g. Oil changes, Brake repair, Tire rotation, AC service"
              />
            </Field>
            <Field label="Business Type">
              <input style={inputStyle} value={form.business_type} onChange={set("business_type")} placeholder="e.g. Independent auto repair shop" />
            </Field>

            <div style={{ marginTop: 8, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
              <span style={{ fontSize: 9, fontWeight: 800, color: "#555", letterSpacing: "0.14em", textTransform: "uppercase" }}>Branding</span>
            </div>

            <Field label="Website">
              <input style={inputStyle} value={form.website} onChange={set("website")} placeholder="e.g. https://precisionautocare.com" />
            </Field>
            <Field label="Tagline">
              <input style={inputStyle} value={form.tagline} onChange={set("tagline")} placeholder="e.g. Honest Service. Every Time." />
            </Field>
            <Field label="Communication Tone">
              <select style={inputStyle} value={form.tone} onChange={set("tone")}>
                <option>Professional</option>
                <option>Friendly</option>
                <option>Professional and friendly</option>
                <option>Casual</option>
              </select>
            </Field>
            <Field label="Google Review Link (optional)">
              <input style={inputStyle} value={form.google_review_link} onChange={set("google_review_link")} placeholder="https://g.page/r/..." />
            </Field>

            {error && (
              <p style={{ fontSize: 12, color: "#E05252", marginBottom: 16, lineHeight: 1.5 }}>{error}</p>
            )}

            <button type="submit" disabled={loading} style={{
              width: "100%", marginTop: 8,
              padding: "16px 0", borderRadius: 3,
              border: `1px solid ${gold}66`,
              background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`,
              color: "#0B0B0D", fontSize: 13, fontWeight: 800,
              cursor: loading ? "default" : "pointer",
              fontFamily: "'Barlow Condensed', sans-serif",
              letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic",
            }}>
              {loading ? "Setting Up..." : "Complete Setup →"}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
