import { useState, useEffect } from "react";
import { getServicePrices, saveServicePrices } from "../api/client";

const gold = "#D4A017";

export default function ServicePricesEditor({ onClose }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getServicePrices();
        // Convert object { "Service": "Price" } to array [{ id, name, price }]
        const arr = Object.entries(data).map(([name, price], idx) => ({
          id: Date.now() + idx,
          name,
          price
        }));
        setItems(arr);
      } catch (e) {
        setError("Failed to load prices: " + e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleAdd = () => {
    setItems([{ id: Date.now(), name: "New Service", price: "$0" }, ...items]);
  };

  const handleRemove = (id) => {
    setItems(items.filter((item) => item.id !== id));
  };

  const handleChange = (id, field, value) => {
    setItems(items.map(item => item.id === id ? { ...item, [field]: value } : item));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      // Convert array back to object
      const data = {};
      items.forEach(item => {
        if (item.name.trim()) {
          data[item.name.trim()] = item.price.trim();
        }
      });
      await saveServicePrices(data);
      onClose(); // Close on success
    } catch (e) {
      setError("Failed to save: " + e.message);
      setSaving(false);
    }
  };

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 9999,
      background: "rgba(0,0,0,0.85)", backdropFilter: "blur(4px)",
      display: "flex", justifyContent: "flex-end"
    }}>
      <div style={{
        width: "100%", maxWidth: 650, background: "#111113",
        borderLeft: `1px solid ${gold}44`,
        display: "flex", flexDirection: "column",
        boxShadow: "-10px 0 30px rgba(0,0,0,0.5)"
      }}>
        {/* Header */}
        <div style={{
          padding: "24px 32px", borderBottom: "1px solid #222",
          display: "flex", justifyContent: "space-between", alignItems: "center",
          background: "linear-gradient(180deg, #1A1A1E 0%, #111113 100%)"
        }}>
          <div>
            <h2 style={{
              margin: 0, fontFamily: "'Barlow Condensed', sans-serif",
              fontSize: 26, color: "#F2F2F4", textTransform: "uppercase",
              fontWeight: 800, fontStyle: "italic", letterSpacing: "0.03em"
            }}>Service Price Editor</h2>
            <p style={{ margin: "4px 0 0", fontSize: 13, color: "#888" }}>
              Customize the prices the AI uses for estimates.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "none", border: "none", color: "#888",
              fontSize: 28, cursor: "pointer", padding: "0 8px"
            }}
          >×</button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: "auto", padding: "24px 32px" }}>
          {error && (
            <div style={{
              background: "#311", border: "1px solid #622", color: "#F88",
              padding: "12px 16px", borderRadius: 4, marginBottom: 20, fontSize: 13
            }}>
              {error}
            </div>
          )}

          {loading ? (
            <div style={{ color: "#888", textAlign: "center", padding: 40 }}>Loading...</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <button
                onClick={handleAdd}
                style={{
                  alignSelf: "flex-start", background: `${gold}22`, color: gold,
                  border: `1px solid ${gold}55`, padding: "8px 16px", borderRadius: 4,
                  cursor: "pointer", fontWeight: 600, fontSize: 12, textTransform: "uppercase",
                  letterSpacing: "0.05em", marginBottom: 10
                }}
              >
                + Add New Service
              </button>

              <div style={{
                display: "grid", gridTemplateColumns: "1fr 150px 40px", gap: 12,
                color: "#666", fontSize: 11, fontWeight: 700, textTransform: "uppercase",
                letterSpacing: "0.1em", paddingBottom: 8, borderBottom: "1px solid #222"
              }}>
                <div>Service Name</div>
                <div>Price Range</div>
                <div></div>
              </div>

              {items.map((item) => (
                <div key={item.id} style={{ display: "grid", gridTemplateColumns: "1fr 150px 40px", gap: 12, alignItems: "center" }}>
                  <input
                    value={item.name}
                    onChange={(e) => handleChange(item.id, "name", e.target.value)}
                    placeholder="e.g. Oil Change"
                    style={{
                      background: "#18181A", border: "1px solid #333", color: "#EEE",
                      padding: "10px 12px", borderRadius: 4, outline: "none", fontSize: 14,
                      fontFamily: "'Barlow', sans-serif"
                    }}
                  />
                  <input
                    value={item.price}
                    onChange={(e) => handleChange(item.id, "price", e.target.value)}
                    placeholder="$0 - $0"
                    style={{
                      background: "#18181A", border: "1px solid #333", color: "#EEE",
                      padding: "10px 12px", borderRadius: 4, outline: "none", fontSize: 14,
                      fontFamily: "'Barlow', sans-serif"
                    }}
                  />
                  <button
                    onClick={() => handleRemove(item.id)}
                    style={{
                      background: "none", border: "none", color: "#666", cursor: "pointer",
                      fontSize: 18, display: "flex", alignItems: "center", justifyContent: "center"
                    }}
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: "20px 32px", borderTop: "1px solid #222",
          background: "#0E0E10", display: "flex", justifyContent: "flex-end", gap: 12
        }}>
          <button
            onClick={onClose}
            disabled={saving}
            style={{
              background: "transparent", border: "1px solid #444", color: "#AAA",
              padding: "10px 24px", borderRadius: 4, cursor: "pointer",
              fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", fontSize: 13
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving || loading}
            style={{
              background: gold, border: "none", color: "#000",
              padding: "10px 24px", borderRadius: 4, cursor: "pointer",
              fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", fontSize: 13,
              boxShadow: `0 0 15px ${gold}44`
            }}
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
