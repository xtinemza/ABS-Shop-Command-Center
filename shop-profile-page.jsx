import { useState, useEffect } from "react";

const US_STATES = [
  "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
  "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
  "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
  "VA","WA","WV","WI","WY","DC"
];

const SERVICE_OPTIONS = [
  "General Repair","Oil Changes","Brake Service","Tire Service","Diagnostics",
  "AC / Heating","Transmission","Engine Repair","Electrical","Suspension & Steering",
  "Exhaust","Alignments","State Inspections","Fleet Service","Diesel Repair",
  "Hybrid / EV Service","Custom / Performance","Towing"
];

const INITIAL = {
  shop_name: "", owner_name: "", phone: "", email: "",
  address: "", city: "", state: "", zip: "",
  hours_weekday: "", hours_saturday: "", hours_sunday: "",
  website: "", business_type: "Auto Repair",
  services: [],
  tagline: "", tone: "Professional and friendly",
  labor_rate: "",
  google_review: "", yelp_review: "", facebook_review: "",
  facebook_url: "", instagram_url: "", google_business_url: "",
};

export default function ShopProfilePage() {
  const [profile, setProfile] = useState(INITIAL);
  const [activeSection, setActiveSection] = useState("basics");
  const [saved, setSaved] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const set = (key, val) => {
    setProfile(p => ({ ...p, [key]: val }));
    setSaved(false);
  };

  const toggleService = (svc) => {
    setProfile(p => ({
      ...p,
      services: p.services.includes(svc)
        ? p.services.filter(s => s !== svc)
        : [...p.services, svc]
    }));
    setSaved(false);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  // Completion calc
  const required = ["shop_name", "owner_name", "phone", "address", "city", "state"];
  const recommended = ["website", "hours_weekday", "labor_rate", "google_review", "tagline"];
  const filledReq = required.filter(k => profile[k]).length;
  const filledRec = recommended.filter(k => profile[k]).length;
  const totalFilled = filledReq + filledRec + (profile.services.length > 0 ? 1 : 0);
  const totalFields = required.length + recommended.length + 1;
  const pct = Math.round((totalFilled / totalFields) * 100);

  const sections = [
    { id: "basics", label: "Shop Info", icon: "🏪" },
    { id: "hours", label: "Hours & Rate", icon: "🕐" },
    { id: "services", label: "Services", icon: "🔧" },
    { id: "brand", label: "Brand & Tone", icon: "🎨" },
    { id: "reviews", label: "Reviews & Social", icon: "⭐" },
  ];

  const gold = "#D4A017";

  return (
    <div style={{
      minHeight: "100vh", background: "#0B0B0D",
      fontFamily: "'Barlow', sans-serif", color: "#AAA",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800;900&family=Barlow+Condensed:ital,wght@0,400;0,600;0,700;0,800;1,600;1,700;1,800&family=Playfair+Display:wght@500;600;700;800&display=swap" rel="stylesheet" />
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.6; } }
        @keyframes checkmark { from { transform: scale(0); } to { transform: scale(1); } }
        input:focus, select:focus, textarea:focus { outline: none; border-color: ${gold} !important; }
        ::placeholder { color: #444; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #222; border-radius: 3px; }
      `}</style>

      {/* Top bar */}
      <div style={{ height: 3, background: `linear-gradient(90deg, transparent, ${gold}, transparent)` }} />

      {/* Header */}
      <header style={{
        padding: "20px 32px", display: "flex", alignItems: "center",
        justifyContent: "space-between", borderBottom: "1px solid #1A1A1E",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <button onClick={() => {}} style={{
            padding: "6px 14px", borderRadius: 4, border: "1px solid #2A2A30",
            background: "#111", color: "#888", fontSize: 12, cursor: "pointer",
            fontFamily: "'Barlow', sans-serif",
          }}>← Back</button>
          <span style={{ fontSize: 18 }}>🏪</span>
          <div>
            <h1 style={{
              fontFamily: "'Barlow Condensed', sans-serif",
              fontWeight: 800, fontStyle: "italic",
              fontSize: 22, color: "#F0F0F2",
              textTransform: "uppercase", letterSpacing: "0.02em", margin: 0,
            }}>My Shop Profile</h1>
            <p style={{ fontSize: 12, color: "#666", marginTop: 2 }}>
              This information powers every module in your Command Center
            </p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {/* Completion ring */}
          <div style={{ position: "relative", width: 48, height: 48 }}>
            <svg width="48" height="48" viewBox="0 0 48 48">
              <circle cx="24" cy="24" r="20" fill="none" stroke="#1A1A1E" strokeWidth="3" />
              <circle cx="24" cy="24" r="20" fill="none" stroke={pct === 100 ? "#27AE60" : gold}
                strokeWidth="3" strokeDasharray={`${pct * 1.256} 999`}
                strokeLinecap="round" transform="rotate(-90 24 24)"
                style={{ transition: "stroke-dasharray 0.5s ease" }} />
            </svg>
            <div style={{
              position: "absolute", inset: 0, display: "flex", alignItems: "center",
              justifyContent: "center", fontSize: 12, fontWeight: 800,
              color: pct === 100 ? "#27AE60" : gold,
            }}>{pct}%</div>
          </div>

          <button onClick={() => setShowPreview(!showPreview)} style={{
            padding: "10px 18px", borderRadius: 4, border: "1px solid #2A2A30",
            background: showPreview ? `${gold}15` : "#111",
            color: showPreview ? gold : "#888",
            fontSize: 12, fontWeight: 700, cursor: "pointer",
            fontFamily: "'Barlow', sans-serif", letterSpacing: "0.04em",
          }}>
            {showPreview ? "✕ CLOSE PREVIEW" : "👁 PREVIEW IN MODULE"}
          </button>

          <button onClick={handleSave} style={{
            padding: "10px 24px", borderRadius: 4, border: `1px solid ${gold}66`,
            background: saved ? "#27AE60" : `linear-gradient(135deg, ${gold}, #B8900F)`,
            color: saved ? "#fff" : "#0B0B0D",
            fontSize: 12, fontWeight: 800, cursor: "pointer",
            fontFamily: "'Barlow Condensed', sans-serif",
            letterSpacing: "0.1em", textTransform: "uppercase", fontStyle: "italic",
            transition: "all 0.3s",
          }}>
            {saved ? "✓ SAVED" : "SAVE PROFILE"}
          </button>
        </div>
      </header>

      <div style={{ display: "flex" }}>
        {/* Section nav */}
        <nav style={{
          width: 200, padding: "20px 0", borderRight: "1px solid #1A1A1E",
          flexShrink: 0,
        }}>
          {sections.map(s => {
            const isActive = activeSection === s.id;
            return (
              <button key={s.id} onClick={() => setActiveSection(s.id)} style={{
                display: "flex", alignItems: "center", gap: 10,
                width: "100%", padding: "12px 20px", border: "none",
                background: isActive ? `${gold}10` : "transparent",
                borderLeft: isActive ? `3px solid ${gold}` : "3px solid transparent",
                color: isActive ? "#E8E8EA" : "#666",
                fontSize: 13, fontWeight: isActive ? 700 : 500, cursor: "pointer",
                textAlign: "left", fontFamily: "'Barlow', sans-serif",
                transition: "all 0.15s",
              }}>
                <span style={{ fontSize: 15 }}>{s.icon}</span>
                {s.label}
              </button>
            );
          })}

          {/* Required fields indicator */}
          <div style={{ padding: "20px", marginTop: 16, borderTop: "1px solid #1A1A1E" }}>
            <div style={{ fontSize: 9, fontWeight: 700, color: "#555", letterSpacing: "0.12em", marginBottom: 10 }}>
              REQUIRED FIELDS
            </div>
            {required.map(k => (
              <div key={k} style={{
                display: "flex", alignItems: "center", gap: 8,
                fontSize: 11, color: profile[k] ? "#27AE60" : "#444",
                marginBottom: 6,
              }}>
                <span style={{ fontSize: 10 }}>{profile[k] ? "✅" : "⬜"}</span>
                {k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
              </div>
            ))}
          </div>
        </nav>

        {/* Form area */}
        <div style={{
          flex: 1, padding: "28px 36px",
          maxWidth: showPreview ? "50%" : "100%",
          transition: "max-width 0.3s ease",
        }}>
          {activeSection === "basics" && (
            <FormSection title="Shop Information" subtitle="The basics that appear on every customer-facing output">
              <FieldRow>
                <Field label="Shop Name" required value={profile.shop_name}
                  onChange={v => set("shop_name", v)} placeholder="e.g. Lone Star Auto Repair" />
                <Field label="Owner / Manager Name" required value={profile.owner_name}
                  onChange={v => set("owner_name", v)} placeholder="e.g. Mike Johnson" />
              </FieldRow>
              <FieldRow>
                <Field label="Phone Number" required value={profile.phone}
                  onChange={v => set("phone", v)} placeholder="(713) 555-1234" />
                <Field label="Email" value={profile.email}
                  onChange={v => set("email", v)} placeholder="hello@lonestararepair.com" />
              </FieldRow>
              <FieldRow>
                <Field label="Street Address" required value={profile.address}
                  onChange={v => set("address", v)} placeholder="4821 Westheimer Rd" wide />
              </FieldRow>
              <FieldRow>
                <Field label="City" required value={profile.city}
                  onChange={v => set("city", v)} placeholder="Houston" />
                <SelectField label="State" required value={profile.state}
                  onChange={v => set("state", v)}
                  options={[{ v: "", l: "Select state..." }, ...US_STATES.map(s => ({ v: s, l: s }))]} />
                <Field label="ZIP" value={profile.zip}
                  onChange={v => set("zip", v)} placeholder="77027" />
              </FieldRow>
              <FieldRow>
                <Field label="Website" value={profile.website}
                  onChange={v => set("website", v)} placeholder="https://lonestararepair.com" wide />
              </FieldRow>
              <FieldRow>
                <SelectField label="Business Type" value={profile.business_type}
                  onChange={v => set("business_type", v)}
                  options={[
                    { v: "Auto Repair", l: "Auto Repair" },
                    { v: "Tire Shop", l: "Tire Shop" },
                    { v: "RV Repair", l: "RV Repair" },
                    { v: "Diesel Repair", l: "Diesel Repair" },
                    { v: "Body Shop", l: "Body Shop" },
                    { v: "Specialty / Performance", l: "Specialty / Performance" },
                    { v: "Multi-Service", l: "Multi-Service" },
                  ]} />
              </FieldRow>

              {profile.state && (
                <div style={{
                  marginTop: 16, padding: "14px 18px", borderRadius: 4,
                  background: `${gold}08`, border: `1px solid ${gold}20`,
                  display: "flex", alignItems: "center", gap: 10,
                }}>
                  <span style={{ fontSize: 14 }}>📍</span>
                  <span style={{ fontSize: 12, color: gold }}>
                    State set to <strong>{profile.state}</strong> — this drives tax calculations, labor rate comparisons, and environmental fee disclosures in the Estimate Narrator module.
                  </span>
                </div>
              )}
            </FormSection>
          )}

          {activeSection === "hours" && (
            <FormSection title="Hours & Labor Rate" subtitle="Used in appointment reminders, wait time updates, and estimate context">
              <FieldRow>
                <Field label="Weekday Hours" value={profile.hours_weekday}
                  onChange={v => set("hours_weekday", v)} placeholder="Mon–Fri 7:30am–5:30pm" wide />
              </FieldRow>
              <FieldRow>
                <Field label="Saturday Hours" value={profile.hours_saturday}
                  onChange={v => set("hours_saturday", v)} placeholder="Sat 8am–1pm" />
                <Field label="Sunday Hours" value={profile.hours_sunday}
                  onChange={v => set("hours_sunday", v)} placeholder="Closed" />
              </FieldRow>

              <div style={{ marginTop: 28, marginBottom: 12 }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 10, marginBottom: 16,
                }}>
                  <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
                  <span style={{ fontSize: 10, fontWeight: 800, color: "#777", letterSpacing: "0.12em" }}>
                    LABOR RATE
                  </span>
                </div>
              </div>
              <FieldRow>
                <Field label="Shop Labor Rate ($/hr)" value={profile.labor_rate}
                  onChange={v => set("labor_rate", v)} placeholder="e.g. 120" type="number" />
              </FieldRow>
              <div style={{
                marginTop: 8, padding: "14px 18px", borderRadius: 4,
                background: "#111113", border: "1px solid #1A1A1E",
                fontSize: 12, color: "#666", lineHeight: 1.6,
              }}>
                Your labor rate is used in the Estimate Narrator to show customers how your rate compares to the state average. It helps build trust and transparency.
              </div>
            </FormSection>
          )}

          {activeSection === "services" && (
            <FormSection title="Services Offered" subtitle="Select all services your shop provides — used in welcome kits, seasonal campaigns, and recommendations">
              <div style={{
                display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
                gap: 8, marginTop: 8,
              }}>
                {SERVICE_OPTIONS.map(svc => {
                  const active = profile.services.includes(svc);
                  return (
                    <button key={svc} onClick={() => toggleService(svc)} style={{
                      padding: "12px 16px", borderRadius: 4, cursor: "pointer",
                      border: active ? `1px solid ${gold}44` : "1px solid #1A1A1E",
                      background: active ? `${gold}10` : "#111113",
                      color: active ? "#E8E8EA" : "#666",
                      fontSize: 13, fontWeight: active ? 600 : 400,
                      textAlign: "left", fontFamily: "'Barlow', sans-serif",
                      display: "flex", alignItems: "center", gap: 10,
                      transition: "all 0.15s",
                    }}>
                      <span style={{
                        width: 18, height: 18, borderRadius: 3,
                        border: active ? `2px solid ${gold}` : "2px solid #2A2A30",
                        background: active ? gold : "transparent",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 10, color: "#0B0B0D", fontWeight: 900,
                        transition: "all 0.15s", flexShrink: 0,
                      }}>
                        {active && "✓"}
                      </span>
                      {svc}
                    </button>
                  );
                })}
              </div>
              {profile.services.length > 0 && (
                <div style={{ marginTop: 16, fontSize: 12, color: "#666" }}>
                  {profile.services.length} service{profile.services.length !== 1 ? "s" : ""} selected
                </div>
              )}
            </FormSection>
          )}

          {activeSection === "brand" && (
            <FormSection title="Brand & Tone" subtitle="Controls the personality and voice of all generated content">
              <FieldRow>
                <Field label="Tagline" value={profile.tagline}
                  onChange={v => set("tagline", v)}
                  placeholder="e.g. Honest Work. Fair Prices. Every Time." wide />
              </FieldRow>
              <FieldRow>
                <SelectField label="Communication Tone" value={profile.tone}
                  onChange={v => set("tone", v)}
                  options={[
                    { v: "Professional and friendly", l: "Professional & Friendly" },
                    { v: "Casual and warm", l: "Casual & Warm" },
                    { v: "Straightforward and no-nonsense", l: "Straightforward & Direct" },
                    { v: "Technical and authoritative", l: "Technical & Authoritative" },
                    { v: "Family-oriented and caring", l: "Family-Oriented & Caring" },
                  ]} />
              </FieldRow>
              <div style={{
                marginTop: 16, padding: "18px 20px", borderRadius: 4,
                background: "#111113", border: "1px solid #1A1A1E",
              }}>
                <div style={{ fontSize: 10, fontWeight: 800, color: "#555", letterSpacing: "0.1em", marginBottom: 10 }}>
                  TONE PREVIEW
                </div>
                <div style={{ fontSize: 13, color: "#999", lineHeight: 1.7, fontStyle: "italic" }}>
                  {profile.tone === "Professional and friendly" && `"Hi Sarah, thank you for choosing ${profile.shop_name || "our shop"}. We appreciate your trust and look forward to keeping your vehicle running safely."`}
                  {profile.tone === "Casual and warm" && `"Hey Sarah! Thanks for swinging by ${profile.shop_name || "the shop"} — we loved working on your ride. Let us know if you need anything!"`}
                  {profile.tone === "Straightforward and no-nonsense" && `"Sarah — your brake service is complete. Total: $486.68. Vehicle is ready for pickup. Call ${profile.phone || "us"} with questions."`}
                  {profile.tone === "Technical and authoritative" && `"Sarah, we've completed the front brake pad and rotor replacement on your 2019 Camry. All components torqued to manufacturer specifications. Ready for pickup."`}
                  {profile.tone === "Family-oriented and caring" && `"Hi Sarah! We're so glad you brought your car to the ${profile.shop_name || "shop"} family. Your safety on the road means everything to us. See you next time!"`}
                </div>
              </div>
            </FormSection>
          )}

          {activeSection === "reviews" && (
            <FormSection title="Reviews & Social Media" subtitle="Review links appear in post-service messages. Social links in welcome kits and campaigns.">
              <div style={{
                display: "flex", alignItems: "center", gap: 10, marginBottom: 20,
              }}>
                <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
                <span style={{ fontSize: 10, fontWeight: 800, color: "#777", letterSpacing: "0.12em" }}>
                  REVIEW LINKS
                </span>
              </div>
              <FieldRow>
                <Field label="Google Review Link" value={profile.google_review}
                  onChange={v => set("google_review", v)}
                  placeholder="https://g.page/your-shop/review" wide />
              </FieldRow>
              <FieldRow>
                <Field label="Yelp Review Link" value={profile.yelp_review}
                  onChange={v => set("yelp_review", v)}
                  placeholder="https://yelp.com/biz/your-shop" />
                <Field label="Facebook Review Link" value={profile.facebook_review}
                  onChange={v => set("facebook_review", v)}
                  placeholder="https://facebook.com/your-shop/reviews" />
              </FieldRow>

              <div style={{
                display: "flex", alignItems: "center", gap: 10,
                marginTop: 28, marginBottom: 20,
              }}>
                <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
                <span style={{ fontSize: 10, fontWeight: 800, color: "#777", letterSpacing: "0.12em" }}>
                  SOCIAL MEDIA
                </span>
              </div>
              <FieldRow>
                <Field label="Facebook Page" value={profile.facebook_url}
                  onChange={v => set("facebook_url", v)}
                  placeholder="https://facebook.com/lonestararepair" />
                <Field label="Instagram" value={profile.instagram_url}
                  onChange={v => set("instagram_url", v)}
                  placeholder="@lonestararepair" />
              </FieldRow>
              <FieldRow>
                <Field label="Google Business Profile" value={profile.google_business_url}
                  onChange={v => set("google_business_url", v)}
                  placeholder="https://g.page/your-shop" wide />
              </FieldRow>
            </FormSection>
          )}
        </div>

        {/* Live preview panel */}
        {showPreview && (
          <div style={{
            width: "50%", borderLeft: "1px solid #1A1A1E",
            padding: "28px", overflowY: "auto",
            background: "#0E0E10",
            animation: "fadeIn 0.3s ease",
          }}>
            <div style={{
              display: "flex", alignItems: "center", gap: 10, marginBottom: 20,
            }}>
              <div style={{ width: 3, height: 14, background: gold, borderRadius: 1 }} />
              <span style={{ fontSize: 10, fontWeight: 800, color: "#777", letterSpacing: "0.12em" }}>
                LIVE PREVIEW — HOW YOUR PROFILE APPEARS IN MODULES
              </span>
            </div>

            {/* Email template preview */}
            <div style={{
              background: "#fff", borderRadius: 6, overflow: "hidden",
              boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
            }}>
              {/* Email header */}
              <div style={{
                background: "linear-gradient(135deg, #1B1B1F, #2A2A2E)",
                padding: "24px 28px",
              }}>
                <div style={{
                  fontFamily: "'Playfair Display', serif", fontSize: 20, fontWeight: 700,
                  color: gold,
                }}>
                  {profile.shop_name || "Your Shop Name"}
                </div>
                {profile.tagline && (
                  <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4, fontStyle: "italic" }}>
                    {profile.tagline}
                  </div>
                )}
              </div>

              {/* Sample estimate output */}
              <div style={{ padding: "24px 28px" }}>
                <div style={{ fontSize: 11, color: "#999", marginBottom: 4 }}>
                  From: {profile.shop_name || "Your Shop"} &lt;hello@{profile.website?.replace(/https?:\/\//, "") || "yourshop.com"}&gt;
                </div>
                <div style={{ fontSize: 15, fontWeight: 700, color: "#1B1B1F", marginBottom: 16 }}>
                  Your Repair Estimate — Explained
                </div>

                <p style={{ fontSize: 13, color: "#555", lineHeight: 1.6, marginBottom: 16 }}>
                  Hi Sarah, here's a plain-language breakdown of the repairs we discussed for your 2019 Toyota Camry:
                </p>

                {/* Estimate card */}
                <div style={{ border: "1px solid #E8E4DE", borderRadius: 6, overflow: "hidden", marginBottom: 16 }}>
                  <div style={{
                    background: "#FEF9F0", padding: "12px 18px",
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    borderBottom: "1px solid #E8E4DE",
                  }}>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "#1B1B1F" }}>Front Brake Pads & Rotors</div>
                      <div style={{ fontSize: 11, color: "#B8900F", fontWeight: 600 }}>🔴 IMMEDIATE</div>
                    </div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: "#1B1B1F" }}>$450</div>
                  </div>
                  <div style={{ padding: "14px 18px" }}>
                    <div style={{
                      background: "#FAFAF8", borderRadius: 4, padding: "12px 14px",
                      border: "1px solid #F0EDE8", fontSize: 12, color: "#555",
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                        <span>Parts</span><span style={{ fontWeight: 600 }}>$180.00</span>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                        <span>Labor{profile.labor_rate ? ` (1.5 hrs × $${profile.labor_rate}/hr)` : ""}</span>
                        <span style={{ fontWeight: 600 }}>$270.00</span>
                      </div>
                      {profile.state && (
                        <div style={{ borderTop: "1px solid #E8E4DE", paddingTop: 6, marginTop: 6, display: "flex", justifyContent: "space-between" }}>
                          <span>Est. Tax ({profile.state})</span>
                          <span style={{ fontWeight: 600 }}>$36.68</span>
                        </div>
                      )}
                      <div style={{ borderTop: "1px solid #E8E4DE", paddingTop: 6, marginTop: 6, display: "flex", justifyContent: "space-between", fontWeight: 700, color: "#1B1B1F" }}>
                        <span>Estimated Total</span><span>$486.68</span>
                      </div>
                      {profile.labor_rate && profile.state && (
                        <div style={{ fontSize: 11, color: "#999", marginTop: 8, fontStyle: "italic" }}>
                          {profile.state} average shop rate: $90–$140/hr. Our rate (${profile.labor_rate}/hr) is within the typical range.
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div style={{
                  background: "#F8F6F2", borderRadius: 4, padding: "12px 16px",
                  borderLeft: `3px solid ${gold}`, fontSize: 12, color: "#555", lineHeight: 1.6,
                }}>
                  Questions? Call us at <strong>{profile.phone || "(XXX) XXX-XXXX"}</strong> or reply to this email.
                </div>
              </div>

              {/* Footer */}
              <div style={{
                background: "#1B1B1F", padding: "18px 28px",
                display: "flex", justifyContent: "space-between", alignItems: "center",
                flexWrap: "wrap", gap: 8,
              }}>
                <div>
                  <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 13, fontWeight: 700, color: gold }}>
                    {profile.shop_name || "Your Shop Name"}
                  </div>
                  <div style={{ fontSize: 10, color: "#888", marginTop: 3 }}>
                    {[profile.address, profile.city, profile.state].filter(Boolean).join(", ") || "Your address"}
                  </div>
                  <div style={{ fontSize: 10, color: "#888" }}>
                    {profile.phone || "(XXX) XXX-XXXX"} · {profile.website?.replace(/https?:\/\//, "") || "yourwebsite.com"}
                  </div>
                </div>
                <div style={{ fontSize: 9, color: "#555" }}>
                  {[profile.hours_weekday, profile.hours_saturday].filter(Boolean).join(" · ") || "Your hours"}
                </div>
              </div>
            </div>

            {/* Indicators showing which profile fields are being used */}
            <div style={{ marginTop: 20, padding: "16px 18px", background: "#111113", borderRadius: 4, border: "1px solid #1A1A1E" }}>
              <div style={{ fontSize: 9, fontWeight: 800, color: "#555", letterSpacing: "0.12em", marginBottom: 12 }}>
                PROFILE FIELDS USED IN THIS TEMPLATE
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {[
                  { f: "shop_name", l: "Shop Name" },
                  { f: "phone", l: "Phone" },
                  { f: "address", l: "Address" },
                  { f: "state", l: "State (tax)" },
                  { f: "labor_rate", l: "Labor Rate" },
                  { f: "website", l: "Website" },
                  { f: "hours_weekday", l: "Hours" },
                  { f: "tagline", l: "Tagline" },
                  { f: "owner_name", l: "Owner Name" },
                ].map(({ f, l }) => (
                  <span key={f} style={{
                    fontSize: 10, fontWeight: 700, padding: "4px 10px", borderRadius: 3,
                    background: profile[f] ? "#27AE6012" : "#1A1A1E",
                    color: profile[f] ? "#27AE60" : "#444",
                    border: `1px solid ${profile[f] ? "#27AE6025" : "#1A1A1E"}`,
                    letterSpacing: "0.04em",
                  }}>
                    {profile[f] ? "✓" : "○"} {l}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ===== Form Components ===== */
function FormSection({ title, subtitle, children }) {
  return (
    <div style={{ animation: "fadeIn 0.25s ease" }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{
          fontFamily: "'Barlow Condensed', sans-serif",
          fontWeight: 800, fontStyle: "italic",
          fontSize: 20, color: "#E8E8EA",
          textTransform: "uppercase", letterSpacing: "0.02em", margin: 0,
        }}>{title}</h2>
        <p style={{ fontSize: 12, color: "#555", marginTop: 4 }}>{subtitle}</p>
      </div>
      {children}
    </div>
  );
}

function FieldRow({ children }) {
  return (
    <div style={{
      display: "flex", gap: 16, marginBottom: 16,
      flexWrap: "wrap",
    }}>
      {children}
    </div>
  );
}

function Field({ label, value, onChange, placeholder, required, wide, type = "text" }) {
  return (
    <div style={{ flex: wide ? "1 1 100%" : "1 1 200px", minWidth: 0 }}>
      <label style={{
        display: "block", fontSize: 10, fontWeight: 700,
        color: "#666", letterSpacing: "0.1em", marginBottom: 6,
        textTransform: "uppercase",
      }}>
        {label}{required && <span style={{ color: "#D4A017", marginLeft: 4 }}>*</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: "100%", padding: "11px 14px", borderRadius: 4,
          border: "1px solid #1A1A1E", background: "#111113",
          color: "#E8E8EA", fontSize: 14,
          fontFamily: "'Barlow', sans-serif",
          transition: "border-color 0.2s",
        }}
      />
    </div>
  );
}

function SelectField({ label, value, onChange, options, required }) {
  return (
    <div style={{ flex: "1 1 200px", minWidth: 0 }}>
      <label style={{
        display: "block", fontSize: 10, fontWeight: 700,
        color: "#666", letterSpacing: "0.1em", marginBottom: 6,
        textTransform: "uppercase",
      }}>
        {label}{required && <span style={{ color: "#D4A017", marginLeft: 4 }}>*</span>}
      </label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          width: "100%", padding: "11px 14px", borderRadius: 4,
          border: "1px solid #1A1A1E", background: "#111113",
          color: value ? "#E8E8EA" : "#444", fontSize: 14,
          fontFamily: "'Barlow', sans-serif",
          cursor: "pointer", appearance: "auto",
        }}
      >
        {options.map(o => (
          <option key={o.v} value={o.v}>{o.l}</option>
        ))}
      </select>
    </div>
  );
}
