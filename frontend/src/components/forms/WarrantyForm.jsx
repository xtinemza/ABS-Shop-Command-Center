import { useState } from "react"
import { warrantyClaims, warrantyReport } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function WarrantyForm({ onSubmit, onSubmitStart, loading }) {
  const [tab, setTab] = useState("claims")
  const [claims, setClaims] = useState({ action: "list", claim_id: "", customer: "", vehicle: "", part: "", vendor: "", amount: "", status: "pending", notes: "" })
  const [report, setReport] = useState({ period: "month", status: "all" })
  const setC = (k) => (e) => setClaims(f => ({ ...f, [k]: e.target.value }))
  const setR = (k) => (e) => setReport(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try {
      const res = tab === "claims" ? await warrantyClaims(claims) : await warrantyReport(report)
      onSubmit && onSubmit(res)
    } catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const tabBtn = (v, label) => (
    <button type="button" onClick={() => setTab(v)} style={{ flex: 1, padding: "9px 0", border: "none", borderRadius: 2, background: tab === v ? gold : "#111113", color: tab === v ? "#0B0B0D" : "#666", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</button>
  )

  const showDetails = ["add", "update"].includes(claims.action)

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#0B0B0D", padding: 4, borderRadius: 3 }}>
        {tabBtn("claims", "Claims")}
        {tabBtn("report", "Report")}
      </div>
      {tab === "claims" ? (
        <>
          <Field label="Action">
            <select style={inputStyle} value={claims.action} onChange={setC("action")}>
              <option value="list">List Claims</option>
              <option value="add">Add Claim</option>
              <option value="update">Update Claim</option>
            </select>
          </Field>
          {claims.action === "update" && <Field label="Claim ID"><input style={inputStyle} value={claims.claim_id} onChange={setC("claim_id")} placeholder="e.g. CLM-2024-001" /></Field>}
          {showDetails && (
            <>
              <Field label="Customer"><input style={inputStyle} value={claims.customer} onChange={setC("customer")} placeholder="e.g. Tom Wilson" /></Field>
              <Field label="Vehicle"><input style={inputStyle} value={claims.vehicle} onChange={setC("vehicle")} placeholder="e.g. 2018 Chevy Silverado" /></Field>
              <Field label="Part / Service"><input style={inputStyle} value={claims.part} onChange={setC("part")} placeholder="e.g. Alternator replacement" /></Field>
              <Field label="Vendor"><input style={inputStyle} value={claims.vendor} onChange={setC("vendor")} placeholder="e.g. ACDelco" /></Field>
              <Field label="Claim Amount"><input style={inputStyle} type="number" step="0.01" value={claims.amount} onChange={setC("amount")} placeholder="e.g. 285.00" /></Field>
              <Field label="Status">
                <select style={inputStyle} value={claims.status} onChange={setC("status")}>
                  <option value="pending">Pending</option>
                  <option value="submitted">Submitted</option>
                  <option value="approved">Approved</option>
                  <option value="denied">Denied</option>
                  <option value="paid">Paid</option>
                </select>
              </Field>
              <Field label="Notes"><textarea style={{ ...inputStyle, height: 80, resize: "vertical" }} value={claims.notes} onChange={setC("notes")} placeholder="Additional notes about this claim" /></Field>
            </>
          )}
        </>
      ) : (
        <>
          <Field label="Period">
            <select style={inputStyle} value={report.period} onChange={setR("period")}>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
              <option value="all">All Time</option>
            </select>
          </Field>
          <Field label="Filter by Status">
            <select style={inputStyle} value={report.status} onChange={setR("status")}>
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="denied">Denied</option>
              <option value="paid">Paid</option>
            </select>
          </Field>
        </>
      )}
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Processing..." : "Run →"}
      </button>
    </form>
  )
}
WarrantyForm.apiFunc = warrantyClaims
