import { useState } from "react";
import { supabase } from "../supabase";

const gold = "#D4A017";
const inputStyle = {
  width: "100%", background: "#111113", border: "1px solid #222",
  borderRadius: 3, color: "#CCC", padding: "12px 16px",
  fontSize: 14, fontFamily: "'Barlow', sans-serif", outline: "none",
  marginBottom: 16
};

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState(null);

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        setError("Success! Please check your email to verify your account.");
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
          <div style={{ textAlign: "center", marginBottom: 32 }}>
            <span style={{ fontSize: 32 }}>⚙️</span>
            <h1 style={{
              fontFamily: "'Barlow Condensed', sans-serif", fontWeight: 800, fontStyle: "italic",
              fontSize: 28, color: "#F2F2F4", textTransform: "uppercase", margin: "10px 0 0"
            }}>Shop Command Center</h1>
            <p style={{ fontSize: 11, color: gold, fontWeight: 700, letterSpacing: "0.14em", textTransform: "uppercase", margin: "4px 0 0" }}>
              {isSignUp ? "Create Account" : "Secure Login"}
            </p>
          </div>

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
              style={inputStyle}
              required
            />

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
              {loading ? "Processing..." : (isSignUp ? "Sign Up" : "Log In")}
            </button>
          </form>

          <div style={{ textAlign: "center", marginTop: 20 }}>
            <button
              type="button"
              onClick={() => { setIsSignUp(!isSignUp); setError(null); }}
              style={{
                background: "none", border: "none", color: "#666", cursor: "pointer",
                fontSize: 12, fontWeight: 600, textDecoration: "underline"
              }}
            >
              {isSignUp ? "Already have an account? Log in" : "Need an account? Sign up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
