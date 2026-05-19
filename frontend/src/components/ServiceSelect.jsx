import { useState, useEffect } from "react"
import { getProfile, saveProfile } from "../api/client"

const gold = "#D4A017"

const DEFAULT_SERVICES = [
  "Oil Change",
  "Brake Service",
  "Tire Rotation",
  "Wheel Alignment",
  "Battery Replacement",
  "Air Filter Replacement",
  "Transmission Service",
  "Coolant Flush",
  "Spark Plug Replacement",
  "Timing Belt / Timing Chain",
  "AC Service",
  "Engine Diagnostic",
  "Suspension Service",
  "Exhaust Service",
  "Fuel System Service",
  "Multi-Point Inspection",
]

const inputStyle = {
  width: "100%", background: "#111113", border: "1px solid #222",
  borderRadius: 3, color: "#CCC", padding: "10px 12px",
  fontSize: 13, fontFamily: "'Barlow', sans-serif", outline: "none",
}

export default function ServiceSelect({ value, onChange, placeholder = "Select a service..." }) {
  const [saved, setSaved]     = useState([])
  const [adding, setAdding]   = useState(false)
  const [newSvc, setNewSvc]   = useState("")
  const [saving, setSaving]   = useState(false)

  useEffect(() => {
    getProfile()
      .then(res => setSaved(res.profile?.quick_services || []))
      .catch(() => {})
  }, [])

  const handleChange = (e) => {
    if (e.target.value === "__add__") {
      setAdding(true)
    } else {
      onChange(e.target.value)
    }
  }

  const handleSave = async () => {
    const name = newSvc.trim()
    if (!name) return
    setSaving(true)
    const updated = [...saved.filter(s => s !== name), name]
    try {
      await saveProfile({ quick_services: updated })
      setSaved(updated)
      onChange(name)
    } catch {
      onChange(name) // still set even if save fails
    } finally {
      setSaving(false)
      setNewSvc("")
      setAdding(false)
    }
  }

  const handleRemove = async (svc) => {
    const updated = saved.filter(s => s !== svc)
    setSaved(updated)
    await saveProfile({ quick_services: updated }).catch(() => {})
    if (value === svc) onChange("")
  }

  const customOnly = saved.filter(s => !DEFAULT_SERVICES.includes(s))

  if (adding) {
    return (
      <div style={{ display: "flex", gap: 6 }}>
        <input
          autoFocus
          style={{ ...inputStyle, flex: 1 }}
          value={newSvc}
          onChange={e => setNewSvc(e.target.value)}
          placeholder="e.g. CV Axle Replacement"
          onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); handleSave() } if (e.key === "Escape") setAdding(false) }}
        />
        <button
          type="button"
          onClick={handleSave}
          disabled={saving || !newSvc.trim()}
          style={{
            padding: "0 14px", borderRadius: 3, border: `1px solid ${gold}66`,
            background: `linear-gradient(135deg, ${gold}, ${gold}CC)`,
            color: "#0B0B0D", fontSize: 11, fontWeight: 800, cursor: "pointer",
            fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em",
            textTransform: "uppercase", whiteSpace: "nowrap",
          }}
        >
          {saving ? "..." : "Save"}
        </button>
        <button
          type="button"
          onClick={() => { setAdding(false); setNewSvc("") }}
          style={{
            padding: "0 12px", borderRadius: 3, border: "1px solid #333",
            background: "transparent", color: "#666", fontSize: 11,
            fontWeight: 700, cursor: "pointer", fontFamily: "'Barlow', sans-serif",
            letterSpacing: "0.08em", textTransform: "uppercase",
          }}
        >
          ✕
        </button>
      </div>
    )
  }

  return (
    <div>
      <select style={inputStyle} value={value || ""} onChange={handleChange}>
        <option value="">{placeholder}</option>

        {customOnly.length > 0 && (
          <optgroup label="Your Services">
            {customOnly.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </optgroup>
        )}

        <optgroup label="Common Services">
          {DEFAULT_SERVICES.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </optgroup>

        <option value="__add__">+ Add custom service...</option>
      </select>

      {customOnly.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
          {customOnly.map(s => (
            <span key={s} style={{
              display: "inline-flex", alignItems: "center", gap: 5,
              padding: "3px 8px", borderRadius: 3,
              background: value === s ? `${gold}22` : "#151518",
              border: `1px solid ${value === s ? gold + "55" : "#1C1C20"}`,
              fontSize: 10, color: value === s ? gold : "#555",
              fontWeight: 700, letterSpacing: "0.06em",
            }}>
              {s}
              <button
                type="button"
                onClick={() => handleRemove(s)}
                style={{
                  background: "none", border: "none", color: "#444",
                  cursor: "pointer", padding: 0, fontSize: 10, lineHeight: 1,
                }}
              >
                ✕
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
