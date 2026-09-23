# CA Student OS — visual product architecture

**Approval gate:** This document is the design and interaction contract for Phase 0. No new feature phase should start until the visual direction, information architecture and acceptance criteria are approved.

**Reference direction:** Premium, calm, editorial SaaS quality inspired by the visual confidence of modern Indian professional-service websites such as ShriCasa. The product identity, copy, layouts, components and assets remain original. No ShriCasa branding, logo, text or copyrighted asset is reused.

## 1. Final visual design system

### Product character

CA Student OS should feel like a serious study companion rather than an education portal: quiet authority from deep navy, warmth from bronze, generous off-white space, strong editorial headings, and focused actions. Motion gives feedback and hierarchy; it never distracts from study.

### Design principles

1. **Focus before density:** one clear primary action per view.
2. **Progress is visible:** every meaningful activity has a state, not just a button.
3. **Authority with warmth:** navy carries trust; bronze marks progress and decisions.
4. **Calm surfaces:** cards, panels and tables use one consistent material language.
5. **Accessible by default:** keyboard, reduced-motion and touch behavior are designed, not patched later.
6. **Original product voice:** concise, supportive and direct; no government-portal phrasing.

### Exact color tokens

| Token | Value | Use |
|---|---|---|
| `--navy-950` | `#0B1126` | deepest hero/sidebar surface, high contrast |
| `--navy-900` | `#111A35` | primary navbar/sidebar background |
| `--navy-800` | `#17213F` | secondary dark surface, hover state |
| `--navy-700` | `#263252` | muted dark controls and dividers |
| `--bronze-700` | `#8F5526` | pressed bronze, dark-on-light contrast |
| `--bronze-600` | `#B87333` | primary accent, key numbers and CTAs |
| `--bronze-500` | `#C98A4E` | hover accent, charts and focus ornaments |
| `--bronze-100` | `#F4E8DA` | bronze tint, soft badges and selected states |
| `--canvas` | `#F7F7F5` | page background |
| `--canvas-warm` | `#FAFAF8` | alternate section background |
| `--surface` | `#FFFFFF` | cards, drawers and forms |
| `--surface-muted` | `#F1F2F0` | skeletons, inactive fields and table headers |
| `--text-900` | `#202838` | primary text |
| `--text-700` | `#465166` | secondary headings and readable metadata |
| `--text-500` | `#667085` | supporting copy |
| `--text-400` | `#98A2B3` | placeholders and low-priority metadata |
| `--border` | `#E5E7EB` | default borders |
| `--border-strong` | `#D0D5DD` | inputs, dividers and table rules |
| `--success` | `#2F8F75` | completed / healthy |
| `--warning` | `#B7791F` | due / attention |
| `--danger` | `#C65D5D` | destructive / failed |
| `--focus` | `#6D5BD0` | keyboard focus ring, never a hidden focus state |

Bronze is an accent, not a fill for every card. Dark navy is reserved for authority surfaces and high-contrast CTAs. Avoid rainbow progress charts; use bronze, navy tints and semantic colors only.

### Typography

- **Primary family:** `Manrope`, fallback `Inter`, then system sans.
- **Reading family:** `DM Sans` for dense data, labels and forms.
- **Display weights:** 700 and 800.
- **Body weights:** 400, 500 and 600.
- **Letter spacing:** display headings from `-0.045em` to `-0.06em`; labels `0.06em` to `0.12em` uppercase.

| Style | Size / line height | Weight | Use |
|---|---:|---:|---|
| Display XL | `clamp(3rem, 6vw, 6.25rem) / .98` | 800 | homepage hero |
| Display L | `clamp(2.25rem, 4vw, 4rem) / 1.02` | 800 | major product section |
| Heading 1 | `2.25rem / 1.1` | 800 | dashboard page heading |
| Heading 2 | `1.5rem / 1.2` | 700 | card groups and sections |
| Heading 3 | `1.125rem / 1.3` | 700 | card title |
| Body L | `1rem / 1.65` | 400 | hero/supporting paragraph |
| Body | `.875rem / 1.55` | 400 / 500 | app body copy |
| Label | `.6875rem / 1.3` | 700 | metadata and controls |
| Micro | `.625rem / 1.3` | 700 | overline, status, table hint |

### Layout, radii and surfaces

- Desktop content max width: `1280px`; marketing hero can use `1360px`.
- Page gutters: `24px` mobile, `40px` tablet, `64px` desktop.
- Base spacing unit: `4px`; common rhythm: `8 / 12 / 16 / 24 / 32 / 48 / 72 / 112px`.
- Card radius: `16px`; inputs/buttons: `10px`; pills: `999px`; large hero panel: `28px`.
- Default card shadow: `0 10px 28px rgba(17, 26, 53, .06)`.
- Hover card shadow: `0 18px 42px rgba(17, 26, 53, .11)`.
- Border-first design: if a surface has a shadow, it still keeps a low-contrast border.
- Use a 12-column grid on desktop, 6 on tablet, 4 on mobile.

### Component style guide

#### Buttons

- Primary: navy fill on light pages, bronze fill only for a high-intent action; white label, `10px` radius.
- Secondary: white/off-white fill, navy text, `1px` border.
- Text action: no background, underline or arrow on hover.
- All buttons have `44px` minimum touch height on mobile.
- Arrow icons move `4px` right on hover; the label never shifts.

#### Cards

- One surface, one border, one interaction model.
- Card hover: `translateY(-3px)`, border shifts toward bronze, shadow deepens.
- No large gradients; use a small bronze rule, icon or number for emphasis.
- Cards must have a useful empty state and a loading skeleton with the same geometry.

#### Inputs and filters

- Height `44px`, `10px` radius, `1px` border.
- Focus uses a `3px` `--focus` ring plus a stronger border.
- Search fields support clear, keyboard focus and empty state.
- Filter chips show selected state with navy text and bronze-tinted background.

#### Tables and data views

- Use compact but readable rows, sticky header only when it improves scanning.
- Mobile tables become stacked cards or a horizontally scrollable region with a visible affordance.
- Every row exposes a keyboard-accessible action menu.
- Never encode status by color alone; pair color with text or an icon.

#### Icons and imagery

- Lucide icons, default stroke `1.75px`, `16–20px` in controls and `24px` in feature cards.
- Use line illustrations, abstract grids or original generated editorial imagery only where it explains a concept.
- No unlicensed ICAI/BOS pages, logos or scraped thumbnails.

## 2. Navbar specification

### Desktop

A two-layer sticky header:

1. **Marketing navbar:** `--navy-900` background, brand left, links centered (`Home`, `Platform`, `Resources`, `MCQ Practice`, `Test Series`, `Community`, `Career`), utilities right (`Search`, theme, notifications, messages, profile).
2. **App navbar:** same navy authority surface, compact breadcrumbs left, global search center/right, notification and profile controls.

- Height: `76px` marketing, `68px` app.
- Default border: `rgba(255,255,255,.12)`.
- On scroll: add `backdrop-filter: blur(16px)`, lower opacity to `.94`, add subtle bottom shadow, animate over `220ms`.
- Active link: rounded `10px` navy-light pill with bronze top/side marker; no persistent underline plus pill at the same time.
- Search opens the command palette, not a dead input.

### Mobile

- `64px` header with brand, search icon, notification bell and menu trigger.
- Full-screen or right-side drawer with accordion sections.
- Drawer traps focus, closes on Escape and restores focus to the trigger.
- Profile and theme controls remain reachable without scrolling to the footer.

## 3. Custom cursor specification

Enabled only for `pointer: fine` and viewport width `>= 900px`; disabled for touch, pen, reduced-motion and keyboard-only sessions.

### Layers

- `.cursor-dot`: 5px navy/bronze dot, immediate position.
- `.cursor-ring`: 34px transparent ring, `1px` bronze/navy border, follows with spring-like lerp at `0.16`.
- `.cursor-label`: optional 10px uppercase text (`VIEW`, `OPEN`, `EXPLORE`) inside a 72px ring on explicit `data-cursor-label` targets only.

### Motion implementation

- Pointer events update a target coordinate.
- One `requestAnimationFrame` loop interpolates dot and ring positions.
- Use CSS transforms only; never cause layout.
- Hover intent adds a `.is-hovering` class after `40ms` and removes it after `80ms` to avoid flicker.
- Cards expand ring to `52px`; buttons become `46px`; label targets use a larger labelled ring.
- `pointerleave` fades the cursor over `160ms`.
- The cursor must never cover focus outlines, block click targets or be the only hover affordance.

## 4. Animation system

### Motion tokens

- Quick feedback: `120ms`, `cubic-bezier(.2,.8,.2,1)`.
- Standard: `220ms`, `cubic-bezier(.22,1,.36,1)`.
- Panels/drawers: `360ms`, `cubic-bezier(.16,1,.3,1)`.
- Page transition: `240ms` opacity + `8px` translate + mild blur.

### Approved patterns

- Section reveal: opacity `0 → 1`, translateY `18px → 0`, once, stagger `45ms`.
- Card hover: translateY `-3px`, scale `1.005` maximum.
- Magnetic CTA: only on desktop fine pointers, max movement `6px`, disabled for reduced motion.
- Count-up statistics: one time on entering viewport; no looping counters.
- Toast: slide from bottom/right, persist until read or `4s`, pause on hover.
- Accordion: animate height/opacity, respect content and focus.
- Route transition: never block navigation on animation; the next page is interactive immediately.
- Skeletons use a low-contrast shimmer only when content is expected within a short interval.

`prefers-reduced-motion: reduce` disables parallax, cursor follower, magnetic behavior, looping motion and translates; opacity or instant state changes remain.

## 5. Public homepage wireframe

```text
┌──────────────────────────────────────────────────────────────────────┐
│ CA OS   Home Platform Resources MCQ Tests Community Career  Search ◐ │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [ MADE FOR CA STUDENTS ]              [ quiet abstract CA study art ]│
│  Your complete CA journey,                                             │
│  simplified in one place.                  [Explore platform]           │
│  Study smarter, practise better...        [Student dashboard →]        │
│                                                                      │
│  40K+ students       3 levels       24/7 support       Built for India │
├──────────────────────────────────────────────────────────────────────┤
│  Tools built for the CA journey                          View all →   │
│  [01 Resources] [02 MCQ practice] [03 Test series] [04 Paper check]  │
│  [05 Past paper] [06 Syllabus] [07 Planner] [08 AI assistant]        │
├──────────────────────────────────────────────────────────────────────┤
│  One workspace for every phase       [resource preview / filter UI]   │
│  Foundation · Intermediate · Final                                    │
├──────────────────────────────────────────────────────────────────────┤
│  Practise with intent                  [MCQ session card]             │
│  Diagnose weak areas, not just marks.                                  │
├──────────────────────────────────────────────────────────────────────┤
│  Tests, checking and feedback          [evaluation workflow]          │
├──────────────────────────────────────────────────────────────────────┤
│  See your syllabus move                [progress / revision visual]   │
├──────────────────────────────────────────────────────────────────────┤
│  Faculty guidance · AI support · Career & articleship · Community      │
├──────────────────────────────────────────────────────────────────────┤
│  Trusted by students building the long game   [testimonial system]    │
├──────────────────────────────────────────────────────────────────────┤
│  Ready for your next focused day?                 [Start your plan]   │
├──────────────────────────────────────────────────────────────────────┤
│ CA OS | Product | Resources | Company | Legal | social | status        │
└──────────────────────────────────────────────────────────────────────┘
```

Hero copy is two-tone: `--text-900` for the first line and `--bronze-600` for the second. The statistics are an API-backed aggregate in production; seeded local values are only development fixtures.

## 6. Student dashboard wireframe

```text
┌──────────────┬───────────────────────────────────────────────────────┐
│ CA OS         │ Search anything              bell   messages   avatar  │
│ Dashboard     ├───────────────────────────────────────────────────────┤
│ Resources     │ Good morning, Aarav              [Focus mode] [+task] │
│ MCQ practice  │ CA Intermediate · Group 1 · 221 days to exam          │
│ Test series   ├───────────────────────────────────────────────────────┤
│ Syllabus      │ [Preparation] [Syllabus] [MCQ accuracy] [Streak]     │
│ Planner       ├──────────────────────────┬────────────────────────────┤
│ Revision      │ Your focus today         │ Syllabus pulse             │
│ Past papers   │ • tasks with check state │ • subject progress          │
│ Videos        │ • duration               │ • revision shortcut         │
│ Library       ├──────────────────────────┼────────────────────────────┤
│ Queries       │ Coming up                │ Your rhythm                 │
│ AI zone       │ tests / revisions / live │ heatmap / hours / streak    │
│ Articleship   ├──────────────────────────┴────────────────────────────┤
│ Career        │ A nudge from your data → next recommended action      │
│ ICAI updates  └───────────────────────────────────────────────────────┘
└──────────────┘
```

Dashboard priority order: due revision, unfinished daily task, upcoming test, weak subject intervention, then discovery content. The preparation score opens a transparent drawer showing syllabus, tests, MCQs, revision and consistency contributions.

## 7. Faculty dashboard wireframe

```text
┌──────────────┬───────────────────────────────────────────────────────┐
│ Faculty OS    │ Search  notifications  profile                        │
│ Overview      ├───────────────────────────────────────────────────────┤
│ Students      │ Good morning, faculty                   [Create test] │
│ Papers        │ assigned subjects · cohorts · SLA status               │
│ Tests         ├───────────────────────────────────────────────────────┤
│ Queries       │ [Pending papers] [Open queries] [Students] [Avg score]│
│ Resources     ├──────────────────────────┬────────────────────────────┤
│ MCQs          │ Evaluation queue          │ Query queue                │
│ Videos        │ student · test · due      │ priority · subject · SLA   │
│ Analytics     ├──────────────────────────┴────────────────────────────┤
│ Profile       │ Assigned cohorts | recent performance | quick actions  │
└──────────────┴───────────────────────────────────────────────────────┘
```

Faculty sees only assigned level/group/subject/batch rows. Evaluation and query queues show SLA, not vanity analytics first.

## 8. Admin dashboard wireframe

```text
┌──────────────┬───────────────────────────────────────────────────────┐
│ Admin OS      │ Global search          system status  avatar            │
│ Overview      ├───────────────────────────────────────────────────────┤
│ Students      │ Operations overview                         [Export]   │
│ Faculty       │ [Students] [Active] [Content] [Papers] [Queries]      │
│ Resources     ├───────────────────────────────────────────────────────┤
│ MCQs          │ Activity trend / resource usage / cohort health       │
│ Tests         ├──────────────────────────┬────────────────────────────┤
│ Evaluations   │ Needs attention           │ Recent activity             │
│ Queries       │ failed uploads, SLA, ... │ audited mutations           │
│ Timetable     ├──────────────────────────┴────────────────────────────┤
│ Announcements │ filtered tables with drawers, bulk actions and audit   │
│ ICAI updates  └───────────────────────────────────────────────────────┘
│ Analytics     │                                                       │
│ Permissions   │                                                       │
│ Audit logs    │                                                       │
│ Settings      │                                                       │
└──────────────┴───────────────────────────────────────────────────────┘
```

Admin UI uses the same tokens, with a dark navy sidebar and warm canvas. Destructive actions require a confirmation dialog and audit event; bulk actions show affected count and scope.

## 9. Complete sitemap

### Public

`/` · `/platform` · `/resources` · `/resources/[id]` · `/mcq` · `/tests` · `/community` · `/career` · `/articleship` · `/login` · `/register` · `/forgot-password` · `/verify-email` · `/terms` · `/privacy`

### Student

`/dashboard` · `/resources` · `/resources/[id]` · `/videos` · `/mcq` · `/mcq/session/[id]` · `/mcq/mistakes` · `/tests` · `/tests/[id]` · `/tests/[id]/attempt/[attemptId]` · `/tests/[id]/result/[attemptId]` · `/evaluations` · `/syllabus` · `/planner` · `/revision` · `/timetable` · `/past-papers` · `/library` · `/queries` · `/notifications` · `/messages` · `/ai` · `/articleship` · `/career` · `/icai-updates` · `/profile` · `/settings`

### Faculty

`/faculty` · `/faculty/students` · `/faculty/papers` · `/faculty/evaluations/[id]` · `/faculty/tests` · `/faculty/queries` · `/faculty/resources` · `/faculty/mcqs` · `/faculty/videos` · `/faculty/analytics` · `/faculty/profile`

### Admin / Super Admin

`/admin` · `/admin/students` · `/admin/faculty` · `/admin/resources` · `/admin/mcqs` · `/admin/tests` · `/admin/evaluations` · `/admin/queries` · `/admin/timetable` · `/admin/announcements` · `/admin/icai-updates` · `/admin/analytics` · `/admin/notifications` · `/admin/permissions` · `/admin/audit-logs` · `/admin/settings`

## 10. Database entity map

```text
identity: users ─< user_roles >─ roles ─< role_permissions >─ permissions
              │                    │
              ├─ student_profiles  ├─ faculty_profiles / faculty_scopes
              ├─ sessions ─< refresh_tokens
              └─ audit_logs / notification_preferences

catalog: levels ─< groups ─< subjects ─< modules ─< chapters ─< topics
                                     │
                                     ├─ attempts
                                     ├─ resources ─< resource_progress / resource_bookmarks
                                     ├─ videos ─< video_progress
                                     ├─ mcq_questions ─< mcq_options
                                     └─ tests ─< test_questions / test_assignments

practice: users ─< mcq_attempts ─< mcq_responses
                    ├─ mcq_bookmarks
                    └─ wrong_answer_book
          users ─< test_attempts

evaluation: users ─< paper_submissions ─< submission_pages
             paper_submissions ─< evaluations ─< evaluation_marks / faculty_feedback

planning: users ─< syllabus_progress
          users ─< study_plans ─< study_tasks
          users ─< revision_schedule ─< revision_history
          timetables ─< timetable_entries

support: users ─< queries ─< query_replies / query_assignments / query_ratings
content: announcements / icai_updates / past_papers ─< past_paper_questions
career: articleship_opportunities ─< student_applications
```

Relational rules: UUID keys, UTC `timestamptz`, soft delete where user/content history matters, explicit scope FKs for level/group/subject/batch, private storage references rather than blobs in Postgres, composite indexes for dominant filters and partial indexes for active rows.

## 11. Backend architecture

```text
FastAPI route
  -> request validation / error boundary
  -> authentication dependency
  -> permission + row-scope dependency
  -> application service / transaction boundary
  -> repository / SQLAlchemy query
  -> domain event
  -> Redis worker (email, notifications, OCR, analytics, AI)
```

Recommended modules:

- `auth`: credential, session and verification flows.
- `identity`: profiles, roles and permission administration.
- `catalog`: academic hierarchy and attempts.
- `content`: resources, videos and upload finalization.
- `practice`: MCQ and test sessions.
- `evaluation`: answer-sheet submission and marking.
- `planning`: syllabus, revision, plans and timetables.
- `support`: queries, replies and ratings.
- `insights`: paper facts, score breakdown and analytics.
- `career`: articleship, applications and roadmaps.
- `notifications`: event routing, preferences and delivery.
- `search`: one permission-aware provider interface.
- `ai`: source retrieval, provider adapters, citations and safety policy.

Routes never call another domain's ORM model directly. Services own business rules; repositories own pagination and filters; schemas are the public contract. Privileged mutations emit audit events in the same transaction.

## 12. Frontend architecture

- Next.js App Router and TypeScript strict mode.
- Server components for page data and SEO; client components only for stateful controls, runners, drawers and animation.
- Route groups: `(marketing)`, `(auth)`, `(student)`, `(faculty)`, `(admin)`.
- Shared `AppShell`, `Navbar`, `CommandPalette`, `CursorSystem`, `ToastProvider`, `ThemeProvider`, `PageTransition` and primitives.
- Feature modules own their API hooks, schemas, loading states, empty states and tests.
- Typed API client handles auth refresh, `401`, `403`, pagination and request IDs.
- TanStack Query may be introduced for client cache invalidation where server actions are insufficient.
- CSS variables are the source of truth for themes; dark mode maps the same semantic tokens rather than replacing every component style.
- `data-cursor-label`, `data-motion` and `data-testid` are standardized attributes.

## 13. Folder structure

```text
studentapp/
├─ apps/web/
│  ├─ app/
│  │  ├─ (marketing)/
│  │  ├─ (auth)/
│  │  ├─ (student)/
│  │  ├─ (faculty)/
│  │  └─ (admin)/
│  ├─ components/
│  │  ├─ ui/                 # buttons, inputs, cards, drawers, tables
│  │  ├─ navigation/         # navbar, sidebar, command palette
│  │  ├─ motion/              # reveals, cursor, transitions
│  │  └─ feedback/            # toast, skeleton, errors, empty states
│  ├─ features/
│  │  ├─ resources/
│  │  ├─ mcq/
│  │  ├─ tests/
│  │  ├─ evaluation/
│  │  ├─ planning/
│  │  ├─ queries/
│  │  ├─ analytics/
│  │  ├─ career/
│  │  └─ ai/
│  ├─ hooks/
│  ├─ lib/                    # API, auth, config, formatters
│  ├─ stores/
│  ├─ types/
│  └─ tests/
├─ services/api/app/
│  ├─ api/v1/endpoints/
│  ├─ auth/
│  ├─ core/
│  ├─ db/
│  ├─ models/
│  ├─ schemas/
│  ├─ repositories/
│  ├─ services/
│  ├─ permissions/
│  ├─ tasks/
│  └─ utils/
├─ infra/
├─ docs/
└─ scripts/
```

The current repository already has a working Phase 0 shell under `apps/web` and a FastAPI foundation under `services/api`; this structure is the target as feature folders are added.

## 14. API structure

All APIs are versioned under `/api/v1` and use a consistent list envelope: `{ items, page, page_size, total }` for offset pagination or `{ items, next_cursor }` for feeds.

```text
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout
GET    /auth/me

GET    /dashboard/summary
GET    /resources
GET    /resources/{id}
POST   /resources/{id}/bookmark
PATCH  /resources/{id}/progress
GET    /videos
GET    /mcq/questions
POST   /mcq/attempts
POST   /mcq/attempts/{id}/responses
GET    /mcq/mistakes
GET    /tests
POST   /tests/{id}/attempts
PATCH  /tests/{id}/attempts/{attempt_id}/answers
POST   /tests/{id}/attempts/{attempt_id}/submit

POST   /evaluations/submissions/presign
POST   /evaluations/submissions/finalize
GET    /evaluations
GET    /evaluations/{id}
PATCH  /evaluations/{id}/marks
POST   /evaluations/{id}/submit

GET    /progress/syllabus
PATCH  /progress/syllabus/{chapter_id}
GET    /revision/due
POST   /revision/{id}/complete
GET    /study-plan
POST   /study-plan/tasks
PATCH  /study-plan/tasks/{id}
GET    /timetable

GET    /queries
POST   /queries
POST   /queries/{id}/replies
PATCH  /queries/{id}/status
GET    /notifications
PATCH  /notifications/{id}/read
GET    /search?q=...
GET    /analytics/preparation-score
GET    /analytics/past-papers
POST   /ai/conversations
POST   /ai/conversations/{id}/messages

# Admin/faculty scope is enforced by permission and row-scope dependencies.
GET    /faculty/students
GET    /faculty/evaluations/queue
POST   /faculty/tests
GET    /admin/metrics
POST   /admin/resources
POST   /admin/mcqs/import
GET    /admin/audit-logs
```

Every mutation defines validation, `401`, `403`, `404`, `409`, `422` and `429` behavior. Uploads use presigned URLs, quarantine and finalize steps. Search results are category-labelled and permission-filtered.

## 15. Phase-wise development roadmap

### Phase 0 — design system and foundation

Design tokens, dark mode, responsive navbar/sidebar, cursor system, motion primitives, base UI, authentication, session rotation, RBAC, audit model, database metadata, Alembic and CI.

**Gate:** keyboard navigation, reduced-motion, touch fallback, auth tests, migration check, responsive review and no dead Phase 0 controls.

### Phase 1 — public homepage, auth, student dashboard and resources

Marketing homepage, real student profile, dashboard API, catalog tables, authorized resource CRUD, browse/details, bookmark/progress and storage abstraction.

### Phase 2 — RTP, MTP, PYQ, videos and search

Attempt taxonomy, video progress, unified search, filters, source attribution and original ICAI links where permitted.

### Phase 3 — MCQ engine

Question import/manual authoring, objective runner, autosave response, timer, explanations, wrong-answer book and analytics.

### Phase 4 — preparation

Syllabus states, configurable spaced-revision algorithm, planner generation, drag/reschedule, timetable and notification events.

### Phase 5 — evaluation

Test series, assignments, private answer-sheet uploads, faculty viewer, marks, feedback, result history and notification delivery.

### Phase 6 — faculty and support

Faculty scope portal, query lifecycle, assignment, SLA, ratings, content authoring and faculty analytics.

### Phase 7 — admin operations

Student/faculty management, content management, bulk imports, announcements, ICAI updates, permissions, reports and audit viewer.

### Phase 8 — insight

Past-paper facts, heatmaps/matrices, preparation score breakdown, cohort analytics and non-predictive trend disclaimer.

### Phase 9 — AI and career

Source-grounded AI zone, citations, PDF Q&A, articleship, resume, applications, career roadmaps and moderated community foundation.

### Phase 10 — production readiness

Security review, load testing, query/index review, accessibility audit, backups/restore, deployment, observability, mobile/push and incident runbooks.

## Approval checklist

- [ ] Palette and typography approved.
- [ ] Homepage wireframe approved.
- [ ] Student, faculty and admin information hierarchy approved.
- [ ] Cursor and reduced-motion behavior approved.
- [ ] Navbar and responsive behavior approved.
- [ ] Sitemap and route ownership approved.
- [ ] API/domain boundaries approved.
- [ ] Phase 0 acceptance tests approved.

After approval, Phase 0 is implemented as a vertical slice and verified before Phase 1 begins. No page is considered complete if its primary action is non-functional or if authorization exists only in the frontend.
