"use client";

import { useEffect, useState } from "react";
import { Icon } from "@/components/icon";
import { apiFetch } from "@/lib/api-client";
import type { DashboardSnapshot, FocusTask } from "@/lib/types";

type DashboardSummaryResponse = {
  user: { full_name: string; student_level?: string | null; student_group?: string | null; student_attempt?: string | null };
};

const taskIcon: Record<FocusTask["kind"], string> = {
  lesson: "book-open",
  practice: "circle-help",
  revision: "rotate-ccw",
};

export function DashboardView({ snapshot }: { snapshot: DashboardSnapshot }) {
  const [activeSnapshot, setActiveSnapshot] = useState(snapshot);
  const [tasks, setTasks] = useState(activeSnapshot.focusTasks);
  const [examMode, setExamMode] = useState(false);

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_ENABLE_DEMO !== "false") return;
    apiFetch<DashboardSummaryResponse>("/api/v1/dashboard/summary").then((response) => {
      const liveSnapshot: DashboardSnapshot = {
        student: {
          name: response.user.full_name,
          level: response.user.student_level ?? "CA student",
          attempt: response.user.student_attempt ?? "Set your current attempt in Profile",
          examDate: "",
          daysLeft: 0,
        },
        focusTasks: [],
        subjects: [],
        metrics: [
          { label: "Preparation score", value: "—", detail: "Complete activity to calculate", trend: "Awaiting activity", tone: "violet" },
          { label: "Syllabus covered", value: "—", detail: "Add your first chapter", trend: "Not started", tone: "mint" },
          { label: "MCQ accuracy", value: "—", detail: "No attempts yet", trend: "Not started", tone: "coral" },
          { label: "Study streak", value: "0 days", detail: "Start your first session", trend: "Ready when you are", tone: "blue" },
        ],
      };
      setActiveSnapshot(liveSnapshot);
      setTasks([]);
    }).catch(() => undefined);
  }, []);

  const completeTask = (index: number) => {
    setTasks((current) => current.map((task, taskIndex) => taskIndex === index ? { ...task, complete: !task.complete } : task));
  };

  return (
    <div className="dashboard-page">
      <section className="welcome-row">
        <div>
          <div className="eyebrow eyebrow-with-dot"><span className="live-dot" /> Monday, 23 September 2026</div>
          <h1>Good morning, {activeSnapshot.student.name}<span className="wave">✦</span></h1>
          <p className="page-subtitle">A little progress today compounds into a lot of confidence later.</p>
        </div>
        <div className="welcome-actions">
          <button className={`exam-mode-toggle ${examMode ? "exam-mode-on" : ""}`} onClick={() => setExamMode((value) => !value)}>
            <span className="toggle-icon"><Icon name="sparkles" size={15} /></span>
            <span><small>Focus mode</small><strong>{examMode ? "Exam mode on" : "Turn on exam mode"}</strong></span>
            <span className={`toggle-track ${examMode ? "toggle-track-on" : ""}`}><span /></span>
          </button>
          <button className="button button-primary button-with-icon"><Icon name="plus" size={16} /> Add a task</button>
        </div>
      </section>

      <section className="attempt-banner">
        <div className="attempt-copy">
          <div className="attempt-kicker"><span className="attempt-status" /> Your current attempt</div>
          <h2>{activeSnapshot.student.level} <span>·</span> Group 1</h2>
          <p>{activeSnapshot.student.attempt} <span className="banner-divider" /> Exam starts in <strong>{activeSnapshot.student.daysLeft} days</strong></p>
        </div>
        <div className="attempt-progress-wrap">
          <div className="progress-ring" style={{ background: "conic-gradient(#c7a8ff 0deg 230deg, rgba(255,255,255,.12) 230deg 360deg)" }}><div><strong>64%</strong><span>covered</span></div></div>
          <button className="banner-link">View syllabus <Icon name="arrow-up-right" size={14} /></button>
        </div>
        <div className="banner-decoration"><span /><span /><span /></div>
      </section>

      <section className="metric-grid" aria-label="Preparation overview">
        {activeSnapshot.metrics.map((metric) => (
          <article className={`metric-card metric-${metric.tone}`} key={metric.label}>
            <div className="metric-top"><span>{metric.label}</span><span className="metric-menu"><Icon name="more-horizontal" size={16} /></span></div>
            <div className="metric-value-row"><strong>{metric.value}</strong>{metric.label === "Preparation score" ? <span className="metric-unit">/100</span> : null}</div>
            <div className="metric-bottom"><span>{metric.detail}</span><span className="metric-trend"><Icon name="arrow-up-right" size={12} /> {metric.trend}</span></div>
          </article>
        ))}
      </section>

      <div className="dashboard-grid">
        <section className="dashboard-card focus-card">
          <div className="card-heading">
            <div><div className="section-kicker"><span className="section-kicker-icon"><Icon name="flame" size={14} /></span> Your focus today</div><h2>Make today count</h2></div>
            <button className="text-button">View plan <Icon name="arrow-right" size={14} /></button>
          </div>
          <div className="task-list">
            {tasks.length ? tasks.map((task, index) => (
              <button className={`task-row ${task.complete ? "task-complete" : ""}`} key={task.title} onClick={() => completeTask(index)}>
                <span className={`task-check ${task.complete ? "task-check-done" : ""}`}>{task.complete ? <Icon name="check" size={13} /> : null}</span>
                <span className="task-type-icon"><Icon name={taskIcon[task.kind]} size={16} /></span>
                <span className="task-copy"><strong>{task.title}</strong><small>{task.subject}</small></span>
                <span className="task-duration"><Icon name="clock-3" size={13} /> {task.duration}</span>
                <Icon name="arrow-right" size={15} />
              </button>
            )) : <div className="dashboard-empty-copy"><Icon name="calendar-days" size={18} /><span><strong>Your plan is ready for your first task.</strong><small>Open Study Planner to add today’s focus block.</small></span></div>}
          </div>
          <button className="add-task-row"><Icon name="plus" size={15} /> Add another task</button>
        </section>

        <section className="dashboard-card syllabus-card">
          <div className="card-heading"><div><div className="section-kicker">Syllabus pulse</div><h2>Keep the balance</h2></div><button className="icon-button"><Icon name="more-horizontal" size={17} /></button></div>
          <div className="subject-list">
            {activeSnapshot.subjects.length ? activeSnapshot.subjects.map((subject) => (
              <div className="subject-row" key={subject.name}>
                <div className={`subject-badge subject-${subject.tone}`}>{subject.shortName}</div>
                <div className="subject-info"><div><strong>{subject.name}</strong><span>{subject.percent}%</span></div><div className="progress-track"><span className={`progress-fill fill-${subject.tone}`} style={{ width: `${subject.percent}%` }} /></div><small>{subject.meta}</small></div>
              </div>
            )) : <div className="dashboard-empty-copy"><Icon name="chart-no-axes-combined" size={18} /><span><strong>Your syllabus pulse will appear here.</strong><small>Complete your first chapter to start tracking progress.</small></span></div>}
          </div>
          <button className="outline-button">Open syllabus tracker <Icon name="arrow-up-right" size={14} /></button>
        </section>
      </div>

      <div className="dashboard-grid lower-grid">
        <section className="dashboard-card upcoming-card">
          <div className="card-heading"><div><div className="section-kicker">Coming up</div><h2>Stay one step ahead</h2></div><button className="text-button">See calendar <Icon name="arrow-right" size={14} /></button></div>
          <div className="upcoming-list">
            <div className="upcoming-row"><div className="date-chip date-purple"><strong>28</strong><span>SEP</span></div><div className="upcoming-copy"><strong>Chapter test · Advanced Accounting</strong><span>45 marks <i /> 60 minutes</span></div><span className="upcoming-tag tag-ready">Open</span></div>
            <div className="upcoming-row"><div className="date-chip date-peach"><strong>02</strong><span>OCT</span></div><div className="upcoming-copy"><strong>Revision 2 · Partnership accounts</strong><span>Advanced Accounting <i /> 30 min</span></div><span className="upcoming-tag tag-revision">Revision</span></div>
            <div className="upcoming-row"><div className="date-chip date-blue"><strong>05</strong><span>OCT</span></div><div className="upcoming-copy"><strong>Faculty live session · Company Law</strong><span>7:00 PM <i /> Online</span></div><span className="upcoming-tag tag-live">Live</span></div>
          </div>
        </section>

        <section className="dashboard-card activity-card">
          <div className="card-heading"><div><div className="section-kicker">Your rhythm</div><h2>Study consistency</h2></div><span className="streak-pill"><Icon name="flame" size={14} /> 12 day streak</span></div>
          <div className="activity-visual"><div className="activity-total"><strong>18.5</strong><span>hours this week</span></div><div className="bar-chart" aria-label="Study hours by day"><span style={{ height: "42%" }} /><span style={{ height: "68%" }} /><span style={{ height: "54%" }} /><span style={{ height: "82%" }} /><span style={{ height: "61%" }} /><span style={{ height: "92%" }} /><span className="bar-today" style={{ height: "36%" }} /></div></div>
          <div className="chart-labels"><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span></div>
          <div className="activity-foot"><span><i className="legend-dot legend-purple" /> Planned <strong>22h</strong></span><span><i className="legend-dot legend-gray" /> Completed <strong>18.5h</strong></span></div>
        </section>
      </div>

      <section className="insight-strip"><div className="insight-icon"><Icon name="sparkles" size={18} /></div><div><span className="section-kicker">A nudge from your data</span><strong>Your Taxation progress dipped this week.</strong><p>Try a 20-minute MCQ sprint after tomorrow’s revision to rebuild momentum.</p></div><button className="button button-soft">Start a sprint <Icon name="arrow-right" size={14} /></button></section>
    </div>
  );
}
