import Link from "next/link";

export default function TermsPage() {
  return <main className="legal-page"><Link href="/" className="auth-brand"><span className="brand-mark">ca<span>•</span></span><span><strong>CA OS</strong><small>student workspace</small></span></Link><span className="eyebrow">Legal</span><h1>Terms of service</h1><p className="muted">This foundation preview is for product validation. Before public launch, terms will cover accounts, authorized ICAI content, student submissions, acceptable use, intellectual property, and account closure.</p><Link href="/" className="button button-primary">Back to dashboard</Link></main>;
}
