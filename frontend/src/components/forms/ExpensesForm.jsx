import { useState } from "react"
import { logExpense, expenseReport } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function ExpensesForm({ onSubmit, onSubmitStart, loading }) {
  const [tab, setTab] = useState("log")
  const [log, setLog] = useState({ action: "add", date: "", amount: "", vendor: "", description: "", category: "parts", payment_method: "card", receipt_ref: "" })
  const [report, setReport] = useState({ period: "month", month: "", year: new Date().getFullYear().toString(), format: "summary" })
  const setL = (k) => (e) => setLog(f => ({ ...f, [k]: e.target.value }))
  const setR = (k) => (e) => setReport(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try {
      const res = tab === "log" ? await logExpense(log) : await expenseReport(report)
      onSubmit && onSubmit(res)
    } catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const tabBtn = (v, label) => (
    <button type="button" onClick={() => setTab(v)} style={{ flex: 1, padding: "9px 0", border: "none", borderRadius: 2, background: tab === v ? gold : "#111113", color: tab === v ? "#0B0B0D" : "#666", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</button>
  )

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#0B0B0D", padding: 4, borderRadius: 3 }}>
        {tabBtn("log", "Log Expense")}
        {tabBtn("report", "Report")}
      </div>
      {tab === "log" ? (
        <>
          <Field label="Action">
            <select style={inputStyle} value={log.action} onChange={setL("action")}>
              <option value="add">Add Expense</option>
              <option value="list">List Expenses</option>
            </select>
          </Field>
          {log.action === "add" && (
            <>
              <Field label="Date"><input style={inputStyle} type="date" value={log.date} onChange={setL("date")} /></Field>
              <Field label="Amount ($)"><input style={inputStyle} type="number" step="0.01" value={log.amount} onChange={setL("amount")} placeholder="e.g. 142.50" /></Field>
              <Field label="Vendor"><input style={inputStyle} value={log.vendor} onChange={setL("vendor")} placeholder="e.g. NAPA Auto Parts" /></Field>
              <Field label="Description"><input style={inputStyle} value={log.description} onChange={setL("description")} placeholder="e.g. Brake parts restock" /></Field>
              <Field label="Category">
                <select style={inputStyle} value={log.category} onChange={setL("category")}>
                  <option value="parts">Parts</option>
                  <option value="labor">Labor</option>
                  <option value="rent">Rent / Lease</option>
                  <option value="utilities">Utilities</option>
                  <option value="insurance">Insurance</option>
                  <option value="marketing">Marketing</option>
                  <option value="tools">Tools / Equipment</option>
                  <option value="training">Training</option>
                  <option value="other">Other</option>
                </select>
              </Field>
              <Field label="Payment Method">
                <select style={inputStyle} value={log.payment_method} onChange={setL("payment_method")}>
                  <option value="card">Card</option>
                  <option value="check">Check</option>
                  <option value="cash">Cash</option>
                  <option value="ach">ACH / Bank Transfer</option>
                </select>
              </Field>
              <Field label="Receipt Reference"><input style={inputStyle} value={log.receipt_ref} onChange={setL("receipt_ref")} placeholder="e.g. RCP-2024-0312" /></Field>
            </>
          )}
        </>
      ) : (
        <>
          <Field label="Period">
            <select style={inputStyle} value={report.period} onChange={setR("period")}>
              <option value="month">Monthly</option>
              <option value="quarter">Quarterly</option>
              <option value="year">Annual</option>
            </select>
          </Field>
          {report.period === "month" && <Field label="Month"><input style={inputStyle} value={report.month} onChange={setR("month")} placeholder="e.g. March" /></Field>}
          <Field label="Year"><input style={inputStyle} value={report.year} onChange={setR("year")} placeholder="e.g. 2024" /></Field>
          <Field label="Format">
            <select style={inputStyle} value={report.format} onChange={setR("format")}>
              <option value="summary">Summary</option>
              <option value="detailed">Detailed</option>
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
ExpensesForm.apiFunc = logExpense
