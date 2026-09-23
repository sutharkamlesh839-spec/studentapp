import Link from "next/link";

export default function PrivacyPage() {
  return <main className="legal-page"><Link href="/" className="auth-brand"><span className="brand-mark">ca<span>•</span></span><span><strong>CA OS</strong><small>student workspace</small></span></Link><span className="eyebrow">Legal</span><h1>Privacy policy</h1><p className="muted">The production policy will explain data collection, profile visibility, answer-sheet storage, analytics controls, retention, deletion, subprocessors and user rights under applicable Indian law.</p><Link href="/" className="button button-primary">Back to dashboard</Link></main>;
}
