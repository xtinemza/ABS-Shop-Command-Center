import { useState } from "react"

const gold = "#D4A017"

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).catch(() => {
    const el = document.createElement("textarea")
    el.value = text
    document.body.appendChild(el)
    el.select()
    document.execCommand("copy")
    document.body.removeChild(el)
  })
}

function downloadTxt(text, filename) {
  const blob = new Blob([text], { type: "text/plain" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename || "output.txt"
  a.click()
  URL.revokeObjectURL(url)
}

function extractSection(text, keyword) {
  const lines = text.split("\n")
  const sections = []
  let inSection = false
  let current = []
  for (const line of lines) {
    if (line.toLowerCase().includes(keyword.toLowerCase())) {
      if (current.length) sections.push(current.join("\n"))
      current = [line]
      inSection = true
    } else if (inSection) {
      if (line.trim() === "" && current.length > 2) {
        sections.push(current.join("\n"))
        current = []
        inSection = false
      } else {
        current.push(line)
      }
    }
  }
  if (current.length) sections.push(current.join("\n"))
  return sections.join("\n\n")
}

export default function OutputPanel({ output, loading, error, files, moduleName }) {
  const [copied, setCopied] = useState("")

  const handleCopy = (text, label) => {
    copyToClipboard(text)
    setCopied(label)
    setTimeout(() => setCopied(""), 2000)
  }

  const hasSms = output && (output.toLowerCase().includes("sms") || output.toLowerCase().includes("text message"))
  const hasEmail = output && (output.toLowerCase().includes("subject:") || output.toLowerCase().includes("email"))
  const hasScript = output && (output.toLowerCase().includes("phone script") || output.toLowerCase().includes("caller:") || output.toLowerCase().includes("staff:"))

  const btnStyle = (label) => ({
    padding: "7px 14px",
    background: copied === label ? "#1A2A1A" : "#111113",
    border: `1px solid ${copied === label ? "#4ADE8040" : "#222"}`,
    borderRadius: 2,
    color: copied === label ? "#4ADE80" : "#888",
    fontSize: 11, fontWeight: 700,
    letterSpacing: "0.08em", textTransform: "uppercase",
    cursor: "pointer", fontFamily: "'Barlow', sans-serif",
    transition: "all 0.2s",
    whiteSpace: "nowrap",
  })

  return (
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      background: "#0B0B0D", overflow: "hidden",
    }}>
      {/* Header bar */}
      <div style={{
        padding: "14px 20px",
        borderBottom: "1px solid #1A1A1E",
        background: "#0D0D0F",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
          <span style={{ fontSize: 10, fontWeight: 800, color: "#666", letterSpacing: "0.12em", textTransform: "uppercase" }}>
            Output
          </span>
          {output && !loading && (
            <span style={{
              fontSize: 8, fontWeight: 800, color: "#4ADE80",
              background: "#4ADE8010", border: "1px solid #4ADE8025",
              padding: "2px 8px", borderRadius: 2, letterSpacing: "0.1em",
            }}>READY</span>
          )}
        </div>

        {output && !loading && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "flex-end" }}>
            <button style={btnStyle("all")} onClick={() => handleCopy(output, "all")}>
              {copied === "all" ? "✓ Copied" : "Copy All"}
            </button>
            {hasSms && (
              <button style={btnStyle("sms")} onClick={() => handleCopy(extractSection(output, "sms"), "sms")}>
                {copied === "sms" ? "✓ Copied" : "Copy SMS"}
              </button>
            )}
            {hasEmail && (
              <button style={btnStyle("email")} onClick={() => handleCopy(extractSection(output, "subject:"), "email")}>
                {copied === "email" ? "✓ Copied" : "Copy Email"}
              </button>
            )}
            {hasScript && (
              <button style={btnStyle("script")} onClick={() => handleCopy(extractSection(output, "phone script"), "script")}>
                {copied === "script" ? "✓ Copied" : "Copy Script"}
              </button>
            )}
            <button
              style={{ ...btnStyle("dl"), color: gold, borderColor: `${gold}30` }}
              onClick={() => downloadTxt(output, `${moduleName || "output"}.txt`)}
            >
              Download .txt
            </button>
          </div>
        )}
      </div>

      {/* Content area */}
      <div style={{ flex: 1, overflowY: "auto", position: "relative" }}>
        {loading && (
          <div style={{
            position: "absolute", inset: 0,
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            gap: 16,
          }}>
            <div style={{ display: "flex", gap: 8 }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: gold,
                  animation: `goldPulse 1.2s ease ${i * 0.2}s infinite`,
                }} />
              ))}
            </div>
            <span style={{ fontSize: 12, color: "#555", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
              Generating...
            </span>
          </div>
        )}

        {!loading && error && (
          <div style={{
            position: "absolute", inset: 0,
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            padding: 32, gap: 12,
          }}>
            <div style={{ fontSize: 28 }}>⚠️</div>
            <p style={{ fontSize: 13, color: "#E05252", textAlign: "center", lineHeight: 1.6, margin: 0 }}>{error}</p>
            <p style={{ fontSize: 11, color: "#444", textAlign: "center", margin: 0 }}>Check that the backend is running at {import.meta.env.VITE_API_URL || "http://localhost:8000"}</p>
          </div>
        )}

        {!loading && !error && !output && (
          <div style={{
            position: "absolute", inset: 0,
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            gap: 10,
          }}>
            <div style={{ fontSize: 32, opacity: 0.3 }}>→</div>
            <p style={{ fontSize: 12, color: "#444", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase", margin: 0, textAlign: "center" }}>
              Fill in the form and click Generate
            </p>
          </div>
        )}

        {!loading && !error && output && (
          <div style={{ padding: "20px 24px" }}>
            <pre style={{
              fontFamily: "'Barlow', monospace, sans-serif",
              fontSize: 12.5, color: "#CCC",
              lineHeight: 1.75, margin: 0,
              whiteSpace: "pre-wrap", wordBreak: "break-word",
            }}>{output}</pre>

            {files && files.length > 0 && (
              <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid #1A1A1E" }}>
                <div style={{ fontSize: 9, color: "#555", fontWeight: 800, letterSpacing: "0.12em", marginBottom: 8 }}>SAVED FILES</div>
                {files.map((f, i) => (
                  <div key={i} style={{
                    fontSize: 11, color: "#666",
                    fontFamily: "monospace",
                    padding: "4px 0",
                    display: "flex", alignItems: "center", gap: 8,
                  }}>
                    <span style={{ color: "#4ADE80", fontSize: 10 }}>✓</span>
                    {f}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
