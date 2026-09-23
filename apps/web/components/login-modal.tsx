"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Icon } from "@/components/icon";
import { apiFetch, ApiError } from "@/lib/api-client";

export function LoginModal({ onAuthenticated }: { onAuthenticated: (user: { full_name: string; roles?: string[] }) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result = await apiFetch<{ user: { full_name: string; roles?: string[] } }>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("caos-user", JSON.stringify(result.user));
      onAuthenticated(result.user);
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : "The API could not be reached. Start the backend and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-backdrop auth-gate-backdrop" role="presentation">
      <section className="login-gate-modal" role="dialog" aria-modal="true" aria-labelledby="login-gate-title">
        <div className="login-gate-aside">
          <span className="brand-mark">ca<span>•</span></span>
          <span className="login-gate-overline">Your CA workspace</span>
          <h2>Keep your preparation moving.</h2>
          <p>Sign in to access your resources, practice history and personal plan.</p>
          <div className="login-gate-points"><span><Icon name="shield-check" size={14} /> Secure session</span><span><Icon name="sparkles" size={14} /> Personalised workspace</span></div>
        </div>
        <div className="login-gate-form">
          <div className="login-gate-header"><div><span className="eyebrow">Welcome back</span><h1 id="login-gate-title">Sign in to continue</h1><p>Use your CA OS student or staff account.</p></div><div className="login-gate-badge"><Icon name="lock" size={15} /></div></div>
          <form onSubmit={submit} className="auth-form">
            <label>Email address<input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" required /></label>
            <label><span className="label-action"><span>Password</span><Link href="/forgot-password">Forgot password?</Link></span><input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" required /></label>
            {error ? <div className="form-error" role="alert"><Icon name="circle-help" size={15} /> {error}</div> : null}
            <button className="button button-primary auth-submit" type="submit" disabled={loading}>{loading ? "Checking your account…" : "Sign in"}<Icon name="arrow-right" size={16} /></button>
          </form>
          <p className="login-gate-register">New to CA OS? <Link href="/register">Create a student account</Link></p>
          <p className="login-gate-security"><Icon name="shield-check" size={13} /> Passwords are securely hashed and sessions can be revoked.</p>
        </div>
      </section>
    </div>
  );
}
