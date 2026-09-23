"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { studentNavigation, supportNavigation } from "@/lib/navigation";

function NavigationLink({ label, href, icon, badge, onNavigate }: { label: string; href: string; icon: string; badge?: string; onNavigate?: () => void }) {
  const pathname = usePathname();
  const active = href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <Link href={href as Route} className={`nav-link ${active ? "nav-link-active" : ""}`} onClick={onNavigate}>
      <Icon name={icon} size={17} />
      <span>{label}</span>
      {badge ? <span className="nav-badge">{badge}</span> : null}
    </Link>
  );
}

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const pathname = usePathname();
  const demoMode = process.env.NEXT_PUBLIC_ENABLE_DEMO !== "false";

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandOpen((open) => !open);
      }
      if (event.key === "Escape") {
        setCommandOpen(false);
        setMobileOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const quickActions = useMemo(() => [
    { label: "Start MCQ practice", detail: "Pick up where you left off", icon: "circle-help", href: "/mcq" },
    { label: "Add study task", detail: "Plan a focused block", icon: "plus", href: "/planner" },
    { label: "View today’s revision", detail: "2 chapters are due", icon: "rotate-ccw", href: "/revision" },
    { label: "Ask a doubt", detail: "Faculty replies in your queue", icon: "message-circle", href: "/queries" },
  ], []);

  const closeNavigation = () => setMobileOpen(false);

  return (
    <div className="app-shell">
      {mobileOpen ? <button className="sidebar-scrim" aria-label="Close navigation" onClick={closeNavigation} /> : null}
      <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark">ca<span>•</span></div>
          <div>
            <div className="brand-name">CA OS</div>
            <div className="brand-caption">student workspace</div>
          </div>
          <button className="icon-button sidebar-close" aria-label="Close navigation" onClick={closeNavigation}>
            <Icon name="x" size={18} />
          </button>
        </div>

        <div className="workspace-switcher">
          <div className="workspace-avatar">A</div>
          <div className="workspace-copy">
            <span className="workspace-label">Personal workspace</span>
            <span className="workspace-level">CA Intermediate · G1</span>
          </div>
          <Icon name="chevron-down" size={15} />
        </div>

        <nav className="sidebar-nav" aria-label="Primary navigation">
          <span className="nav-section-label">Workspace</span>
          {studentNavigation.map((item) => <NavigationLink key={item.href} {...item} onNavigate={closeNavigation} />)}
          <span className="nav-section-label nav-section-label-spaced">More for your journey</span>
          {supportNavigation.map((item) => <NavigationLink key={item.href} {...item} onNavigate={closeNavigation} />)}
        </nav>

        <div className="sidebar-bottom">
          <div className="exam-countdown">
            <div className="countdown-icon"><Icon name="calendar-check" size={16} /></div>
            <div>
              <span className="countdown-label">May 2027 attempt</span>
              <strong>221 days to go</strong>
            </div>
            <Icon name="arrow-up-right" size={15} />
          </div>
          <Link href={"/settings" as Route} className="nav-link sidebar-settings" onClick={closeNavigation}>
            <Icon name="settings" size={17} /><span>Settings</span>
          </Link>
          <div className="profile-mini">
            <div className="avatar avatar-small">AR</div>
            <div className="profile-mini-copy"><strong>Aarav Rao</strong><span>Student account</span></div>
            <button className="icon-button" aria-label="Account menu"><Icon name="more-horizontal" size={17} /></button>
          </div>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setMobileOpen(true)}><Icon name="menu" size={21} /></button>
          <div className="breadcrumbs"><span>Workspace</span><span className="breadcrumb-slash">/</span><strong>{pathname === "/" ? "Overview" : "Student workspace"}</strong></div>
          <div className="topbar-actions">
            <button className="search-trigger" onClick={() => setCommandOpen(true)} aria-label="Open global search">
              <Icon name="search" size={17} /><span>Search anything</span><kbd><Icon name="command" size={12} /> K</kbd>
            </button>
            <button className="icon-button notification-button" aria-label="Notifications"><Icon name="bell" size={19} /><span className="notification-dot" /></button>
            <div className="topbar-avatar avatar">AR</div>
          </div>
        </header>
        <main className="main-content">{children}</main>
        <footer className="app-footer"><span>CA OS · Built for the long game</span><span className="footer-status"><i /> All systems operational</span></footer>
      </div>

      {commandOpen ? (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.currentTarget === event.target) setCommandOpen(false); }}>
          <section className="command-modal" role="dialog" aria-modal="true" aria-label="Quick actions">
            <div className="command-input"><Icon name="search" size={19} /><input autoFocus placeholder="Search resources, questions, videos..." /><kbd>ESC</kbd></div>
            <div className="command-body">
              <span className="command-label">Quick actions</span>
              {quickActions.map((action) => (
                <Link href={action.href as Route} key={action.href} className="command-item" onClick={() => setCommandOpen(false)}>
                  <span className="command-icon"><Icon name={action.icon} size={17} /></span>
                  <span><strong>{action.label}</strong><small>{action.detail}</small></span>
                  <Icon name="arrow-right" size={15} />
                </Link>
              ))}
            </div>
            <div className="command-footer"><span><kbd>↑</kbd><kbd>↓</kbd> to navigate</span><span><kbd>↵</kbd> to open</span></div>
          </section>
        </div>
      ) : null}
      {demoMode ? <div className="demo-pill"><span /> Preview mode · local fixtures</div> : null}
    </div>
  );
}
