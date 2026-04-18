const gold = "#D4A017"

export default function SectionHead({ title, badge }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
      <div style={{ width: 4, height: 20, background: gold, borderRadius: 1 }} />
      <h2 style={{
        fontFamily: "'Barlow Condensed', sans-serif",
        fontWeight: 800, fontStyle: "italic",
        fontSize: 17, color: "#E8E8EA",
        textTransform: "uppercase", letterSpacing: "0.04em", margin: 0,
      }}>{title}</h2>
      {badge && (
        <span style={{
          fontSize: 8, fontWeight: 800, color: gold,
          background: `${gold}12`, padding: "4px 10px", borderRadius: 2,
          border: `1px solid ${gold}25`, letterSpacing: "0.12em",
        }}>{badge}</span>
      )}
      <div style={{ flex: 1, height: 1, background: "linear-gradient(90deg, #222, transparent)" }} />
    </div>
  )
}
