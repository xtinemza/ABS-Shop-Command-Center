import { useState } from "react"

const gold = "#D4A017"

export default function ModuleCard({ mod, idx, ready, active, onClick }) {
  const [hov, setHov] = useState(false)

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background: active ? "#13120E" : hov ? "#111113" : "#0E0E10",
        border: active ? `1px solid ${gold}40` : hov ? "1px solid #252528" : "1px solid #18181C",
        borderRadius: 3, cursor: "pointer",
        transition: "all 0.2s", position: "relative", overflow: "hidden",
        animation: ready ? `cardIn 0.35s ease ${idx * 0.035}s both` : "none",
      }}
    >
      <div style={{
        height: 2,
        background: hov || active ? `linear-gradient(90deg, ${gold}AA, ${gold}22, transparent)` : "transparent",
        transition: "all 0.3s",
      }} />

      <div style={{ padding: "18px 20px 16px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
          <div style={{
            width: 42, height: 42, borderRadius: 3,
            background: "#0B0B0D", border: "1px solid #1A1A1E",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 21,
          }}>{mod.icon}</div>
          <span style={{
            fontSize: 8, fontWeight: 800, letterSpacing: "0.14em",
            color: mod.status === "suggested" ? gold : "#4A4A50",
            padding: "3px 9px", borderRadius: 2,
            background: mod.status === "suggested" ? `${gold}0F` : "#ffffff05",
            border: `1px solid ${mod.status === "suggested" ? `${gold}20` : "#ffffff08"}`,
          }}>{mod.tag}</span>
        </div>

        <h3 style={{
          fontFamily: "'Barlow Condensed', sans-serif",
          fontWeight: 800, fontStyle: "italic",
          fontSize: 17, color: "#E6E6E8",
          textTransform: "uppercase", lineHeight: 1.1, margin: "0 0 2px",
          letterSpacing: "0.015em",
        }}>{mod.title}</h3>
        <p style={{
          fontFamily: "'Barlow Condensed', sans-serif",
          fontWeight: 600, fontSize: 13.5, color: "#555",
          textTransform: "uppercase", lineHeight: 1.2, margin: "0 0 12px",
        }}>{mod.subtitle}</p>

        <p style={{ fontSize: 12.5, color: "#777", lineHeight: 1.6, margin: "0 0 14px" }}>{mod.desc}</p>

        <div style={{ borderTop: "1px solid #1A1A1E", paddingTop: 11, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
            <div style={{
              width: 5, height: 5, background: gold, borderRadius: 1,
              boxShadow: `0 0 8px ${gold}44`,
            }} />
            <span style={{ fontSize: 11, color: gold, fontWeight: 700 }}>{mod.impact}</span>
          </div>
          <span style={{
            fontSize: 12, color: "#333",
            transform: hov ? "translateX(3px)" : "none",
            transition: "transform 0.2s",
          }}>→</span>
        </div>
      </div>
    </div>
  )
}
