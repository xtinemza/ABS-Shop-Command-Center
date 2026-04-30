import { useState, useEffect } from "react"
import { getSops, saveSops } from "../api/client"

const gold = "#D4A017"

const inputStyle = {
  width: "100%", background: "#111113", border: "1px solid #222", borderRadius: 3,
  color: "#CCC", padding: "10px 12px", fontSize: 13, fontFamily: "'Barlow', sans-serif",
  outline: "none"
}

export default function SopEditor({ onClose }) {
  const [sops, setSops] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  // For adding a new SOP
  const [newKey, setNewKey] = useState("")
  const [newTitle, setNewTitle] = useState("")
  const [newSteps, setNewSteps] = useState("")

  useEffect(() => {
    async function load() {
      try {
        const data = await getSops()
        setSops(data || {})
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    setSuccess(false)
    try {
      await saveSops(sops)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = (key) => {
    const next = { ...sops }
    delete next[key]
    setSops(next)
  }

  const handleUpdate = (key, field, value) => {
    const next = { ...sops }
    next[key] = { ...next[key], [field]: value }
    setSops(next)
  }

  const handleStepsUpdate = (key, text) => {
    const next = { ...sops }
    next[key] = { ...next[key], steps: text.split('\n').filter(s => s.trim()) }
    setSops(next)
  }

  const handleAdd = () => {
    if (!newKey || !newTitle) return
    const key = newKey.toLowerCase().replace(/[^a-z0-9_]/g, '_')
    if (sops[key]) {
      setError("An SOP with a similar key already exists.")
      return
    }
    setSops({
      ...sops,
      [key]: {
        title: newTitle,
        category: "Custom",
        steps: newSteps.split('\n').filter(s => s.trim())
      }
    })
    setNewKey("")
    setNewTitle("")
    setNewSteps("")
  }

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 1000,
      background: "rgba(11, 11, 13, 0.9)", backdropFilter: "blur(4px)",
      display: "flex", justifyContent: "flex-end",
      animation: "drawerIn 0.3s ease"
    }}>
      <div style={{
        width: 600, background: "#0E0E10", height: "100%",
        borderLeft: `2px solid ${gold}`, display: "flex", flexDirection: "column"
      }}>
        {/* Header */}
        <div style={{ padding: "24px 32px", borderBottom: "1px solid #1A1A1E", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h2 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: 24, color: "#F2F2F4", margin: 0, textTransform: "uppercase", fontStyle: "italic", fontWeight: 800 }}>
              ⚙️ Edit Shop Operations (SOPs)
            </h2>
            <p style={{ margin: "4px 0 0", color: "#666", fontSize: 13 }}>
              Manage your custom standard operating procedures.
            </p>
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", color: "#888", fontSize: 24, cursor: "pointer" }}>×</button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: "auto", padding: 32 }}>
          {loading ? (
            <div style={{ color: gold }}>Loading...</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
              {Object.keys(sops).length === 0 && (
                <div style={{ padding: 20, background: "#111", border: "1px dashed #333", borderRadius: 4, color: "#888", textAlign: "center" }}>
                  No SOPs found. Add your first custom procedure below!
                </div>
              )}

              {Object.entries(sops).map(([key, data]) => (
                <div key={key} style={{ background: "#111113", border: "1px solid #1A1A1E", borderRadius: 4, padding: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                    <div style={{ color: "#555", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em" }}>
                      Key: {key}
                    </div>
                    <button onClick={() => handleDelete(key)} style={{ background: "transparent", border: "none", color: "#E05252", cursor: "pointer", fontSize: 12, fontWeight: 700 }}>
                      DELETE
                    </button>
                  </div>
                  
                  <div style={{ marginBottom: 12 }}>
                    <label style={{ display: "block", fontSize: 11, color: "#888", marginBottom: 4 }}>Title</label>
                    <input 
                      style={inputStyle} 
                      value={data.title || ""} 
                      onChange={(e) => handleUpdate(key, "title", e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <label style={{ display: "block", fontSize: 11, color: "#888", marginBottom: 4 }}>Steps (one per line)</label>
                    <textarea 
                      style={{ ...inputStyle, height: 120, resize: "vertical" }}
                      value={(data.steps || []).join('\n')}
                      onChange={(e) => handleStepsUpdate(key, e.target.value)}
                    />
                  </div>
                </div>
              ))}

              {/* Add New Section */}
              <div style={{ marginTop: 24, padding: 20, background: "#0B0B0D", border: `1px solid ${gold}44`, borderRadius: 4 }}>
                <h3 style={{ margin: "0 0 16px", color: gold, fontSize: 14, textTransform: "uppercase", letterSpacing: "0.1em" }}>+ Add New SOP</h3>
                <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
                  <div style={{ flex: 1 }}>
                    <input style={inputStyle} placeholder="Key (e.g. check_in)" value={newKey} onChange={e => setNewKey(e.target.value)} />
                  </div>
                  <div style={{ flex: 2 }}>
                    <input style={inputStyle} placeholder="Title (e.g. Customer Check-In)" value={newTitle} onChange={e => setNewTitle(e.target.value)} />
                  </div>
                </div>
                <textarea 
                  style={{ ...inputStyle, height: 80, marginBottom: 12 }} 
                  placeholder="Steps (one per line)..."
                  value={newSteps}
                  onChange={e => setNewSteps(e.target.value)}
                />
                <button onClick={handleAdd} style={{ width: "100%", padding: "10px", background: "#111", border: "1px solid #333", color: "#CCC", cursor: "pointer", borderRadius: 3, fontWeight: 700, textTransform: "uppercase", fontSize: 11 }}>
                  Add Procedure
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ padding: 24, borderTop: "1px solid #1A1A1E", background: "#0D0D0F", display: "flex", flexDirection: "column", gap: 12 }}>
          {error && <div style={{ color: "#E05252", fontSize: 13, textAlign: "center" }}>{error}</div>}
          {success && <div style={{ color: "#4CAF50", fontSize: 13, textAlign: "center" }}>Saved successfully!</div>}
          <button 
            onClick={handleSave} 
            disabled={saving}
            style={{
              width: "100%", padding: "16px 0", borderRadius: 3,
              border: `1px solid ${gold}66`,
              background: saving ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`,
              color: "#0B0B0D", fontSize: 14, fontWeight: 800, cursor: saving ? "default" : "pointer",
              fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em", textTransform: "uppercase"
            }}
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  )
}
