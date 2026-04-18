import { featureData } from "../data/modules"

const gold = "#D4A017"

export default function Drawer({ mod, onClose, onLaunch }) {
  const fl = featureData[mod.id] || []

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 100, display: "flex", justifyContent: "flex-end" }}>
      <div onClick={onClose} style={{
        position: "absolute", inset: 0,
        background: "rgba(0,0,0,0.75)", backdropFilter: "blur(8px)",
      }} />

      <div style={{
        position: "relative", width: "100%", maxWidth: 460,
        background: "#0D0D0F", borderLeft: "1px solid #1A1A1E",
        overflowY: "auto", animation: "drawerIn 0.25s ease",
      }}>
        <div style={{ height: 3, background: `linear-gradient(90deg, ${gold}, #F5C542, ${gold})` }} />

        <div style={{
          padding: "26px 28px 22px",
          borderBottom: "1px solid #1A1A1E",
          background: "linear-gradient(180deg, #12110D, #0D0D0F)",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
              <div style={{
                width: 54, height: 54, borderRadius: 4,
                background: "#0B0B0D", border: `1px solid ${gold}30`,
                display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28,
              }}>{mod.icon}</div>
              <div>
                <h2 style={{
                  fontFamily: "'Barlow Condensed', sans-serif",
                  fontWeight: 800, fontStyle: "italic",
                  fontSize: 23, color: "#F0F0F2",
                  textTransform: "uppercase", lineHeight: 1.05, margin: 0,
                }}>{mod.title}</h2>
                <p style={{
                  fontFamily: "'Barlow Condensed', sans-serif",
                  fontWeight: 600, fontSize: 15, color: "#666",
                  textTransform: "uppercase", margin: "3px 0 0",
                }}>{mod.subtitle}</p>
              </div>
            </div>
            <button onClick={onClose} style={{
              width: 30, height: 30, borderRadius: 3,
              border: "1px solid #222", background: "#111",
              color: "#555", fontSize: 13, cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>✕</button>
          </div>
        </div>

        <div style={{ padding: "24px 28px" }}>
          <div style={{
            padding: "16px 18px", borderRadius: 3,
            background: `linear-gradient(135deg, #16140D, #11100C)`,
            border: `1px solid ${gold}25`, marginBottom: 24,
            display: "flex", alignItems: "center", gap: 14,
          }}>
            <div style={{
              width: 10, height: 10, borderRadius: 2,
              background: gold, boxShadow: `0 0 12px ${gold}55`,
            }} />
            <div>
              <div style={{ fontSize: 8, color: "#777", fontWeight: 800, letterSpacing: "0.14em", marginBottom: 4 }}>BUSINESS IMPACT</div>
              <div style={{
                fontFamily: "'Barlow Condensed', sans-serif",
                fontSize: 16, color: gold, fontWeight: 800,
                fontStyle: "italic", textTransform: "uppercase",
              }}>{mod.impact}</div>
            </div>
          </div>

          <p style={{ fontSize: 13.5, color: "#888", lineHeight: 1.7, marginBottom: 28 }}>{mod.desc}</p>

          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
            <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
            <span style={{ fontSize: 9, fontWeight: 800, color: "#777", letterSpacing: "0.14em" }}>WHAT'S INSIDE</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
            {fl.map((f, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "11px 14px", borderRadius: 2,
                background: "#111113", border: "1px solid #18181C",
              }}>
                <span style={{
                  fontFamily: "'Barlow Condensed', sans-serif",
                  fontSize: 11, fontWeight: 800, color: gold,
                  width: 22, textAlign: "center", flexShrink: 0,
                }}>{String(i + 1).padStart(2, "0")}</span>
                <span style={{ fontSize: 13, color: "#999", lineHeight: 1.3 }}>{f}</span>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 28, paddingTop: 18, borderTop: "1px solid #18181C", display: "flex", gap: 8 }}>
            <span style={{
              fontSize: 8, fontWeight: 800, color: "#555",
              padding: "4px 10px", borderRadius: 2,
              background: "#111", border: "1px solid #1A1A1E",
              letterSpacing: "0.1em",
            }}>{mod.tag}</span>
            <span style={{
              fontSize: 8, fontWeight: 800,
              color: mod.status === "core" ? "#4ADE80" : gold,
              padding: "4px 10px", borderRadius: 2,
              background: mod.status === "core" ? "#4ADE8008" : `${gold}08`,
              border: `1px solid ${mod.status === "core" ? "#4ADE8020" : `${gold}20`}`,
              letterSpacing: "0.1em",
            }}>
              {mod.status === "core" ? "● CORE" : "◐ SUGGESTED"}
            </span>
          </div>

          <button
            onClick={onLaunch}
            style={{
              width: "100%", marginTop: 24,
              padding: "16px 0", borderRadius: 3,
              border: `1px solid ${gold}66`,
              background: `linear-gradient(135deg, ${gold}, ${gold}CC)`,
              color: "#0B0B0D", fontSize: 13, fontWeight: 800,
              cursor: "pointer",
              fontFamily: "'Barlow Condensed', sans-serif",
              letterSpacing: "0.12em", textTransform: "uppercase", fontStyle: "italic",
            }}>
            Launch Module →
          </button>
        </div>
      </div>
    </div>
  )
}
