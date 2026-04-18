import { useState } from "react"
import { equipmentAction } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function EquipmentForm({ onSubmit, onSubmitStart, loading }) {
  const [form, setForm] = useState({ action: "list", equipment_id: "", name: "", type: "", purchase_date: "", last_service: "", next_service: "", notes: "" })
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try { const res = await equipmentAction(form); onSubmit && onSubmit(res) }
    catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const showDetails = ["add", "update", "log_maintenance"].includes(form.action)

  return (
    <form onSubmit={handleSubmit}>
      <Field label="Action">
        <select style={inputStyle} value={form.action} onChange={set("action")}>
          <option value="list">List All Equipment</option>
          <option value="add">Add Equipment</option>
          <option value="update">Update Equipment</option>
          <option value="log_maintenance">Log Maintenance</option>
          <option value="generate_report">Generate Report</option>
        </select>
      </Field>
      {showDetails && (
        <>
          {form.action !== "add" && <Field label="Equipment ID"><input style={inputStyle} value={form.equipment_id} onChange={set("equipment_id")} placeholder="e.g. LIFT-01" /></Field>}
          {form.action === "add" && <Field label="Equipment Name"><input style={inputStyle} value={form.name} onChange={set("name")} placeholder="e.g. Hunter 4-Post Lift" /></Field>}
          {form.action === "add" && <Field label="Equipment Type"><input style={inputStyle} value={form.type} onChange={set("type")} placeholder="e.g. Vehicle lift" /></Field>}
          {form.action === "add" && <Field label="Purchase Date"><input style={inputStyle} value={form.purchase_date} onChange={set("purchase_date")} placeholder="e.g. 2022-03-15" /></Field>}
          <Field label="Last Service Date"><input style={inputStyle} value={form.last_service} onChange={set("last_service")} placeholder="e.g. 2024-01-10" /></Field>
          <Field label="Next Service Date"><input style={inputStyle} value={form.next_service} onChange={set("next_service")} placeholder="e.g. 2024-07-10" /></Field>
          <Field label="Notes"><textarea style={{ ...inputStyle, height: 80, resize: "vertical" }} value={form.notes} onChange={set("notes")} placeholder="Any notes about this equipment or service" /></Field>
        </>
      )}
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Processing..." : "Run →"}
      </button>
    </form>
  )
}
EquipmentForm.apiFunc = equipmentAction
