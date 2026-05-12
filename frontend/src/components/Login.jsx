import { useState } from "react";
import { supabase } from "../supabase";

const gold = "#D4A017";
const inputStyle = {
  width: "100%", background: "#111113", border: "1px solid #222",
  borderRadius: 3, color: "#CCC", padding: "12px 16px",
  fontSize: 14, fontFamily: "'Barlow', sans-serif", outline: "none",
  marginBottom: 16
};

const linkBtn = {
  background: "none", border: "none", color: "#666", cursor: "pointer",
  fontSize: 12, fontWeight: 600, textDecoration: "underline",
  fontFamily: "'Barlow', sans-serif", padding: 0,
};

// Modes: "login" | "signup" | "forgot"
export default function Login() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const reset = (nextMode) => {
    setMode(nextMode);
    setError(null);
    setSuccess(null);
  };

  // ── Login / Sign-up ────────────────────────────────────────────────────────
  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      if (mode === "signup") {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        setSuccess("Account created! Check your email to verify before logging in.");
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ── Forgot password ────────────────────────────────────────────────────────
  const handleForgot = async (e) => {
    e.preventDefault();
    if (!email.trim()) { setError("Enter your email address above."); return; }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
        redirectTo: `${window.location.origin}/?reset=true`,
      });
      if (error) throw error;
      setSuccess("Password reset email sent! Check your inbox and follow the link.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const modeLabel = mode === "signup" ? "Create Account"
    : mode === "forgot" ? "Reset Password"
    : "Secure Login";

  return (
    <div style={{
      minHeight: "100vh", background: "#0B0B0D",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "'Barlow', sans-serif"
    }}>
      <div style={{
        width: "100%", maxWidth: 400, background: "#0E0E10",
        border: "1px solid #1A1A1E", borderRadius: 4, overflow: "hidden"
      }}>
        <div style={{ height: 3, background: `linear-gradient(90deg, ${gold}, #F5C542, ${gold})` }} />

        <div style={{ padding: "40px 32px" }}>
          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: 32 }}>
            <span style={{ fontSize: 32 }}>⚙️</span>
            <h1 style={{
              fontFamily: "'Barlow Condensed', sans-serif", fontWeight: 800, fontStyle: "italic",
              fontSize: 28, color: "#F2F2F4", textTransform: "uppercase", margin: "10px 0 0"
            }}>Shop Command Center</h1>
            <p style={{ fontSize: 11, color: gold, fontWeight: 700, letterSpacing: "0.14em", textTransform: "uppercase", margin: "4px 0 0" }}>
              {modeLabel}
            </p>
          </div>

          {/* ── Forgot password form ── */}
          {mode === "forgot" ? (
            <form onSubmit={handleForgot}>
              <p style={{ fontSize: 13, color: "#888", marginBottom: 20, lineHeight: 1.6 }}>
                Enter your account email and we'll send you a link to reset your password.
              </p>

              <input
                type="email"
                placeholder="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={inputStyle}
                required
              />

              {success && (
                <div style={{ color: "#4ADE80", fontSize: 13, marginBottom: 16, textAlign: "center", lineHeight: 1.5 }}>
                  ✓ {success}
                </div>
              )}
              {error && (
                <div style={{ color: "#E05252", fontSize: 13, marginBottom: 16, textAlign: "center" }}>
                  {error}
                </div>
              )}

              <button type="submit" disabled={loading} style={{
                width: "100%", padding: "14px 0", borderRadius: 3,
                border: `1px solid ${gold}66`,
                background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`,
                color: "#0B0B0D", fontSize: 14, fontWeight: 800, cursor: loading ? "default" : "pointer",
                fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em",
                textTransform: "uppercase", fontStyle: "italic"
              }}>
                {loading ? "Sending..." : "Send Reset Link"}
              </button>

              <div style={{ textAlign: "center", marginTop: 20 }}>
                <button type="button" onClick={() => reset("login")} style={linkBtn}>
                  ← Back to Log In
                </button>
              </div>
            </form>

          ) : (
            /* ── Login / Sign-up form ── */
            <form onSubmit={handleAuth}>
              <input
                type="email"
                placeholder="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={inputStyle}
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ ...inputStyle, marginBottom: mode === "login" ? 4 : 16 }}
                required
              />

              {/* Forgot password link — only on login screen */}
              {mode === "login" && (
                <div style={{ textAlign: "right", marginBottom: 16 }}>
                  <button
                    type="button"
                    onClick={() => reset("forgot")}
                    style={{ ...linkBtn, fontSize: 12, color: gold }}
                  >
                    Forgot password?
                  </button>
                </div>
              )}

              {success && (
                <div style={{ color: "#4ADE80", fontSize: 13, marginBottom: 16, textAlign: "center" }}>
                  ✓ {success}
                </div>
              )}
              {error && (
                <div style={{ color: "#E05252", fontSize: 13, marginBottom: 16, textAlign: "center" }}>
                  {error}
                </div>
              )}

              <button type="submit" disabled={loading} style={{
                width: "100%", padding: "14px 0", borderRadius: 3,
                border: `1px solid ${gold}66`,
                background: loading ? `${gold}88` : `linear-gradient(135deg, ${gold}, ${gold}CC)`,
                color: "#0B0B0D", fontSize: 14, fontWeight: 800, cursor: loading ? "default" : "pointer",
                fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.12em",
                textTransform: "uppercase", fontStyle: "italic"
              }}>
                {loading ? "Processing..." : (mode === "signup" ? "Sign Up" : "Log In")}
              </button>

              <div style={{ textAlign: "center", marginTop: 20 }}>
                <button
                  type="button"
                  onClick={() => reset(mode === "signup" ? "login" : "signup")}
                  style={linkBtn}
                >
                  {mode === "signup" ? "Already have an account? Log in" : "Need an account? Sign up"}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
