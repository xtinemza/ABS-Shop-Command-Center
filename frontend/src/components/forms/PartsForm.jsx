import { useState } from "react"
import { partsInventory, generatePO } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function PartsForm({ onSubmit, onSubmitStart, loading }) {
  const [tab, setTab] = useState("inventory")
  const [inv, setInv] = useState({ action: "list", part_number: "", part_name: "", category: "", quantity: "", reorder_point: "", preferred_vendor: "", cost: "" })
  const [po, setPo] = useState({ vendor: "", items: "", notes: "" })
  const setI = (k) => (e) => setInv(f => ({ ...f, [k]: e.target.value }))
  const setP = (k) => (e) => setPo(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try {
      const res = tab === "inventory" ? await partsInventory(inv) : await generatePO(po)
      onSubmit && onSubmit(res)
    } catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const tabBtn = (v, label) => (
    <button type="button" onClick={() => setTab(v)} style={{ flex: 1, padding: "9px 0", border: "none", borderRadius: 2, background: tab === v ? gold : "#111113", color: tab === v ? "#0B0B0D" : "#666", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</button>
  )

  const showDetails = ["add", "update"].includes(inv.action)

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#0B0B0D", padding: 4, borderRadius: 3 }}>
        {tabBtn("inventory", "Inventory")}
        {tabBtn("po", "Purchase Order")}
      </div>
      {tab === "inventory" ? (
        <>
          <Field label="Action">
            <select style={inputStyle} value={inv.action} onChange={setI("action")}>
              <option value="list">List Inventory</option>
              <option value="add">Add Part</option>
              <option value="update">Update Part</option>
              <option value="reorder_check">Reorder Check</option>
              <option value="report">Generate Report</option>
            </select>
          </Field>
          {showDetails && (
            <>
              <Field label="Part Number"><input style={inputStyle} value={inv.part_number} onChange={setI("part_number")} placeholder="e.g. BP-4421-F" /></Field>
              <Field label="Part Name"><input style={inputStyle} value={inv.part_name} onChange={setI("part_name")} placeholder="e.g. Front Brake Pads" /></Field>
              <Field label="Category"><input style={inputStyle} value={inv.category} onChange={setI("category")} placeholder="e.g. Brakes" /></Field>
              <Field label="Quantity"><input style={inputStyle} type="number" value={inv.quantity} onChange={setI("quantity")} placeholder="e.g. 12" /></Field>
              <Field label="Reorder Point"><input style={inputStyle} type="number" value={inv.reorder_point} onChange={setI("reorder_point")} placeholder="e.g. 4" /></Field>
              <Field label="Preferred Vendor"><input style={inputStyle} value={inv.preferred_vendor} onChange={setI("preferred_vendor")} placeholder="e.g. NAPA Auto Parts" /></Field>
              <Field label="Unit Cost"><input style={inputStyle} type="number" step="0.01" value={inv.cost} onChange={setI("cost")} placeholder="e.g. 24.99" /></Field>
            </>
          )}
        </>
      ) : (
        <>
          <Field label="Vendor"><input style={inputStyle} value={po.vendor} onChange={setP("vendor")} placeholder="e.g. NAPA Auto Parts" /></Field>
          <Field label="Items (JSON array)">
            <textarea style={{ ...inputStyle, height: 120, resize: "vertical" }} value={po.items} onChange={setP("items")} placeholder={'[{"part_number": "BP-4421-F", "name": "Front Brake Pads", "qty": 8, "unit_cost": 24.99}]'} />
          </Field>
          <Field label="Notes">
            <textarea style={{ ...inputStyle, height: 60, resize: "vertical" }} value={po.notes} onChange={setP("notes")} placeholder="Any special instructions for this order" />
          </Field>
        </>
      )}
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Processing..." : "Run →"}
      </button>
    </form>
  )
}
PartsForm.apiFunc = partsInventory
