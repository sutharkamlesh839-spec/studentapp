import Link from "next/link";

export default function NotFound() {
  return (
    <main className="not-found">
      <div className="not-found-mark">404</div>
      <p className="eyebrow">That page took a wrong turn</p>
      <h1>We couldn’t find this workspace.</h1>
      <p className="muted">The link may be outdated, or this feature may be arriving in a later phase.</p>
      <Link href="/" className="button button-primary">Back to dashboard</Link>
    </main>
  );
}
