import { Link, useNavigate } from "react-router";
import { useState } from "react";
import { btnCls, inputCls } from "./layout";
import { ErrorState } from "./states";
import { useAuth } from "../lib/auth";
import type { ApiError } from "../lib/api/client";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [f, setF] = useState({ name: "", email: "", phone: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<ApiError | null>(null);
  const reg = mode === "register";

  return (
    <div className="mx-auto max-w-md px-5 py-16">
      <div className="rounded-[2rem] border bg-card p-8 shadow-float">
        <h1 className="font-display text-3xl font-bold">{reg ? "Join PriceBiz" : "Welcome back"}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{reg ? "Share prices and help your community." : "Log in to contribute and discuss."}</p>
        <form className="mt-6 space-y-3" onSubmit={async (e) => {
          e.preventDefault(); setBusy(true); setErr(null);
          try {
            if (reg) await register({ name: f.name, email: f.email, password: f.password, ...(f.phone ? { phone: f.phone } : {}) });
            else await login(f.email, f.password);
            navigate("/profile");
          } catch (e2) { setErr(e2 as ApiError); } finally { setBusy(false); }
        }}>
          {reg && <input required placeholder="Full name" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} className={inputCls} />}
          <input required type="email" placeholder="Email" autoComplete="email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} className={inputCls} />
          {reg && <input type="tel" placeholder="Phone (optional)" value={f.phone} onChange={(e) => setF({ ...f, phone: e.target.value })} className={inputCls} />}
          <input required type="password" minLength={reg ? 8 : undefined} placeholder="Password" autoComplete={reg ? "new-password" : "current-password"} value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} className={inputCls} />
          {err && <ErrorState error={err} />}
          <button disabled={busy} className={`${btnCls} w-full`}>{busy ? "Please wait…" : reg ? "Create account" : "Log in"}</button>
        </form>
        <p className="mt-5 text-center text-sm text-muted-foreground">
          {reg ? <>Already have an account? <Link to="/auth/login" className="text-primary">Log in</Link></> : <>New here? <Link to="/auth/register" className="text-primary">Create an account</Link></>}
        </p>
      </div>
    </div>
  );
}
