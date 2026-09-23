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
  { label: "My library", href: "/library", icon: "bookmark" },
];

export const supportNavigation: NavItem[] = [
  { label: "Queries", href: "/queries", icon: "message-circle", badge: "2" },
  { label: "AI zone", href: "/ai", icon: "sparkles" },
  { label: "Articleship", href: "/articleship", icon: "briefcase-business" },
  { label: "Career", href: "/career", icon: "compass" },
  { label: "ICAI updates", href: "/icai-updates", icon: "landmark" },
];
