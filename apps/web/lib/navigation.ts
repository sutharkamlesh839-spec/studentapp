import type { NavItem } from "@/lib/types";

export const studentNavigation: NavItem[] = [
  { label: "Dashboard", href: "/", icon: "layout-dashboard" },
  { label: "Study resources", href: "/resources", icon: "book-open" },
  { label: "MCQ practice", href: "/mcq", icon: "circle-help" },
  { label: "Test series", href: "/tests", icon: "clipboard-check" },
  { label: "Syllabus tracker", href: "/syllabus", icon: "chart-no-axes-combined" },
  { label: "Study planner", href: "/planner", icon: "calendar-days" },
  { label: "Revision", href: "/revision", icon: "rotate-ccw" },
  { label: "Past paper analysis", href: "/past-papers", icon: "scan-search" },
  { label: "Videos", href: "/videos", icon: "play-square" },
  { label: "Paper evaluation", href: "/papers", icon: "file-text" },
  { label: "My library", href: "/library", icon: "bookmark" },
];

export const facultyNavigation: NavItem[] = [
  { label: "Faculty dashboard", href: "/faculty", icon: "layout-dashboard" },
  { label: "Assigned students", href: "/faculty/students", icon: "user-round" },
  { label: "Paper evaluations", href: "/faculty/papers", icon: "file-text" },
  { label: "Queries", href: "/faculty/queries", icon: "message-circle" },
  { label: "Tests", href: "/faculty/tests", icon: "clipboard-check" },
  { label: "Resources", href: "/faculty/resources", icon: "book-open" },
  { label: "Analytics", href: "/faculty/analytics", icon: "chart-no-axes-combined" },
];

export const adminNavigation: NavItem[] = [
  { label: "Admin dashboard", href: "/admin", icon: "layout-dashboard" },
  { label: "Students", href: "/admin/students", icon: "user-round" },
  { label: "Faculty", href: "/admin/faculty", icon: "briefcase-business" },
  { label: "Resources", href: "/admin/resources", icon: "book-open" },
  { label: "MCQ management", href: "/admin/mcqs", icon: "circle-help" },
  { label: "Tests", href: "/admin/tests", icon: "clipboard-check" },
  { label: "Learning content", href: "/admin/content", icon: "play-square" },
  { label: "Evaluations", href: "/admin/evaluations", icon: "file-text" },
  { label: "Audit logs", href: "/admin/audit-logs", icon: "shield-check" },
  { label: "Settings", href: "/admin/settings", icon: "settings" },
];

export const supportNavigation: NavItem[] = [
  { label: "Queries", href: "/queries", icon: "message-circle", badge: "2" },
  { label: "AI zone", href: "/ai", icon: "sparkles" },
  { label: "Articleship", href: "/articleship", icon: "briefcase-business" },
  { label: "Career", href: "/career", icon: "compass" },
  { label: "ICAI updates", href: "/icai-updates", icon: "landmark" },
];
