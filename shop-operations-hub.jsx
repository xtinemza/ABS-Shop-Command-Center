import { useState, useRef } from "react";

const gold = "#D4A017";

// Sample data to show populated state
const SAMPLE_PARTS = [
  { id: 1, part: "Brake Pads - Ceramic Front", partNum: "BP-CER-001", qty: 3, min: 4, cost: 35.00, vendor: "AutoZone Commercial", vendorPhone: "(800) 288-6966", status: "low" },
  { id: 2, part: "Oil Filter - Standard", partNum: "OF-STD-010", qty: 24, min: 8, cost: 6.50, vendor: "O'Reilly Auto Parts", vendorPhone: "(800) 755-6759", status: "ok" },
  { id: 3, part: "Brake Rotors - Front Pair", partNum: "BR-FRT-003", qty: 0, min: 2, cost: 78.00, vendor: "AutoZone Commercial", vendorPhone: "(800) 288-6966", status: "out" },
  { id: 4, part: "Serpentine Belt - Universal", partNum: "SB-UNI-005", qty: 6, min: 3, cost: 22.00, vendor: "NAPA Auto Parts", vendorPhone: "(800) 535-3738", status: "ok" },
  { id: 5, part: "Cabin Air Filter", partNum: "CAF-STD-008", qty: 5, min: 4, cost: 12.00, vendor: "O'Reilly Auto Parts", vendorPhone: "(800) 755-6759", status: "ok" },
  { id: 6, part: "Wiper Blades - 22in", partNum: "WB-22-012", qty: 2, min: 4, cost: 8.50, vendor: "AutoZone Commercial", vendorPhone: "(800) 288-6966", status: "low" },
];

const SAMPLE_EQUIPMENT = [
  { id: 1, name: "BendPak XPR-10AS 2-Post Lift", type: "Vehicle Lift", serial: "BP-2022-4819", lastService: "2024-08-15", nextDue: "2024-11-15", status: "due", calibration: null },
  { id: 2, name: "Hunter HawkEye Elite Aligner", type: "Alignment Machine", serial: "HE-2023-0092", lastService: "2024-10-01", nextDue: "2025-01-01", status: "ok", calibration: "2025-03-01" },
  { id: 3, name: "Snap-on SOLUS Edge Scanner", type: "Diagnostic Scanner", serial: "SN-2024-1187", lastService: "2024-09-20", nextDue: "2024-12-20", status: "ok", calibration: null },
  { id: 4, name: "Coats 70X Tire Changer", type: "Tire Machine", serial: "CT-2021-3301", lastService: "2024-03-10", nextDue: "2024-06-10", status: "overdue", calibration: null },
  { id: 5, name: "Robinair 34988 AC Machine", type: "AC Recovery Unit", serial: "RB-2023-0445", lastService: "2024-07-01", nextDue: "2025-01-01", status: "ok", calibration: "2025-07-01" },
];

const SAMPLE_EXPENSES = [
  { id: 1, date: "2024-11-15", desc: "Brake pads bulk order", amount: 1450.00, category: "parts", vendor: "AutoZone Commercial" },
  { id: 2, date: "2024-11-14", desc: "Monthly rent", amount: 3200.00, category: "rent", vendor: "Property Management Co" },
  { id: 3, date: "2024-11-14", desc: "Electric bill", amount: 485.00, category: "utilities", vendor: "Houston Energy" },
  { id: 4, date: "2024-11-13", desc: "Google Ads - November", amount: 750.00, category: "marketing", vendor: "Google" },
  { id: 5, date: "2024-11-12", desc: "Snap-on tool cart", amount: 2100.00, category: "tools_equipment", vendor: "Snap-on" },
  { id: 6, date: "2024-11-11", desc: "Oil disposal pickup", amount: 175.00, category: "waste_disposal", vendor: "Clean Harbors" },
  { id: 7, date: "2024-11-10", desc: "ASE training course", amount: 350.00, category: "training", vendor: "ASE Online" },
  { id: 8, date: "2024-11-08", desc: "Filters bulk order", amount: 680.00, category: "parts", vendor: "O'Reilly Auto Parts" },
];

const SAMPLE_WARRANTY = [
  { id: "WC-001", part: "Alternator - Reman", vendor: "O'Reilly", cost: 189.99, vehicle: "2018 Honda Accord", status: "Submitted", days: 14, reimbursed: 0 },
  { id: "WC-002", part: "Water Pump", vendor: "AutoZone", cost: 125.00, vehicle: "2020 Ford F-150", status: "Approved", days: 32, reimbursed: 125.00 },
  { id: "WC-003", part: "Starter Motor", vendor: "NAPA", cost: 210.00, vehicle: "2017 Chevy Silverado", status: "Pending Documentation", days: 7, reimbursed: 0 },
];

const CATEGORY_LABELS = {
  parts: "Parts", labor: "Labor", rent: "Rent", utilities: "Utilities",
  insurance: "Insurance", marketing: "Marketing", tools_equipment: "Tools & Equipment",
  training: "Training", waste_disposal: "Waste Disposal", office_supplies: "Office",
  miscellaneous: "Misc",
};

export default function OperationsHub() {
  const [activeTab, setActiveTab] = useState("parts");
  const [showUpload, setShowUpload] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  const tabs = [
    { id: "parts", label: "Parts Inventory", icon: "📦", count: SAMPLE_PARTS.length, alert: SAMPLE_PARTS.filter(p => p.status !== "ok").length },
    { id: "equipment", label: "Equipment", icon: "🔧", count: SAMPLE_EQUIPMENT.length, alert: SAMPLE_EQUIPMENT.filter(e => e.status !== "ok").length },
    { id: "expenses", label: "Expenses", icon: "💰", count: SAMPLE_EXPENSES.length, alert: 0 },
    { id: "warranty", label: "Warranty Claims", icon: "🛡", count: SAMPLE_WARRANTY.length, alert: SAMPLE_WARRANTY.filter(w => w.days > 30).length },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "#0B0B0D", fontFamily: "'Barlow', sans-serif", color: "#AAA" }}>
      <link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800;900&family=Barlow+Condensed:ital,wght@0,400;0,600;0,700;0,800;1,600;1,700;1,800&display=swap" rel="stylesheet" />
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
        @keyframes slideDown { from { opacity:0; max-height:0; } to { opacity:1; max-height:500px; } }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #222; border-radius: 3px; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: ${gold} !important; }
      `}</style>

      <div style={{ height: 3, background: `linear-gradient(90deg, transparent, ${gold}, transparent)` }} />

      {/* Header */}
      <header style={{
        padding: "20px 32px", display: "flex", alignItems: "center",
        justifyContent: "space-between", borderBottom: "1px solid #1A1A1E",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <button style={{
            padding: "6px 14px", borderRadius: 4, border: "1px solid #2A2A30",
            background: "#111", color: "#888", fontSize: 12, cursor: "pointer",
          }}>← Back</button>
          <span style={{ fontSize: 18 }}>⚙️</span>
          <h1 style={{
            fontFamily: "'Barlow Condensed', sans-serif",
            fontWeight: 800, fontStyle: "italic",
            fontSize: 22, color: "#F0F0F2",
            textTransform: "uppercase", letterSpacing: "0.02em",
          }}>Shop Operations</h1>
        </div>
      </header>

      {/* Tab bar */}
      <div style={{
        display: "flex", borderBottom: "2px solid #1A1A1E",
        padding: "0 32px", gap: 2,
      }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => { setActiveTab(t.id); setShowUpload(false); setShowAddForm(false); }}
            style={{
              padding: "14px 24px", border: "none",
              borderBottom: activeTab === t.id ? `3px solid ${gold}` : "3px solid transparent",
              marginBottom: -2, background: "transparent",
              color: activeTab === t.id ? gold : "#555",
              fontSize: 12, fontWeight: 800, letterSpacing: "0.08em",
              textTransform: "uppercase", cursor: "pointer",
              fontFamily: "'Barlow', sans-serif",
              display: "flex", alignItems: "center", gap: 8,
            }}>
            <span style={{ fontSize: 14 }}>{t.icon}</span>
            {t.label}
            <span style={{
              fontSize: 10, background: activeTab === t.id ? `${gold}20` : "#1A1A1E",
              color: activeTab === t.id ? gold : "#555",
              padding: "2px 7px", borderRadius: 10,
            }}>{t.count}</span>
            {t.alert > 0 && (
              <span style={{
                fontSize: 9, background: "#C0392B", color: "#fff",
                padding: "2px 6px", borderRadius: 10, fontWeight: 700,
              }}>{t.alert}</span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <main style={{ padding: "24px 32px" }}>
        {activeTab === "parts" && <PartsInventory showUpload={showUpload} setShowUpload={setShowUpload} showAddForm={showAddForm} setShowAddForm={setShowAddForm} />}
        {activeTab === "equipment" && <EquipmentLog />}
        {activeTab === "expenses" && <ExpenseTracker showUpload={showUpload} setShowUpload={setShowUpload} showAddForm={showAddForm} setShowAddForm={setShowAddForm} />}
        {activeTab === "warranty" && <WarrantyTracker />}
      </main>
    </div>
  );
}

/* ===== PARTS INVENTORY ===== */
function PartsInventory({ showUpload, setShowUpload, showAddForm, setShowAddForm }) {
  const fileRef = useRef(null);
  const outCount = SAMPLE_PARTS.filter(p => p.status === "out").length;
  const lowCount = SAMPLE_PARTS.filter(p => p.status === "low").length;

  return (
    <div style={{ animation: "fadeIn 0.25s ease" }}>
      {/* Alert bar */}
      {(outCount > 0 || lowCount > 0) && (
        <div style={{
          display: "flex", gap: 12, marginBottom: 20,
        }}>
          {outCount > 0 && (
            <div style={{ flex: 1, padding: "14px 18px", borderRadius: 4, background: "#C0392B12", border: "1px solid #C0392B25", display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 16 }}>🔴</span>
              <span style={{ fontSize: 13, color: "#C0392B", fontWeight: 600 }}>{outCount} part{outCount > 1 ? "s" : ""} OUT OF STOCK</span>
            </div>
          )}
          {lowCount > 0 && (
            <div style={{ flex: 1, padding: "14px 18px", borderRadius: 4, background: `${gold}08`, border: `1px solid ${gold}20`, display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 16 }}>🟡</span>
              <span style={{ fontSize: 13, color: gold, fontWeight: 600 }}>{lowCount} part{lowCount > 1 ? "s" : ""} below minimum threshold</span>
            </div>
          )}
        </div>
      )}

      {/* Actions bar */}
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        marginBottom: 20,
      }}>
        <div style={{ display: "flex", gap: 10 }}>
          <ActionBtn label="+ ADD PART" onClick={() => { setShowAddForm(!showAddForm); setShowUpload(false); }} active={showAddForm} />
          <ActionBtn label="📄 UPLOAD CSV" onClick={() => { setShowUpload(!showUpload); setShowAddForm(false); }} active={showUpload} />
          <ActionBtn label="📋 GENERATE PO" onClick={() => {}} />
        </div>
        <div style={{ fontSize: 12, color: "#555" }}>
          {SAMPLE_PARTS.length} parts tracked
        </div>
      </div>

      {/* CSV Upload panel */}
      {showUpload && (
        <div style={{
          marginBottom: 20, padding: "24px", borderRadius: 4,
          background: "#111113", border: `1px dashed ${gold}44`,
          animation: "fadeIn 0.2s ease",
        }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 24 }}>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: 14, color: "#E8E8EA", fontWeight: 700, marginBottom: 8 }}>
                Upload Parts CSV
              </h3>
              <p style={{ fontSize: 12, color: "#666", lineHeight: 1.6, marginBottom: 16 }}>
                Upload a CSV file with your parts list. Required columns: Part Name, Part Number, Quantity, Min Threshold, Unit Cost, Vendor. Optional: Vendor Phone.
              </p>

              <div style={{
                padding: "28px", borderRadius: 4, border: "2px dashed #2A2A30",
                background: "#0E0E10", textAlign: "center", cursor: "pointer",
              }} onClick={() => fileRef.current?.click()}>
                <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" style={{ display: "none" }} />
                <div style={{ fontSize: 28, marginBottom: 8 }}>📁</div>
                <div style={{ fontSize: 13, color: "#888", marginBottom: 4 }}>
                  Drag & drop your CSV file here, or <span style={{ color: gold, fontWeight: 600 }}>click to browse</span>
                </div>
                <div style={{ fontSize: 11, color: "#444" }}>CSV, XLSX, or XLS — max 5MB</div>
              </div>
            </div>

            <div style={{
              width: 280, padding: "16px", borderRadius: 4,
              background: "#0E0E10", border: "1px solid #1A1A1E",
            }}>
              <div style={{ fontSize: 10, fontWeight: 800, color: "#555", letterSpacing: "0.1em", marginBottom: 10 }}>
                EXPECTED CSV FORMAT
              </div>
              <div style={{
                fontFamily: "monospace", fontSize: 10, color: "#888",
                background: "#0B0B0D", padding: "10px", borderRadius: 3,
                lineHeight: 1.8, whiteSpace: "pre",
              }}>
{`Part Name,Part Number,Qty,Min,Cost,Vendor
Brake Pads,BP-001,12,4,35.00,AutoZone
Oil Filter,OF-010,24,8,6.50,O'Reilly`}
              </div>
              <div style={{ fontSize: 10, color: "#444", marginTop: 8 }}>
                First row must be headers. Existing parts with matching part numbers will be updated.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Part form */}
      {showAddForm && (
        <div style={{
          marginBottom: 20, padding: "24px", borderRadius: 4,
          background: "#111113", border: "1px solid #1A1A1E",
          animation: "fadeIn 0.2s ease",
        }}>
          <h3 style={{ fontSize: 14, color: "#E8E8EA", fontWeight: 700, marginBottom: 16 }}>Add Part</h3>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <MiniField label="Part Name" placeholder="Brake Pads - Ceramic Front" flex="2" />
            <MiniField label="Part Number" placeholder="BP-CER-001" flex="1" />
            <MiniField label="Qty" placeholder="12" flex="0.5" type="number" />
            <MiniField label="Min Threshold" placeholder="4" flex="0.5" type="number" />
            <MiniField label="Unit Cost ($)" placeholder="35.00" flex="0.5" type="number" />
            <MiniField label="Vendor" placeholder="AutoZone Commercial" flex="1.5" />
            <MiniField label="Vendor Phone" placeholder="(800) 288-6966" flex="1" />
          </div>
          <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
            <GoldBtn label="ADD PART →" />
            <button onClick={() => {}} style={{
              padding: "10px 18px", borderRadius: 4, border: "1px solid #2A2A30",
              background: "transparent", color: "#666", fontSize: 11, fontWeight: 700,
              cursor: "pointer", letterSpacing: "0.06em",
            }}>CANCEL</button>
          </div>
        </div>
      )}

      {/* Parts table */}
      <div style={{ borderRadius: 4, border: "1px solid #1A1A1E", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#111113" }}>
              {["STATUS", "PART NAME", "PART #", "QTY", "MIN", "UNIT COST", "VENDOR", ""].map(h => (
                <th key={h} style={{
                  padding: "12px 16px", textAlign: "left", fontSize: 9,
                  fontWeight: 800, color: "#555", letterSpacing: "0.12em",
                  borderBottom: "1px solid #1A1A1E",
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {SAMPLE_PARTS.map(p => (
              <tr key={p.id} style={{ borderBottom: "1px solid #141416" }}>
                <td style={{ padding: "12px 16px" }}>
                  <StatusBadge status={p.status} />
                </td>
                <td style={{ padding: "12px 16px", fontSize: 13, color: "#E8E8EA", fontWeight: 600 }}>{p.part}</td>
                <td style={{ padding: "12px 16px", fontSize: 12, color: "#666", fontFamily: "monospace" }}>{p.partNum}</td>
                <td style={{ padding: "12px 16px", fontSize: 14, fontWeight: 700, color: p.status === "out" ? "#C0392B" : p.status === "low" ? gold : "#E8E8EA" }}>{p.qty}</td>
                <td style={{ padding: "12px 16px", fontSize: 12, color: "#555" }}>{p.min}</td>
                <td style={{ padding: "12px 16px", fontSize: 13, color: "#AAA" }}>${p.cost.toFixed(2)}</td>
                <td style={{ padding: "12px 16px", fontSize: 12, color: "#666" }}>{p.vendor}</td>
                <td style={{ padding: "12px 16px" }}>
                  <button style={{
                    padding: "4px 10px", borderRadius: 3, border: "1px solid #1A1A1E",
                    background: "transparent", color: "#555", fontSize: 11, cursor: "pointer",
                  }}>Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ===== EQUIPMENT ===== */
function EquipmentLog() {
  return (
    <div style={{ animation: "fadeIn 0.25s ease" }}>
      {/* Alerts */}
      {SAMPLE_EQUIPMENT.filter(e => e.status !== "ok").length > 0 && (
        <div style={{
          marginBottom: 20, padding: "14px 18px", borderRadius: 4,
          background: "#C0392B12", border: "1px solid #C0392B25",
          display: "flex", alignItems: "center", gap: 10,
        }}>
          <span style={{ fontSize: 16 }}>⚠️</span>
          <span style={{ fontSize: 13, color: "#C0392B", fontWeight: 600 }}>
            {SAMPLE_EQUIPMENT.filter(e => e.status === "overdue").length} overdue, {SAMPLE_EQUIPMENT.filter(e => e.status === "due").length} due soon
          </span>
        </div>
      )}

      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <ActionBtn label="+ ADD EQUIPMENT" />
        <ActionBtn label="📄 UPLOAD CSV" />
        <ActionBtn label="📊 COMPLIANCE REPORT" />
      </div>

      {/* Equipment cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 12 }}>
        {SAMPLE_EQUIPMENT.map(eq => (
          <div key={eq.id} style={{
            background: "#111113", border: `1px solid ${eq.status === "overdue" ? "#C0392B33" : eq.status === "due" ? `${gold}25` : "#1A1A1E"}`,
            borderRadius: 4, padding: "18px 20px",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#E8E8EA" }}>{eq.name}</div>
                <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>{eq.type} · Serial: {eq.serial}</div>
              </div>
              <StatusBadge status={eq.status} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 12 }}>
              <DataCell label="Last Service" value={eq.lastService} />
              <DataCell label="Next Due" value={eq.nextDue} highlight={eq.status !== "ok"} />
              {eq.calibration && <DataCell label="Calibration Due" value={eq.calibration} />}
            </div>

            <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
              <button style={{
                flex: 1, padding: "8px", borderRadius: 3, border: "1px solid #1A1A1E",
                background: "#0E0E10", color: "#888", fontSize: 11, fontWeight: 600,
                cursor: "pointer", letterSpacing: "0.04em",
              }}>LOG SERVICE</button>
              <button style={{
                padding: "8px 12px", borderRadius: 3, border: "1px solid #1A1A1E",
                background: "transparent", color: "#555", fontSize: 11, cursor: "pointer",
              }}>Edit</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ===== EXPENSES ===== */
function ExpenseTracker({ showUpload, setShowUpload, showAddForm, setShowAddForm }) {
  const totalMonth = SAMPLE_EXPENSES.reduce((s, e) => s + e.amount, 0);
  const byCategory = {};
  SAMPLE_EXPENSES.forEach(e => {
    byCategory[e.category] = (byCategory[e.category] || 0) + e.amount;
  });
  const sortedCats = Object.entries(byCategory).sort((a, b) => b[1] - a[1]);

  return (
    <div style={{ animation: "fadeIn 0.25s ease" }}>
      {/* Summary bar */}
      <div style={{
        display: "flex", gap: 16, marginBottom: 20,
      }}>
        <div style={{
          flex: 1, padding: "18px 22px", borderRadius: 4,
          background: "#111113", border: "1px solid #1A1A1E",
        }}>
          <div style={{ fontSize: 9, fontWeight: 800, color: "#555", letterSpacing: "0.12em", marginBottom: 6 }}>NOVEMBER 2024</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: "#E8E8EA", fontFamily: "'Barlow Condensed', sans-serif" }}>
            ${totalMonth.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: 11, color: "#555", marginTop: 4 }}>{SAMPLE_EXPENSES.length} transactions</div>
        </div>

        {/* Category breakdown mini */}
        <div style={{
          flex: 2, padding: "18px 22px", borderRadius: 4,
          background: "#111113", border: "1px solid #1A1A1E",
        }}>
          <div style={{ fontSize: 9, fontWeight: 800, color: "#555", letterSpacing: "0.12em", marginBottom: 10 }}>TOP CATEGORIES</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {sortedCats.slice(0, 4).map(([cat, amt]) => (
              <div key={cat} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ width: 90, fontSize: 11, color: "#888" }}>{CATEGORY_LABELS[cat] || cat}</div>
                <div style={{ flex: 1, height: 6, background: "#1A1A1E", borderRadius: 3 }}>
                  <div style={{
                    height: 6, borderRadius: 3, width: `${(amt / totalMonth) * 100}%`,
                    background: `linear-gradient(90deg, ${gold}, #B8900F)`,
                  }} />
                </div>
                <div style={{ width: 80, textAlign: "right", fontSize: 12, color: "#AAA", fontWeight: 600 }}>
                  ${amt.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <ActionBtn label="+ ADD EXPENSE" onClick={() => { setShowAddForm(!showAddForm); setShowUpload(false); }} active={showAddForm} />
        <ActionBtn label="📄 UPLOAD CSV" onClick={() => { setShowUpload(!showUpload); setShowAddForm(false); }} active={showUpload} />
        <ActionBtn label="📊 GENERATE REPORT" />
      </div>

      {/* CSV Upload */}
      {showUpload && (
        <div style={{
          marginBottom: 20, padding: "24px", borderRadius: 4,
          background: "#111113", border: `1px dashed ${gold}44`,
          animation: "fadeIn 0.2s ease",
        }}>
          <h3 style={{ fontSize: 14, color: "#E8E8EA", fontWeight: 700, marginBottom: 8 }}>Upload Expenses CSV</h3>
          <p style={{ fontSize: 12, color: "#666", lineHeight: 1.6, marginBottom: 16 }}>
            Required columns: Date, Amount, Description, Category. Optional: Vendor.
          </p>
          <div style={{
            padding: "28px", borderRadius: 4, border: "2px dashed #2A2A30",
            background: "#0E0E10", textAlign: "center", cursor: "pointer",
          }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>📁</div>
            <div style={{ fontSize: 13, color: "#888" }}>
              Drag & drop or <span style={{ color: gold, fontWeight: 600 }}>click to browse</span>
            </div>
            <div style={{ fontSize: 11, color: "#444", marginTop: 4 }}>Categories: parts, labor, rent, utilities, insurance, marketing, tools_equipment, training, waste_disposal</div>
          </div>
        </div>
      )}

      {/* Add expense form */}
      {showAddForm && (
        <div style={{
          marginBottom: 20, padding: "24px", borderRadius: 4,
          background: "#111113", border: "1px solid #1A1A1E",
          animation: "fadeIn 0.2s ease",
        }}>
          <h3 style={{ fontSize: 14, color: "#E8E8EA", fontWeight: 700, marginBottom: 16 }}>Add Expense</h3>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <MiniField label="Date" placeholder="" flex="0.8" type="date" />
            <MiniField label="Amount ($)" placeholder="450.00" flex="0.6" type="number" />
            <MiniField label="Description" placeholder="Brake pads bulk order" flex="2" />
            <div style={{ flex: "1", minWidth: 160 }}>
              <label style={{ display: "block", fontSize: 9, fontWeight: 700, color: "#555", letterSpacing: "0.1em", marginBottom: 6, textTransform: "uppercase" }}>Category</label>
              <select style={{
                width: "100%", padding: "10px 12px", borderRadius: 4,
                border: "1px solid #1A1A1E", background: "#0E0E10",
                color: "#AAA", fontSize: 13,
              }}>
                <option value="">Select...</option>
                {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
            <MiniField label="Vendor" placeholder="AutoZone" flex="1" />
          </div>
          <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
            <GoldBtn label="ADD EXPENSE →" />
          </div>
        </div>
      )}

      {/* Expense table */}
      <div style={{ borderRadius: 4, border: "1px solid #1A1A1E", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#111113" }}>
              {["DATE", "DESCRIPTION", "CATEGORY", "VENDOR", "AMOUNT", ""].map(h => (
                <th key={h} style={{
                  padding: "12px 16px", textAlign: h === "AMOUNT" ? "right" : "left",
                  fontSize: 9, fontWeight: 800, color: "#555", letterSpacing: "0.12em",
                  borderBottom: "1px solid #1A1A1E",
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {SAMPLE_EXPENSES.map(e => (
              <tr key={e.id} style={{ borderBottom: "1px solid #141416" }}>
                <td style={{ padding: "12px 16px", fontSize: 12, color: "#666" }}>{e.date}</td>
                <td style={{ padding: "12px 16px", fontSize: 13, color: "#E8E8EA" }}>{e.desc}</td>
                <td style={{ padding: "12px 16px" }}>
                  <span style={{
                    fontSize: 10, fontWeight: 700, padding: "3px 9px", borderRadius: 3,
                    background: `${gold}10`, color: gold, letterSpacing: "0.04em",
                  }}>{CATEGORY_LABELS[e.category] || e.category}</span>
                </td>
                <td style={{ padding: "12px 16px", fontSize: 12, color: "#666" }}>{e.vendor}</td>
                <td style={{ padding: "12px 16px", fontSize: 14, fontWeight: 700, color: "#E8E8EA", textAlign: "right" }}>
                  ${e.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </td>
                <td style={{ padding: "12px 16px" }}>
                  <button style={{
                    padding: "4px 10px", borderRadius: 3, border: "1px solid #1A1A1E",
                    background: "transparent", color: "#555", fontSize: 11, cursor: "pointer",
                  }}>Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ===== WARRANTY ===== */
function WarrantyTracker() {
  const totalClaimed = SAMPLE_WARRANTY.reduce((s, w) => s + w.cost, 0);
  const totalRecovered = SAMPLE_WARRANTY.reduce((s, w) => s + w.reimbursed, 0);

  return (
    <div style={{ animation: "fadeIn 0.25s ease" }}>
      {/* Summary */}
      <div style={{ display: "flex", gap: 16, marginBottom: 20 }}>
        {[
          { label: "TOTAL CLAIMED", value: `$${totalClaimed.toFixed(2)}`, color: "#E8E8EA" },
          { label: "RECOVERED", value: `$${totalRecovered.toFixed(2)}`, color: "#27AE60" },
          { label: "PENDING", value: `$${(totalClaimed - totalRecovered).toFixed(2)}`, color: gold },
          { label: "OPEN CLAIMS", value: SAMPLE_WARRANTY.filter(w => w.status !== "Resolved").length, color: "#E8E8EA" },
        ].map(s => (
          <div key={s.label} style={{
            flex: 1, padding: "16px 20px", borderRadius: 4,
            background: "#111113", border: "1px solid #1A1A1E",
          }}>
            <div style={{ fontSize: 9, fontWeight: 800, color: "#555", letterSpacing: "0.12em", marginBottom: 6 }}>{s.label}</div>
            <div style={{ fontSize: 24, fontWeight: 800, color: s.color, fontFamily: "'Barlow Condensed', sans-serif" }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <ActionBtn label="+ NEW CLAIM" />
        <ActionBtn label="📊 MONTHLY REPORT" />
      </div>

      {/* Claims */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {SAMPLE_WARRANTY.map(w => (
          <div key={w.id} style={{
            background: "#111113", border: `1px solid ${w.days > 60 ? "#C0392B25" : w.days > 30 ? `${gold}20` : "#1A1A1E"}`,
            borderRadius: 4, padding: "18px 22px",
            display: "flex", alignItems: "center", gap: 20,
          }}>
            <div style={{
              width: 52, height: 52, borderRadius: 4,
              background: "#0E0E10", border: "1px solid #1A1A1E",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: "'Barlow Condensed', sans-serif",
              fontSize: 14, fontWeight: 800, color: gold,
            }}>{w.id}</div>

            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: "#E8E8EA" }}>{w.part}</div>
              <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>
                {w.vehicle} · Vendor: {w.vendor} · ${w.cost.toFixed(2)}
              </div>
            </div>

            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: "#555", letterSpacing: "0.1em" }}>AGE</div>
              <div style={{
                fontSize: 16, fontWeight: 800,
                color: w.days > 60 ? "#C0392B" : w.days > 30 ? gold : "#AAA",
              }}>{w.days}d</div>
            </div>

            <div style={{
              padding: "6px 14px", borderRadius: 3, fontSize: 11, fontWeight: 700,
              background: w.status === "Approved" ? "#27AE6012" : w.status === "Submitted" ? `${gold}10` : "#1A1A1E",
              color: w.status === "Approved" ? "#27AE60" : w.status === "Submitted" ? gold : "#888",
              border: `1px solid ${w.status === "Approved" ? "#27AE6020" : w.status === "Submitted" ? `${gold}20` : "#2A2A30"}`,
            }}>{w.status}</div>

            <button style={{
              padding: "8px 14px", borderRadius: 3, border: "1px solid #1A1A1E",
              background: "transparent", color: "#555", fontSize: 11, cursor: "pointer",
              fontWeight: 600,
            }}>UPDATE</button>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ===== Shared Components ===== */
function StatusBadge({ status }) {
  const styles = {
    ok: { bg: "#27AE6012", color: "#27AE60", border: "#27AE6020", label: "IN STOCK" },
    low: { bg: `${gold}10`, color: gold, border: `${gold}20`, label: "LOW" },
    out: { bg: "#C0392B12", color: "#C0392B", border: "#C0392B25", label: "OUT" },
    due: { bg: `${gold}10`, color: gold, border: `${gold}20`, label: "DUE SOON" },
    overdue: { bg: "#C0392B12", color: "#C0392B", border: "#C0392B25", label: "OVERDUE" },
  };
  const s = styles[status] || styles.ok;
  return (
    <span style={{
      fontSize: 9, fontWeight: 800, padding: "3px 8px", borderRadius: 3,
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
      letterSpacing: "0.08em",
    }}>{s.label}</span>
  );
}

function DataCell({ label, value, highlight }) {
  return (
    <div>
      <div style={{ fontSize: 9, fontWeight: 700, color: "#555", letterSpacing: "0.08em", marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 13, color: highlight ? gold : "#AAA", fontWeight: highlight ? 600 : 400 }}>{value}</div>
    </div>
  );
}

function ActionBtn({ label, onClick, active }) {
  return (
    <button onClick={onClick} style={{
      padding: "10px 18px", borderRadius: 4,
      border: active ? `1px solid ${gold}44` : "1px solid #2A2A30",
      background: active ? `${gold}12` : "#111",
      color: active ? gold : "#888",
      fontSize: 11, fontWeight: 700, cursor: "pointer",
      letterSpacing: "0.06em", fontFamily: "'Barlow', sans-serif",
    }}>{label}</button>
  );
}

function GoldBtn({ label }) {
  return (
    <button style={{
      padding: "10px 24px", borderRadius: 4,
      border: `1px solid ${gold}66`,
      background: `linear-gradient(135deg, ${gold}, #B8900F)`,
      color: "#0B0B0D", fontSize: 11, fontWeight: 800,
      cursor: "pointer", fontFamily: "'Barlow Condensed', sans-serif",
      letterSpacing: "0.1em", textTransform: "uppercase", fontStyle: "italic",
    }}>{label}</button>
  );
}

function MiniField({ label, placeholder, flex = "1", type = "text" }) {
  return (
    <div style={{ flex, minWidth: 120 }}>
      <label style={{
        display: "block", fontSize: 9, fontWeight: 700, color: "#555",
        letterSpacing: "0.1em", marginBottom: 6, textTransform: "uppercase",
      }}>{label}</label>
      <input type={type} placeholder={placeholder} style={{
        width: "100%", padding: "10px 12px", borderRadius: 4,
        border: "1px solid #1A1A1E", background: "#0E0E10",
        color: "#E8E8EA", fontSize: 13, fontFamily: "'Barlow', sans-serif",
      }} />
    </div>
  );
}
