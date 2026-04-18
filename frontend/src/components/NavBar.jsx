const gold = "#D4A017"

export default function NavBar({ cat, setCat, categoryMeta }) {
  return (
    <nav style={{
      display: "flex", marginTop: 28, borderBottom: `2px solid #1A1A1E`,
      overflow: "auto", padding: "0 32px",
      background: "linear-gradient(180deg, #111113 0%, #0B0B0D 100%)",
    }}>
      {Object.entries(categoryMeta).map(([k, v]) => {
        const active = cat === k
        return (
          <button key={k} onClick={() => setCat(k)} style={{
            padding: "14px 22px", border: "none",
            borderBottom: active ? `3px solid ${gold}` : "3px solid transparent",
            marginBottom: -2,
            background: "transparent",
            color: active ? gold : "#555",
            fontSize: 11, fontWeight: 800,
            letterSpacing: "0.12em", textTransform: "uppercase",
            cursor: "pointer", fontFamily: "'Barlow', sans-serif",
            transition: "all 0.2s", whiteSpace: "nowrap",
          }}>
            {v.label}
            <span style={{ marginLeft: 6, opacity: 0.5, fontSize: 10 }}>
              {v.count}
            </span>
          </button>
        )
      })}
    </nav>
  )
}
