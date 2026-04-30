import { useState, useEffect } from "react"
import { getHealth, getProfile } from "./api/client"
import { supabase } from "./supabase"
import Login from "./components/Login"
import { modules, categoryMeta } from "./data/modules"
import Header from "./components/Header"
import NavBar from "./components/NavBar"
import SectionHead from "./components/SectionHead"
import ModuleCard from "./components/ModuleCard"
import Drawer from "./components/Drawer"
import ModulePanel from "./components/ModulePanel"
import SetupWizard from "./components/SetupWizard"
import ServicePricesEditor from "./components/ServicePricesEditor"
import SopEditor from "./components/SopEditor"

export default function App() {
  const [cat, setCat] = useState("all")
  const [selected, setSelected] = useState(null)
  const [panelOpen, setPanelOpen] = useState(false)
  const [ready, setReady] = useState(false)
  const [profile, setProfile] = useState(null)
  const [setupNeeded, setSetupNeeded] = useState(false)
  const [bootstrapped, setBootstrapped] = useState(false)
  const [editorOpen, setEditorOpen] = useState(false)
  const [sopEditorOpen, setSopEditorOpen] = useState(false)
  const [profileEditorOpen, setProfileEditorOpen] = useState(false)
  const [session, setSession] = useState(null)

  useEffect(() => {
    async function init() {
      const { data: { session } } = await supabase.auth.getSession()
      setSession(session)
      
      supabase.auth.onAuthStateChange((_event, session) => {
        setSession(session)
      })
      setBootstrapped(true)
      setTimeout(() => setReady(true), 50)
    }
    init()
  }, [])

  useEffect(() => {
    async function fetchUserContext() {
      if (session) {
        try {
          const res = await getProfile()
          const p = res.profile || {}
          if (!p || Object.keys(p).length === 0 || !p.shop_name) {
            setSetupNeeded(true)
          } else {
            setProfile(p)
            setSetupNeeded(false)
          }
        } catch {
          setSetupNeeded(true)
        }
      }
    }
    fetchUserContext()
  }, [session])

  const handleSetupComplete = async () => {
    setSetupNeeded(false)
    try {
      const p = await getProfile()
      setProfile(p)
    } catch {
      // ignore
    }
    setTimeout(() => setReady(true), 50)
  }

  const list = modules.filter(m => cat === "all" || m.category === cat)
  const core = list.filter(m => m.status === "core")
  const suggested = list.filter(m => m.status === "suggested")

  if (!bootstrapped) {
    return (
      <div style={{
        minHeight: "100vh", background: "#0B0B0D",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "'Barlow', sans-serif",
      }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 32, marginBottom: 16 }}>⚙️</div>
          <p style={{ fontSize: 11, color: "#444", fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase" }}>
            Loading...
          </p>
        </div>
      </div>
    )
  }

  if (!session) {
    return <Login />
  }

  if (setupNeeded || profileEditorOpen) {
    return <SetupWizard 
      existingProfile={profile}
      onComplete={async () => {
        setSetupNeeded(false)
        setProfileEditorOpen(false)
        try {
          const res = await getProfile()
          setProfile(res.profile || {})
        } catch {}
        setTimeout(() => setReady(true), 50)
      }} 
      onCancel={profileEditorOpen ? () => setProfileEditorOpen(false) : undefined}
    />
  }

  if (panelOpen && selected) {
    return (
      <ModulePanel
        mod={selected}
        onBack={() => {
          setPanelOpen(false)
        }}
      />
    )
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0B0B0D", fontFamily: "'Barlow', sans-serif", color: "#AAA" }}>
      <Header 
        profile={profile} 
        onEditPrices={() => setEditorOpen(true)} 
        onEditSops={() => setSopEditorOpen(true)}
        onEditProfile={() => setProfileEditorOpen(true)}
      />

      <NavBar cat={cat} setCat={setCat} categoryMeta={categoryMeta} />

      <main style={{ padding: "28px 32px 48px" }}>
        {core.length > 0 && <SectionHead title="Core Modules" />}

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(310px, 1fr))",
          gap: 12,
        }}>
          {core.map((m, i) => (
            <ModuleCard
              key={m.id}
              mod={m}
              idx={i}
              ready={ready}
              active={selected?.id === m.id}
              onClick={() => setSelected(selected?.id === m.id ? null : m)}
            />
          ))}
        </div>

        {suggested.length > 0 && (
          <>
            <div style={{ marginTop: 36 }}>
              <SectionHead title="Suggested Additions" badge="RECOMMENDED" />
            </div>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(310px, 1fr))",
              gap: 12,
            }}>
              {suggested.map((m, i) => (
                <ModuleCard
                  key={m.id}
                  mod={m}
                  idx={i + core.length}
                  ready={ready}
                  active={selected?.id === m.id}
                  onClick={() => setSelected(selected?.id === m.id ? null : m)}
                />
              ))}
            </div>
          </>
        )}

        {list.length === 0 && (
          <div style={{ textAlign: "center", padding: "80px 0" }}>
            <p style={{ fontSize: 40 }}>🔍</p>
            <p style={{ fontSize: 12, color: "#444", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
              No modules in this category
            </p>
          </div>
        )}
      </main>

      <footer style={{
        borderTop: "1px solid #151518",
        padding: "18px 32px",
        display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 9, color: "#333", fontWeight: 700, letterSpacing: "0.1em" }}>POWERED BY</span>
          <span style={{
            fontFamily: "'Barlow Condensed', sans-serif",
            fontWeight: 800, fontStyle: "italic", fontSize: 13, color: "#D4A017",
            textTransform: "uppercase",
          }}>AmericasBestShops.com</span>
        </div>
        <span style={{ fontSize: 9, color: "#282828", fontWeight: 600, letterSpacing: "0.08em" }}>
          WAT FRAMEWORK v1.0
        </span>
      </footer>

      {selected && !panelOpen && (
        <Drawer
          mod={selected}
          onClose={() => setSelected(null)}
          onLaunch={() => setPanelOpen(true)}
        />
      )}

      {editorOpen && <ServicePricesEditor onClose={() => setEditorOpen(false)} />}
      {sopEditorOpen && <SopEditor onClose={() => setSopEditorOpen(false)} />}
    </div>
  )
}
