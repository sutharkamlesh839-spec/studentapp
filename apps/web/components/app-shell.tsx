"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Icon } from "@/components/icon";
import { CursorSystem } from "@/components/cursor-system";
import { LoginModal } from "@/components/login-modal";
import { apiFetch, API_BASE_URL } from "@/lib/api-client";
import { adminNavigation, facultyNavigation, studentNavigation, supportNavigation } from "@/lib/navigation";

type AuthUser = { full_name: string; roles?: string[] };

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

function initials(name?: string) {
  return (name ?? "Student").split(" ").map((part) => part[0]).slice(0, 2).join("").toUpperCase();
}

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [authReady, setAuthReady] = useState(false);
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const pathname = usePathname();
  const demoMode = process.env.NEXT_PUBLIC_ENABLE_DEMO !== "false";
  const publicPath = pathname === "/login" || pathname === "/register" || pathname === "/terms" || pathname === "/privacy" || pathname === "/forgot-password";

  useEffect(() => {
    let active = true;

    const restoreSession = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, { credentials: "include" });
        if (!response.ok) throw new Error("No active session");
        const user = await response.json() as AuthUser;
        if (active) {
          setAuthUser(user);
          window.localStorage.setItem("caos-user", JSON.stringify(user));
        }
      } catch {
        if (active) {
          window.localStorage.removeItem("caos-user");
          setAuthUser(null);
        }
      } finally {
        if (active) setAuthReady(true);
      }
    };

    void restoreSession();
    return () => { active = false; };
  }, []);

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
    { label: "View today’s revision", detail: "See what is due", icon: "rotate-ccw", href: "/revision" },
    { label: "Ask a doubt", detail: "Faculty replies in your queue", icon: "message-circle", href: "/queries" },
  ], []);

  const closeNavigation = () => setMobileOpen(false);
  const handleLogout = async () => {
    try { await apiFetch("/api/v1/auth/logout", { method: "POST" }); } catch { /* the local session is still cleared */ }
    window.localStorage.removeItem("caos-user");
    setAuthUser(null);
  };
  const requiresLogin = authReady && !authUser && !publicPath;
  const isAdmin = authUser?.roles?.some((role) => role === "admin" || role === "super_admin") ?? false;
  const isFaculty = authUser?.roles?.includes("faculty") ?? false;
  const routeNeedsAdmin = pathname.startsWith("/admin");
  const routeNeedsFaculty = pathname.startsWith("/faculty");
  const hasRouteAccess = !routeNeedsAdmin && !routeNeedsFaculty || (routeNeedsAdmin && isAdmin) || (routeNeedsFaculty && (isFaculty || isAdmin));
  const primaryNavigation = isAdmin ? adminNavigation : isFaculty ? facultyNavigation : studentNavigation;

  return (
    <div className="app-shell">
      <CursorSystem />
      {mobileOpen ? <button className="sidebar-scrim" aria-label="Close navigation" onClick={closeNavigation} /> : null}
      <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
        <div className="brand-lockup">
          <div className="brand-mark">ca<span>•</span></div>
          <div><div className="brand-name">CA OS</div><div className="brand-caption">student workspace</div></div>
          <button className="icon-button sidebar-close" aria-label="Close navigation" onClick={closeNavigation}><Icon name="x" size={18} /></button>
        </div>
        <div className="workspace-switcher"><div className="workspace-avatar">{initials(authUser?.full_name)[0]}</div><div className="workspace-copy"><span className="workspace-label">Personal workspace</span><span className="workspace-level">Student · protected</span></div><Icon name="chevron-down" size={15} /></div>
        <nav className="sidebar-nav" aria-label="Primary navigation">
          <span className="nav-section-label">{isAdmin ? "Operations" : isFaculty ? "Faculty queue" : "Workspace"}</span>
          {primaryNavigation.map((item) => <NavigationLink key={item.href} {...item} onNavigate={closeNavigation} />)}
          {!isAdmin && !isFaculty ? <><span className="nav-section-label nav-section-label-spaced">More for your journey</span>{supportNavigation.map((item) => <NavigationLink key={item.href} {...item} onNavigate={closeNavigation} />)}</> : null}
        </nav>
        <div className="sidebar-bottom">
          <Link href={"/timetable" as Route} className="exam-countdown" onClick={closeNavigation}><div className="countdown-icon"><Icon name="calendar-check" size={16} /></div><div><span className="countdown-label">Your current attempt</span><strong>Open study calendar</strong></div><Icon name="arrow-up-right" size={15} /></Link>
          <Link href={"/settings" as Route} className="nav-link sidebar-settings" onClick={closeNavigation}><Icon name="settings" size={17} /><span>Settings</span></Link>
          <div className="profile-mini"><div className="avatar avatar-small">{initials(authUser?.full_name)}</div><div className="profile-mini-copy"><strong>{authUser?.full_name ?? "Student account"}</strong><span>{authUser?.roles?.includes("admin") || authUser?.roles?.includes("super_admin") ? "Administrator" : "Student account"}</span></div><button className="icon-button" aria-label="Sign out" title="Sign out" onClick={handleLogout}><Icon name="log-out" size={16} /></button></div>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setMobileOpen(true)}><Icon name="menu" size={21} /></button>
          <div className="breadcrumbs"><span>Workspace</span><span className="breadcrumb-slash">/</span><strong>{pathname === "/" ? "Overview" : pathname.split("/").filter(Boolean).slice(-1)[0] ?? "Workspace"}</strong></div>
          <div className="topbar-actions"><button className="search-trigger" onClick={() => setCommandOpen(true)} aria-label="Open global search"><Icon name="search" size={17} /><span>Search anything</span><kbd><Icon name="command" size={12} /> K</kbd></button><Link href={"/notifications" as Route} className="icon-button notification-button" aria-label="Notifications"><Icon name="bell" size={19} /><span className="notification-dot" /></Link><div className="topbar-avatar avatar">{initials(authUser?.full_name)}</div></div>
        </header>
        <main className="main-content">{authReady && authUser ? hasRouteAccess ? children : <section className="dashboard-card generic-intro"><div className="generic-intro-icon"><Icon name="shield-check" size={23} /></div><div><span className="section-kicker">Protected workspace</span><h2>You do not have access to this area.</h2><p>Your account role does not include this workspace. Contact an administrator if your scope needs to change.</p></div></section> : <div className="auth-gate-placeholder" aria-hidden="true" />}</main>
        <footer className="app-footer"><span>CA OS · Built for the long game</span><span className="footer-status"><i /> All systems operational</span></footer>
      </div>

      {commandOpen ? <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.currentTarget === event.target) setCommandOpen(false); }}><section className="command-modal" role="dialog" aria-modal="true" aria-label="Quick actions"><div className="command-input"><Icon name="search" size={19} /><input autoFocus placeholder="Search resources, questions, videos..." /><kbd>ESC</kbd></div><div className="command-body"><span className="command-label">Quick actions</span>{quickActions.map((action) => <Link href={action.href as Route} key={action.href} className="command-item" onClick={() => setCommandOpen(false)}><span className="command-icon"><Icon name={action.icon} size={17} /></span><span><strong>{action.label}</strong><small>{action.detail}</small></span><Icon name="arrow-right" size={15} /></Link>)}</div><div className="command-footer"><span><kbd>↑</kbd><kbd>↓</kbd> to navigate</span><span><kbd>↵</kbd> to open</span></div></section></div> : null}
      {demoMode ? <div className="demo-pill"><span /> Preview mode · API-backed auth</div> : null}
      {requiresLogin ? <LoginModal onAuthenticated={(user) => setAuthUser(user)} /> : null}
    </div>
  );
}
