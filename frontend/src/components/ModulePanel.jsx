import { useState } from "react"
import OutputPanel from "./OutputPanel"

const gold = "#D4A017"

export default function ModulePanel({ mod, onBack }) {
  const [output, setOutput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [files, setFiles] = useState([])
  const [content, setContent] = useState(null)

  const FormComponent = mod.formComponent

  const handleFormResult = (res) => {
    if (res && res.error) {
      setError(res.error)
      setOutput("")
    } else {
      const text = res
        ? (res.output || res.result || res.message || JSON.stringify(res, null, 2))
        : ""
      setOutput(text)
      if (res && res.files) setFiles(res.files)
      if (res && res.content) setContent(res.content)
      setError("")
    }
    setLoading(false)
  }

  // Wrap form's onSubmit to set loading before the form fires its own API call
  const handleSubmitStart = () => {
    setLoading(true)
    setError("")
    setOutput("")
    setFiles([])
    setContent(null)
  }

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 200,
      background: "#0B0B0D",
      display: "flex", flexDirection: "column",
      animation: "panelIn 0.2s ease",
    }}>
      {/* Top gold bar */}
      <div style={{
        height: 3,
        background: `linear-gradient(90deg, ${gold}, #F5C542, ${gold})`,
        flexShrink: 0,
      }} />

      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", gap: 16,
        padding: "14px 24px",
        borderBottom: "1px solid #1A1A1E",
        background: "#0D0D0F",
        flexShrink: 0,
      }}>
        <button onClick={onBack} style={{
          display: "flex", alignItems: "center", gap: 6,
          padding: "7px 14px", borderRadius: 2,
          border: "1px solid #222", background: "#111",
          color: "#888", fontSize: 11, fontWeight: 700,
          letterSpacing: "0.08em", cursor: "pointer",
          fontFamily: "'Barlow', sans-serif",
          textTransform: "uppercase",
        }}>
          ← Back
        </button>

        <div style={{ width: 1, height: 28, background: "#222" }} />

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 22 }}>{mod.icon}</span>
          <div>
            <div style={{
              fontFamily: "'Barlow Condensed', sans-serif",
              fontWeight: 800, fontStyle: "italic",
              fontSize: 17, color: "#F0F0F2",
              textTransform: "uppercase", lineHeight: 1,
            }}>{mod.title}</div>
            <div style={{
              fontFamily: "'Barlow Condensed', sans-serif",
              fontSize: 12, color: "#555",
              textTransform: "uppercase", fontWeight: 600,
            }}>{mod.subtitle}</div>
          </div>
        </div>

        <div style={{ flex: 1 }} />

        <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
          <div style={{ width: 5, height: 5, background: gold, borderRadius: 1, boxShadow: `0 0 8px ${gold}44` }} />
          <span style={{ fontSize: 11, color: gold, fontWeight: 700 }}>{mod.impact}</span>
        </div>
      </div>

      {/* Split panel */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left: form */}
        <div style={{
          width: 420, flexShrink: 0,
          background: "#0D0D0F",
          borderRight: "1px solid #1A1A1E",
          overflowY: "auto",
          display: "flex", flexDirection: "column",
        }}>
          <div style={{ padding: "20px 24px 8px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
              <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
              <span style={{ fontSize: 10, fontWeight: 800, color: "#666", letterSpacing: "0.12em", textTransform: "uppercase" }}>
                Input Form
              </span>
            </div>
          </div>

          <div style={{ padding: "0 24px 32px", flex: 1 }}>
            {FormComponent ? (
              <FormComponent
                onSubmit={handleFormResult}
                onSubmitStart={handleSubmitStart}
                loading={loading}
              />
            ) : (
              <p style={{ color: "#555", fontSize: 13 }}>No form available for this module.</p>
            )}
          </div>
        </div>

        {/* Right: output */}
        <OutputPanel
          output={output}
          loading={loading}
          error={error}
          files={files}
          content={content}
          moduleName={mod.id}
        />
      </div>
    </div>
  )
}
