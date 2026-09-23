import type { DashboardSnapshot } from "@/lib/types";

/**
 * Development-only fixture for reviewing the shell before the API is running.
 * Production pages consume the dashboard endpoint and render an empty state
 * until a student has real activity.
 */
export const demoDashboard: DashboardSnapshot = {
  student: {
    name: "Aarav",
    level: "CA Intermediate",
    attempt: "May 2027 · Group 1",
    examDate: "2027-05-02",
    daysLeft: 221,
  },
  metrics: [
    { label: "Preparation score", value: "72", detail: "out of 100", trend: "+6 this week", tone: "violet" },
    { label: "Syllabus covered", value: "64%", detail: "18 of 28 chapters", trend: "+4.2%", tone: "mint" },
    { label: "MCQ accuracy", value: "78%", detail: "1,284 attempted", trend: "+8%", tone: "coral" },
    { label: "Study streak", value: "12 days", detail: "Best: 18 days", trend: "Keep going", tone: "blue" },
  ],
  focusTasks: [
    { title: "Consolidated financial statements", subject: "Advanced Accounting", duration: "90 min", kind: "lesson" },
    { title: "Chapter 4 · Company Law", subject: "Law", duration: "20 questions", kind: "practice" },
    { title: "Income from house property", subject: "Taxation", duration: "30 min", kind: "revision" },
  ],
  subjects: [
    { name: "Advanced Accounting", shortName: "AA", tone: "violet", percent: 72, meta: "8 of 11 chapters" },
    { name: "Corporate & Other Laws", shortName: "LAW", tone: "coral", percent: 55, meta: "6 of 10 chapters" },
    { name: "Taxation", shortName: "TAX", tone: "blue", percent: 43, meta: "4 of 9 chapters" },
    { name: "Cost & Management Accounting", shortName: "CMA", tone: "mint", percent: 68, meta: "6 of 8 chapters" },
  ],
};
