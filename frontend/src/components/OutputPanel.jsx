import { useState, useEffect } from "react"

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
  if (!text) return ""
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

function FileTypeLabel({ name }) {
  const n = name.toLowerCase()
  if (n.includes('sms')) return <span style={{ fontSize: 9, padding: '2px 7px', borderRadius: 2, background: '#1A2A1A', border: '1px solid #2A4A2A', color: '#4ADE80', fontWeight: 800, letterSpacing: '0.08em' }}>SMS</span>
  if (n.includes('email')) return <span style={{ fontSize: 9, padding: '2px 7px', borderRadius: 2, background: '#1A1A2A', border: '1px solid #2A2A5A', color: '#60A5FA', fontWeight: 800, letterSpacing: '0.08em' }}>EMAIL</span>
  if (n.includes('phone') || n.includes('script')) return <span style={{ fontSize: 9, padding: '2px 7px', borderRadius: 2, background: '#2A1A1A', border: '1px solid #5A2A1A', color: '#F97316', fontWeight: 800, letterSpacing: '0.08em' }}>PHONE</span>
  return <span style={{ fontSize: 9, padding: '2px 7px', borderRadius: 2, background: '#1A1A1A', border: '1px solid #2A2A2A', color: '#888', fontWeight: 800, letterSpacing: '0.08em' }}>TXT</span>
}

export default function OutputPanel({ output, loading, error, files, content, moduleName }) {
  const [copied, setCopied] = useState("")
  const [activeFile, setActiveFile] = useState(null)
  const [showSummary, setShowSummary] = useState(false)

  const fileEntries = content ? Object.entries(content) : []

  useEffect(() => {
    if (fileEntries.length > 0 && !activeFile) {
      setActiveFile(fileEntries[0][0])
    } else if (fileEntries.length === 0) {
      setActiveFile(null)
    }
  }, [content])

  const handleCopy = (text, label) => {
    copyToClipboard(text)
    setCopied(label)
    setTimeout(() => setCopied(""), 2000)
  }

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

  // Basic layout variables
  const hasFiles = fileEntries.length > 0
  const allText = hasFiles ? fileEntries.map(([k, v]) => v).join('\n\n' + '─'.repeat(40) + '\n\n') : output
  const activeContent = (hasFiles && activeFile) ? content[activeFile] : output || ''
  
  const shortName = (n) => n.replace(/^.*[\\/]/, '').replace(/\.txt$/, '').replace(/_/g, ' ').toUpperCase()

  const hasSms = activeContent && (activeContent.toLowerCase().includes("sms") || activeContent.toLowerCase().includes("text message"))
  const hasEmail = activeContent && (activeContent.toLowerCase().includes("subject:") || activeContent.toLowerCase().includes("email"))
  const hasScript = activeContent && (activeContent.toLowerCase().includes("phone script") || activeContent.toLowerCase().includes("caller:") || activeContent.toLowerCase().includes("staff:"))

  return (
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      background: "#0B0B0D", overflow: "hidden", position: "relative"
    }}>
      {loading && (
        <div style={{
          position: "absolute", inset: 0, zIndex: 10, background: "#0B0B0D",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 16,
        }}>
          <div style={{ display: "flex", gap: 8 }}>
            {[0, 1, 2].map(i => (
              <div key={i} style={{
                width: 8, height: 8, borderRadius: "50%", background: gold,
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
          position: "absolute", inset: 0, zIndex: 10, background: "#0B0B0D",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
          padding: 32, gap: 12,
        }}>
          <div style={{ fontSize: 28 }}>⚠️</div>
          <p style={{ fontSize: 13, color: "#E05252", textAlign: "center", lineHeight: 1.6, margin: 0 }}>{error}</p>
          <p style={{ fontSize: 11, color: "#444", textAlign: "center", margin: 0 }}>Check that the backend is running.</p>
        </div>
      )}

      {!loading && !error && !output && !hasFiles && (
        <div style={{
          position: "absolute", inset: 0, zIndex: 10, background: "#0B0B0D",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10,
        }}>
          <div style={{ fontSize: 32, opacity: 0.3 }}>→</div>
          <p style={{ fontSize: 12, color: "#444", fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase", margin: 0, textAlign: "center" }}>
            Fill in the form and click Generate
          </p>
        </div>
      )}

      {/* Header bar */}
      {(!loading && !error && (output || hasFiles)) && (
        <div style={{
          padding: "14px 20px", borderBottom: "1px solid #1A1A1E", background: "#0D0D0F",
          display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", flexShrink: 0,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flex: 1 }}>
            <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
            <span style={{ fontSize: 10, fontWeight: 800, color: "#666", letterSpacing: "0.12em", textTransform: "uppercase" }}>
              {hasFiles ? `✓ ${fileEntries.length} file${fileEntries.length > 1 ? 's' : ''} generated` : "Output"}
            </span>
          </div>

          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "flex-end" }}>
            <button style={btnStyle("all")} onClick={() => handleCopy(allText, "all")}>
              {copied === "all" ? "✓ Copied" : "Copy All"}
            </button>
            <button
              style={{ ...btnStyle("dl"), color: gold, borderColor: `${gold}30` }}
              onClick={() => downloadTxt(allText, `${moduleName || "output"}.txt`)}
            >
              Download .txt
            </button>
            {hasFiles && output && (
              <button 
                onClick={() => setShowSummary(!showSummary)} 
                style={{
                  padding: '6px 12px', borderRadius: 3, border: '1px solid #222', 
                  background: 'transparent', color: '#888', fontSize: 10, 
                  fontWeight: 700, cursor: 'pointer', fontFamily: "'Barlow', sans-serif", 
                  letterSpacing: '0.08em'
                }}
              >
                {showSummary ? '▲ HIDE SUMMARY' : '▼ SHOW SUMMARY'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Collapsible stdout summary */}
      {showSummary && output && hasFiles && !loading && (
        <div style={{ padding: '12px 20px', borderBottom: '1px solid #151518', background: '#0A0A0C', flexShrink: 0 }}>
          <pre style={{ fontSize: 11, color: '#555', lineHeight: 1.6, whiteSpace: 'pre-wrap', margin: 0 }}>{output}</pre>
        </div>
      )}

      {/* File tabs */}
      {hasFiles && !loading && !error && (
        <div style={{ display: 'flex', overflowX: 'auto', borderBottom: '1px solid #1A1A1E', background: '#0D0D0F', flexShrink: 0 }}>
          {fileEntries.map(([fname]) => (
            <button key={fname} onClick={() => setActiveFile(fname)}
              style={{
                padding: '10px 16px', border: 'none', 
                borderBottom: activeFile === fname ? `2px solid ${gold}` : '2px solid transparent',
                marginBottom: -1, background: 'transparent', color: activeFile === fname ? gold : '#555', 
                fontSize: 10, fontWeight: 800, letterSpacing: '0.07em', cursor: 'pointer', 
                fontFamily: "'Barlow', sans-serif", whiteSpace: 'nowrap', flexShrink: 0
              }}
            >
              {shortName(fname)}
            </button>
          ))}
        </div>
      )}

      {/* Active file action bar */}
      {activeFile && !loading && !error && (
        <div style={{ padding: '10px 20px', borderBottom: '1px solid #151518', display: 'flex', alignItems: 'center', gap: 10, background: '#0D0D0F', flexShrink: 0 }}>
          <FileTypeLabel name={activeFile} />
          <span style={{ fontSize: 11, color: '#666', fontFamily: 'monospace', flex: 1 }}>
            {activeFile.replace(/^.*[\\/]/, '')}
          </span>
          {hasSms && (
            <button style={{...btnStyle("sms"), padding: "4px 10px", fontSize: 9}} onClick={() => handleCopy(extractSection(activeContent, "sms"), "sms")}>
              {copied === "sms" ? "✓" : "Copy SMS"}
            </button>
          )}
          {hasEmail && (
            <button style={{...btnStyle("email"), padding: "4px 10px", fontSize: 9}} onClick={() => handleCopy(extractSection(activeContent, "subject:"), "email")}>
              {copied === "email" ? "✓" : "Copy Email"}
            </button>
          )}
          {hasScript && (
            <button style={{...btnStyle("script"), padding: "4px 10px", fontSize: 9}} onClick={() => handleCopy(extractSection(activeContent, "phone script"), "script")}>
              {copied === "script" ? "✓" : "Copy Script"}
            </button>
          )}
          <button style={{...btnStyle("dl_single"), padding: "4px 10px", fontSize: 9}} onClick={() => downloadTxt(activeContent, activeFile.replace(/^.*[\\/]/, ''))}>
            Download File
          </button>
        </div>
      )}

      {/* Content area */}
      {(!loading && !error && (output || hasFiles)) && (
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px" }}>
          <pre style={{
            fontFamily: "'Barlow', monospace, sans-serif",
            fontSize: 12.5, color: "#CCC",
            lineHeight: 1.75, margin: 0,
            whiteSpace: "pre-wrap", wordBreak: "break-word",
          }}>
            {activeContent}
          </pre>
        </div>
      )}
    </div>
  )
}
