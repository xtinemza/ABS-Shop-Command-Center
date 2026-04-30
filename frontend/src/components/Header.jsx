const gold = "#D4A017"

export default function Header({ profile, onEditPrices, onEditSops, onEditProfile }) {
  const name = profile?.shop_name || "Shop Command Center"
  const tag = profile?.tagline || "Professional Auto Care"
  return (
    <>
      <div style={{ height: 3, background: `linear-gradient(90deg, transparent, ${gold}, transparent)` }} />
      <header style={{
        position: "relative", overflow: "hidden",
        padding: "36px 32px 0",
        background: "linear-gradient(180deg, #111113 0%, #0B0B0D 100%)",
      }}>
        <div style={{
          position: "absolute", top: -40, right: -20,
          width: 300, height: 300,
          background: `linear-gradient(135deg, ${gold}08 0%, transparent 50%)`,
          transform: "rotate(15deg)", pointerEvents: "none",
        }} />
        <div style={{
          position: "absolute", top: 0, right: 80,
          width: 2, height: 120,
          background: `linear-gradient(180deg, ${gold}33, transparent)`,
          transform: "rotate(25deg)", transformOrigin: "top",
          pointerEvents: "none",
        }} />

        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 20, position: "relative" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 6 }}>
              <div style={{
                width: 50, height: 50, borderRadius: 4,
                background: `linear-gradient(135deg, #18180B, #0F0F0A)`,
                border: `2px solid ${gold}55`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 24, position: "relative",
              }}>
                <span>⚙️</span>
                <div style={{
                  position: "absolute", inset: 0, borderRadius: 4,
                  background: `radial-gradient(circle at 30% 30%, ${gold}15, transparent 60%)`,
                }} />
              </div>
              <div>
                <h1 style={{
                  fontFamily: "'Barlow Condensed', sans-serif",
                  fontWeight: 800, fontStyle: "italic",
                  fontSize: 30, color: "#F2F2F4",
                  textTransform: "uppercase", letterSpacing: "0.03em",
                  lineHeight: 1, margin: 0,
                }}>{name}</h1>
                <p style={{
                  fontSize: 11, color: "#AAA", fontWeight: 600,
                  letterSpacing: "0.08em", margin: "3px 0 0",
                }}>{tag}</p>
                <p style={{
                  fontSize: 11, color: gold, fontWeight: 700,
                  letterSpacing: "0.18em", textTransform: "uppercase",
                  margin: "5px 0 0",
                }}>AI-Powered Operations Suite</p>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", gap: 16, marginBottom: 4, alignItems: "center" }}>
            <div style={{ display: "flex", gap: 12 }}>
              <button onClick={onEditSops} style={{
                background: "transparent", border: `1px solid ${gold}44`,
                color: gold, padding: "8px 16px", borderRadius: 3,
                fontSize: 11, fontWeight: 700, cursor: "pointer",
                fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em",
                textTransform: "uppercase"
              }}>
                📋 EDIT SOPs
              </button>
              <button onClick={onEditPrices} style={{
                background: "transparent", border: `1px solid ${gold}44`,
                color: gold, padding: "8px 16px", borderRadius: 3,
                fontSize: 11, fontWeight: 700, cursor: "pointer",
                fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em",
                textTransform: "uppercase"
              }}>
                ⚙️ EDIT PRICES
              </button>
              <button onClick={onEditProfile} style={{
                background: "transparent", border: `1px solid ${gold}44`,
                color: gold, padding: "8px 16px", borderRadius: 3,
                fontSize: 11, fontWeight: 700, cursor: "pointer",
                fontFamily: "'Barlow', sans-serif", letterSpacing: "0.08em",
                textTransform: "uppercase"
              }}>
                🏢 EDIT PROFILE
              </button>
            </div>
            {[{ n: "13", l: "Core" }, { n: "4", l: "Suggested" }, { n: "5", l: "Categories" }].map((s, i) => (
              <div key={i} style={{
                textAlign: "center", padding: "8px 18px",
                background: "#0E0E10", border: "1px solid #1C1C20", borderRadius: 3,
              }}>
                <div style={{
                  fontFamily: "'Barlow Condensed', sans-serif",
                  fontSize: 26, fontWeight: 800, color: gold, lineHeight: 1,
                }}>{s.n}</div>
                <div style={{ fontSize: 9, color: "#555", fontWeight: 700, letterSpacing: "0.1em", marginTop: 3, textTransform: "uppercase" }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </header>
    </>
  )
}
