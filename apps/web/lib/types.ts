export type NavItem = {
  label: string;
  href: string;
  icon: string;
  badge?: string;
};

export type FocusTask = {
  title: string;
  subject: string;
  duration: string;
  kind: "lesson" | "practice" | "revision";
  complete?: boolean;
};

export type SubjectProgress = {
  name: string;
  shortName: string;
  tone: "violet" | "coral" | "blue" | "mint";
  percent: number;
  meta: string;
};

export type DashboardSnapshot = {
  student: {
    name: string;
    level: string;
    attempt: string;
    examDate: string;
    daysLeft: number;
  };
  focusTasks: FocusTask[];
  subjects: SubjectProgress[];
  metrics: {
    label: string;
    value: string;
    detail: string;
    trend?: string;
    tone: "violet" | "mint" | "coral" | "blue";
  }[];
};
