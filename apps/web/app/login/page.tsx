"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Icon } from "@/components/icon";
import { apiFetch, ApiError } from "@/lib/api-client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus(null);
    setLoading(true);
    try {
      await apiFetch("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      window.location.assign("/");
    } catch (error) {
      setStatus(error instanceof ApiError ? error.message : "Could not reach the API. Check your connection and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-orbit auth-orbit-one" /><div className="auth-orbit auth-orbit-two" />
      <section className="auth-brand-panel"><Link href="/" className="auth-brand"><span className="brand-mark">ca<span>•</span></span><span><strong>CA OS</strong><small>student workspace</small></span></Link><div className="auth-quote"><span className="quote-mark">“</span><h1>Make your preparation feel lighter.</h1><p>One focused workspace for every chapter, revision and attempt ahead.</p><span className="quote-author"><span className="avatar avatar-small">AR</span> Built around how CA students actually study.</span></div><div className="auth-panel-footer"><span>Secure student access</span><span><Icon name="shield-check" size={14} /> Your data is protected</span></div></section>
      <section className="auth-form-panel"><div className="auth-form-wrap"><div className="mobile-auth-brand"><Link href="/" className="auth-brand"><span className="brand-mark">ca<span>•</span></span><span><strong>CA OS</strong><small>student workspace</small></span></Link></div><div className="auth-heading"><span className="eyebrow">Welcome back</span><h2>Pick up where you left off.</h2><p>Sign in to your personal study workspace.</p></div><form onSubmit={handleSubmit} className="auth-form"><label>Email address<input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" required /></label><label>Password<span className="label-action"><span>Password</span><Link href="/forgot-password">Forgot password?</Link></span><input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" required minLength={8} /></label>{status ? <div className="form-error" role="alert"><Icon name="circle-help" size={16} /> {status}</div> : null}<button type="submit" className="button button-primary auth-submit" disabled={loading}>{loading ? "Signing you in…" : "Sign in"}<Icon name="arrow-right" size={16} /></button></form><div className="auth-divider"><span>New to CA OS?</span></div><Link href="/register" className="button outline-button auth-register">Create student account <Icon name="arrow-up-right" size={15} /></Link><p className="auth-legal">By continuing, you agree to our <Link href="/terms">Terms</Link> and <Link href="/privacy">Privacy Policy</Link>.</p></div></section>
    </main>
  );
}
