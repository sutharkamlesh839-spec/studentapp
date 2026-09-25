"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Icon } from "@/components/icon";
import { apiFetch, ApiError } from "@/lib/api-client";

export default function RegisterPage() {
  const [form, setForm] = useState({ full_name: "", email: "", password: "", level: "CA Intermediate", group_name: "Group 1", current_attempt: "May 2027" });
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const update = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }));

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setStatus(null);
    if (form.password.length < 8 || form.password.toLowerCase() === form.password || form.password.toUpperCase() === form.password) {
      setStatus("Password must be 8+ characters with upper and lower case letters.");
      return;
    }
    setLoading(true);
    try { await apiFetch("/api/v1/auth/register", { method: "POST", body: JSON.stringify(form) }); window.location.assign("/"); }
    catch (error) { setStatus(error instanceof ApiError ? error.message : "Could not reach the API. Try again."); }
    finally { setLoading(false); }
  }

  return <main className="auth-page"><section className="auth-brand-panel"><Link href="/" className="auth-brand"><span className="brand-mark">ca<span>•</span></span><span><strong>CA OS</strong><small>student workspace</small></span></Link><div className="auth-quote"><span className="quote-mark">“</span><h1>Start with one good study day.</h1><p>Your level, attempt and learning preferences shape a workspace that keeps you moving.</p></div><div className="auth-panel-footer"><span>Secure student access</span><span><Icon name="shield-check" size={14} /> Private by design</span></div></section><section className="auth-form-panel"><div className="auth-form-wrap"><div className="mobile-auth-brand"><Link href="/" className="auth-brand"><span className="brand-mark">ca<span>•</span></span><span><strong>CA OS</strong><small>student workspace</small></span></Link></div><div className="auth-heading"><span className="eyebrow">Create your workspace</span><h2>Let’s make a plan.</h2><p>A few details to tailor your CA journey.</p></div><form onSubmit={handleSubmit} className="auth-form"><label>Full name<input value={form.full_name} onChange={(event) => update("full_name", event.target.value)} placeholder="Your full name" required minLength={2} /></label><label>Email address<input type="email" value={form.email} onChange={(event) => update("email", event.target.value)} placeholder="you@example.com" required /></label><div className="auth-two-col"><label>CA level<select value={form.level} onChange={(event) => update("level", event.target.value)}><option>CA Foundation</option><option>CA Intermediate</option><option>CA Final</option></select></label><label>Group<select value={form.group_name} onChange={(event) => update("group_name", event.target.value)}><option>Group 1</option><option>Group 2</option><option>Both Groups</option></select></label></div><label>Password<input type="password" value={form.password} onChange={(event) => update("password", event.target.value)} placeholder="8+ characters, upper & lower case" required minLength={8} /></label>{status ? <div className="form-error" role="alert"><Icon name="circle-help" size={16} /> {status}</div> : null}<button type="submit" className="button button-primary auth-submit" disabled={loading}>{loading ? "Creating your workspace…" : "Create student account"}<Icon name="arrow-right" size={16} /></button></form><div className="auth-divider"><span>Already have an account?</span></div><Link href="/login" className="button outline-button auth-register">Sign in instead <Icon name="arrow-up-right" size={15} /></Link><p className="auth-legal">By continuing, you agree to our <Link href="/terms">Terms</Link> and <Link href="/privacy">Privacy Policy</Link>.</p></div></section></main>;
}
