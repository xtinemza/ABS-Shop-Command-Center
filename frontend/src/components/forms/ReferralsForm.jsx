import { useState } from "react"
import { trackReferral, generateRewards } from "../../api/client"

const gold = "#D4A017"
const inputStyle = { width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3, color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none" }
const labelStyle = { fontSize: 10, fontWeight: 700, color: "#555", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, display: "block" }
function Field({ label, children }) { return <div style={{ marginBottom: 16 }}><label style={labelStyle}>{label}</label>{children}</div> }

export default function ReferralsForm({ onSubmit, onSubmitStart, loading }) {
  const [tab, setTab] = useState("track")
  const [track, setTrack] = useState({ action: "add", referrer_name: "", referrer_phone: "", referred_name: "", referred_phone: "", service_date: "" })
  const [reward, setReward] = useState({ referrer_name: "", referrer_phone: "", reward_type: "discount", reward_value: "", referred_by: "" })
  const setT = (k) => (e) => setTrack(f => ({ ...f, [k]: e.target.value }))
  const setRw = (k) => (e) => setReward(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    onSubmitStart && onSubmitStart()
    try {
      const res = tab === "track" ? await trackReferral(track) : await generateRewards(reward)
      onSubmit && onSubmit(res)
    } catch (err) { onSubmit && onSubmit({ error: err.message }) }
  }

  const tabBtn = (v, label) => (
    <button type="button" onClick={() => setTab(v)} style={{ flex: 1, padding: "9px 0", border: "none", borderRadius: 2, background: tab === v ? gold : "#111113", color: tab === v ? "#0B0B0D" : "#666", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</button>
  )

  const showDetails = track.action === "add"

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "flex", gap: 4, marginBottom: 20, background: "#0B0B0D", padding: 4, borderRadius: 3 }}>
        {tabBtn("track", "Track Referral")}
        {tabBtn("reward", "Generate Reward")}
      </div>
      {tab === "track" ? (
        <>
          <Field label="Action">
            <select style={inputStyle} value={track.action} onChange={setT("action")}>
              <option value="add">Add Referral</option>
              <option value="list">List Referrals</option>
              <option value="report">Referral Report</option>
              <option value="check_rewards">Check Rewards Due</option>
            </select>
          </Field>
          {showDetails && (
            <>
              <Field label="Referrer Name"><input style={inputStyle} value={track.referrer_name} onChange={setT("referrer_name")} placeholder="e.g. Maria Garcia" /></Field>
              <Field label="Referrer Phone"><input style={inputStyle} value={track.referrer_phone} onChange={setT("referrer_phone")} placeholder="e.g. (303) 555-7890" /></Field>
              <Field label="Referred Customer Name"><input style={inputStyle} value={track.referred_name} onChange={setT("referred_name")} placeholder="e.g. Kevin Park" /></Field>
              <Field label="Referred Customer Phone"><input style={inputStyle} value={track.referred_phone} onChange={setT("referred_phone")} placeholder="e.g. (303) 555-1122" /></Field>
              <Field label="Service Date"><input style={inputStyle} type="date" value={track.service_date} onChange={setT("service_date")} /></Field>
            </>
          )}
        </>
      ) : (
        <>
          <Field label="Referrer Name"><input style={inputStyle} value={reward.referrer_name} onChange={setRw("referrer_name")} placeholder="e.g. Maria Garcia" /></Field>
          <Field label="Referrer Phone"><input style={inputStyle} value={reward.referrer_phone} onChange={setRw("referrer_phone")} placeholder="e.g. (303) 555-7890" /></Field>
          <Field label="Reward Type">
            <select style={inputStyle} value={reward.reward_type} onChange={setRw("reward_type")}>
              <option value="discount">Discount</option>
              <option value="free_service">Free Service</option>
              <option value="gift_card">Gift Card</option>
            </select>
          </Field>
          <Field label="Reward Value"><input style={inputStyle} value={reward.reward_value} onChange={setRw("reward_value")} placeholder="e.g. $25 off or Free oil change" /></Field>
          <Field label="Referred By (vehicle/service)"><input style={inputStyle} value={reward.referred_by} onChange={setRw("referred_by")} placeholder="e.g. Brake job on Kevin's Camry" /></Field>
        </>
      )}
      <button type="submit" disabled={loading} style={{ width: "100%", marginTop: 8, padding: "14px 0", borderRadius: 3, border: `1px solid ${gold}66`, background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`, color: "#0B0B0D", fontSize: 13, fontWeight: 800, cursor: loading ? "default" : "pointer", fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic" }}>
        {loading ? "Processing..." : "Run →"}
      </button>
    </form>
  )
}
ReferralsForm.apiFunc = trackReferral
