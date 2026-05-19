import { useState } from "react"
import { generateEstimate } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none", boxSizing: "border-box" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
const emptyItem = () => ({ part: "", part_cost: "", labor_hours: "", labor_cost: "", urgency: "medium" })

function Field({ label, children }) {
  return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div>
}

export default function EstimatesForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ customer: "", vehicle: "" })
  const [items, setItems] = useState([emptyItem()])
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const setItem = (i, k) => (e) => {
    setItems(prev => prev.map((item, idx) => idx === i ? { ...item, [k]: e.target.value } : item))
  }

  const addItem = () => setItems(prev => [...prev, emptyItem()])
  const removeItem = (i) => setItems(prev => prev.length > 1 ? prev.filter((_, idx) => idx !== i) : prev)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const validItems = items.filter(it => it.part.trim())
    const payload = {
      ...form,
      items: JSON.stringify(validItems.map(it => ({
        part: it.part,
        part_cost: parseFloat(it.part_cost) || 0,
        labor_hours: parseFloat(it.labor_hours) || 0,
        labor_cost: parseFloat(it.labor_cost) || 0,
        urgency: it.urgency,
      })))
    }
    onSubmitStart && onSubmitStart()
    try { const res = await generateEstimate(payload); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const smallInput = (val, onChange, placeholder, type = "text") => (
    <input type={type} style={{ ...inputStyle, padding: "8px 10px", fontSize: 12 }} value={val} onChange={onChange} placeholder={placeholder} />
  )

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Customer Name">
        <input style={inputStyle} value={form.customer} onChange={set("customer")} placeholder="e.g. James Rivera" />
      </Field>
      <Field label="Vehicle">
        <input style={inputStyle} value={form.vehicle} onChange={set("vehicle")} placeholder="e.g. 2017 Honda Accord EX" />
      </Field>

      <div style={{ marginBottom: 16 }}>
        <label style={labelStyle}>Estimate Line Items</label>
        {items.map((item, i) => (
          <div key={i} style={{ background: "#111113", border: "1px solid #1A1A1E", borderRadius: 3, padding: "12px", marginBottom: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <span style={{ fontSize: 10, fontWeight: 700, color: "#444", letterSpacing: "0.1em", textTransform: "uppercase" }}>Item {i + 1}</span>
              {items.length > 1 && (
                <button type="button" onClick={() => removeItem(i)} style={{ background: "none", border: "none", color: "#555", cursor: "pointer", fontSize: 16, padding: 0, lineHeight: 1 }}>✕</button>
              )}
            </div>
            <div style={{ marginBottom: 8 }}>
              {smallInput(item.part, setItem(i, "part"), "Part / service name (e.g. Front brake pads)")}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 8 }}>
              <div>
                <label style={{ ...labelStyle, marginBottom: 4 }}>Part Cost ($)</label>
                {smallInput(item.part_cost, setItem(i, "part_cost"), "45", "number")}
              </div>
              <div>
                <label style={{ ...labelStyle, marginBottom: 4 }}>Labor Hrs</label>
                {smallInput(item.labor_hours, setItem(i, "labor_hours"), "1.5", "number")}
              </div>
              <div>
                <label style={{ ...labelStyle, marginBottom: 4 }}>Labor Cost ($)</label>
                {smallInput(item.labor_cost, setItem(i, "labor_cost"), "120", "number")}
              </div>
              <div>
                <label style={{ ...labelStyle, marginBottom: 4 }}>Urgency</label>
                <select value={item.urgency} onChange={setItem(i, "urgency")} style={{ ...inputStyle, padding: "8px 10px", fontSize: 12 }}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>
          </div>
        ))}
        <button type="button" onClick={addItem} style={{ width: "100%", padding: "8px", borderRadius: 3, border: `1px dashed #333`, background: "none", color: "#555", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          + Add Line Item
        </button>
      </div>

      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Generating..." : "Generate →"}
      </button>
    </form>
  )
}
EstimatesForm.apiFunc = generateEstimate
