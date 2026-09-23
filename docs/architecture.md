# CA Student OS — product and technical architecture

**Status:** Phase 0 foundation approved for implementation
**Decision:** Start as a modular monolith with strict domain boundaries. Split high-load workers and search only when measured demand justifies it.

## 1. Final product architecture

CA Student OS is a role-aware learning, preparation and career platform. The system is organized into these bounded contexts:

- **Identity & access:** registration, verification, sessions, roles, permissions, audit events.
- **Academic catalog:** levels, groups, subjects, modules, chapters, topics, attempts.
- **Content:** authorized ICAI resources, notes, PDFs, videos, RTP/MTP/PYQ and announcements.
- **Practice:** MCQs, attempts, wrong-answer book, tests and answer keys.
- **Preparation:** syllabus state, revisions, study plans, timetable and exam mode.
- **Evaluation:** answer-sheet submission, page assets, faculty marking and feedback.
- **Engagement:** queries, notifications, saved library, activity and streaks.
- **Insight:** past-paper analysis, student preparation score and admin/faculty analytics.
- **Career:** articleship opportunities, applications, resume and career roadmaps.
- **AI assistance:** source-grounded explanations, recommendations and study planning.

The initial deployment is a web application plus an API. Background jobs handle email, notification fan-out, document processing, analytics rollups and AI ingestion. Every domain owns its service/repository layer and exposes versioned REST endpoints rather than reaching across another domain's tables directly.

## 2. Complete module map

| Domain | Phase 0–1 | Later capabilities |
|---|---|---|
| Identity | Registration, login, refresh, logout, RBAC, sessions | Email verification, password reset, MFA, SSO |
| Student home | Dashboard shell, profile, prioritized next action | Personalization, exam mode, streaks |
| Resources | Catalog, metadata, save/progress contracts | Upload pipeline, versioning, downloads, sharing |
| RTP/MTP/PYQ | Resource type and attempt taxonomy | Comparison and paper analysis |
| Video | Video metadata and progress contract | Embeds, watch-later and completion analytics |
| MCQ | Question taxonomy and attempt contracts | Timer, modes, explanations, wrong-answer book |
| Tests | Test and assignment contracts | Exam runner, descriptive and objective evaluation |
| Evaluation | Submission/evaluation schema | PDF/image viewer, question-wise marking |
| Preparation | Syllabus, revision, study-task contracts | Spaced repetition and planner generation |
| Queries | Ticket lifecycle and assignment contracts | Attachments, SLA analytics, ratings |
| Search | Unified API contract | Postgres FTS, typo tolerance, Meilisearch adapter |
| Faculty | Assigned-scope access model | Content authoring and cohort analytics |
| Admin | Operations shell, audit model | Bulk imports, reports and settings |
| Notifications | Preferences and in-app event model | Email/push/WhatsApp adapters |
| AI | Provider abstraction and source policy | Retrieval, PDF Q&A and recommendations |
| Career | Opportunity/application taxonomy | Firm portal, resume builder and interview prep |
| Community | Moderation-ready entities only | Opt-in, moderated discussions and groups |

## 3. Roles and permissions matrix

Authorization is permission-based in the API. Roles are permission bundles and can be changed by an authorized admin; a UI hiding a button is never considered authorization.

| Capability | Student | Faculty | Admin | Super Admin |
|---|:---:|:---:|:---:|:---:|
| Own profile, sessions and preferences | Own | Own | Own | Own |
| Read assigned academic content | Yes | Yes | Yes | Yes |
| Create/edit own study tasks and progress | Yes | No | Support | Support |
| Attempt MCQs/tests assigned to self | Yes | Preview | Support | Support |
| Submit answer sheet | Yes | No | Support | Support |
| Evaluate assigned submissions | No | Scoped | Yes | Yes |
| Answer assigned queries | No | Scoped | Yes | Yes |
| Publish resources, MCQs or tests | No | If granted | Yes | Yes |
| Manage students/faculty | No | No | Yes | Yes |
| Manage roles and permissions | No | No | No | Yes |
| Manage system settings and providers | No | No | No | Yes |
| Read audit logs | No | No | Scoped | Full |
| Export reports | Own | Scoped | Yes | Yes |

**Permission naming:** `resource.read`, `resource.publish`, `mcq.attempt`, `test.evaluate`, `query.assign`, `user.manage`, `role.manage`, `audit.read`, etc. Scope filters are enforced in repositories for level, group, subject, batch and assignment.

## 4. Application sitemap

### Public
`/` (marketing/entry) · `/login` · `/register` · `/forgot-password` · `/verify-email` · `/terms` · `/privacy`

### Student
`/dashboard` · `/resources` · `/resources/[id]` · `/videos` · `/mcq` · `/mcq/session/[id]` · `/tests` · `/tests/[id]` · `/syllabus` · `/planner` · `/revision` · `/timetable` · `/past-papers` · `/library` · `/queries` · `/ai` · `/articleship` · `/career` · `/icai-updates` · `/notifications` · `/profile`

### Faculty
`/faculty` · `/faculty/students` · `/faculty/papers` · `/faculty/evaluations/[id]` · `/faculty/tests` · `/faculty/queries` · `/faculty/resources` · `/faculty/mcqs` · `/faculty/videos` · `/faculty/analytics` · `/faculty/profile`

### Admin
`/admin` · `/admin/students` · `/admin/faculty` · `/admin/resources` · `/admin/mcqs` · `/admin/tests` · `/admin/evaluations` · `/admin/queries` · `/admin/timetable` · `/admin/announcements` · `/admin/icai-updates` · `/admin/analytics` · `/admin/notifications` · `/admin/permissions` · `/admin/audit-logs` · `/admin/settings`

## 5. Recommended technology architecture

- **Web:** Next.js App Router, React, TypeScript strict mode, server components by default, client components only for interaction, CSS tokens with accessible responsive primitives.
- **API:** FastAPI, Pydantic v2, SQLAlchemy 2 async, Alembic, service/repository separation.
- **Data:** PostgreSQL 16 as the source of truth, Redis for cache/queues/rate limits, S3-compatible object storage for private files.
- **Workers:** Celery or Dramatiq backed by Redis for email, thumbnails, OCR, analytics and AI ingestion.
- **Search:** PostgreSQL `tsvector` and trigram indexes for MVP; an adapter boundary permits Meilisearch/OpenSearch later.
- **Observability:** structured JSON logs, request IDs, OpenTelemetry traces, metrics and error tracking.
- **Delivery:** Docker images, CI checks (typecheck, lint, unit, API integration, migration check), managed Postgres/Redis/object storage in production.

## 6. Backend architecture

```text
HTTP route -> auth/permission dependency -> application service -> repository -> SQLAlchemy model
                                      \-> domain event -> background worker / notification
```

Routes own HTTP concerns and status codes. Services own business rules and transactions. Repositories own query composition and pagination. Schemas are never ORM models exposed directly. Cross-cutting concerns live in `core/`: configuration, security, logging, errors, storage and rate limiting. Transactions use an explicit unit-of-work boundary; audit events are emitted in the same transaction for sensitive mutations.

## 7. Frontend architecture

- App Router route groups separate public, student, faculty and admin experiences.
- A shared `AppShell` owns responsive navigation, command actions and session-aware chrome.
- Feature folders own API hooks, schemas, tables, empty states and loading states.
- Server-rendered data is preferred; mutations use typed API clients and invalidate the relevant cache.
- Access is optimistic in navigation only; the API remains authoritative and redirects on `401/403`.
- Design tokens cover surface, text, border, brand, success, warning and danger states. Focus rings and minimum touch targets are first-class.

## 8. Database entity map

```text
users --< user_roles >-- roles --< role_permissions >-- permissions
  |                         |
  +-- student_profiles       +-- faculty_profiles
  +-- sessions / refresh_tokens / notifications / audit_logs

levels --< groups --< subjects --< modules --< chapters --< topics
                                      |
                                      +-- resources / videos / mcq_questions / tests

users --< resource_bookmarks / resource_progress / mcq_attempts / test_attempts
users --< syllabus_progress / study_plans --< study_tasks / revision_schedule
users --< queries --< query_replies
users --< paper_submissions --< evaluations --< evaluation_marks
```

All user-owned rows carry `user_id`; all academic rows carry the smallest useful catalog foreign keys for filtering. Files are references to storage keys, not blobs in Postgres.

## 9. Full PostgreSQL schema plan

### Identity and governance

- `users`: UUID PK, normalized email unique, password hash, full name, mobile, status, email verified timestamp, last login, created/updated/deleted timestamps.
- `roles`: UUID PK, unique code, display name, system flag.
- `permissions`: UUID PK, unique code, description.
- `user_roles`: `(user_id, role_id)` unique, assigned by, timestamps.
- `role_permissions`: `(role_id, permission_id)` unique.
- `student_profiles`: user FK, ICAI registration number (nullable), level/group/attempt/city/state/branch, DOB, avatar key, preferences JSONB.
- `faculty_profiles`: user FK, bio, designation, subjects/levels through assignment tables, active status.
- `faculty_scopes`: faculty FK plus level/group/subject/batch nullable dimensions.
- `sessions`: UUID PK, user FK, device metadata, IP hash, expires/revoked timestamps.
- `refresh_tokens`: UUID PK, session FK, token hash unique, rotated/revoked timestamps.
- `audit_logs`: UUID PK, actor FK, action, resource type/id, before/after JSONB, request ID, IP hash, created timestamp; indexes on actor, resource and created time.

### Academic catalog and content

- `levels`, `groups`, `subjects`, `modules`, `chapters`, `topics`: stable slugs, display order, active flags, unique parent/name constraints.
- `attempts`: level/group/year/month/label with unique natural key and applicability dates.
- `resource_types`: code and policy flags (`download_allowed`, `official`).
- `resources`: metadata, catalog FKs, attempt FK, source, storage key or URL, checksum, publishing status, author, active window and search vector.
- `resource_bookmarks`, `resource_progress`: user/resource unique pair, completion and last viewed metadata.
- `videos`, `video_progress`: URL/provider, faculty/channel, duration, attempt applicability and watch state.
- `announcements`, `icai_updates`: audience targeting JSONB plus explicit indexed audience relations; official URL required for ICAI updates.

### Practice and evaluation

- `mcq_questions`, `mcq_options`: immutable question versioning, correct option stored server-side, explanation, difficulty, marks, negative marks, source and catalog FKs.
- `mcq_attempts`, `mcq_responses`, `mcq_bookmarks`, `wrong_answer_book`: session metadata, answer timing and improvement counters.
- `tests`, `test_questions`, `test_assignments`, `test_attempts`: lifecycle, duration, evaluation mode, assignment scope, attempt limits and results.
- `paper_submissions`, `submission_pages`, `evaluations`, `evaluation_marks`, `faculty_feedback`: private storage keys, checksums, virus-scan status, immutable submitted marks and versioned feedback.
- `past_papers`, `past_paper_questions`, `past_paper_analysis`: source-attributed question mapping and aggregate facts; analysis is explicitly descriptive, never predictive.

### Planning and engagement

- `syllabus_progress`: user/chapter unique, status, percent, source (`manual`/`activity`), updated by.
- `revision_schedule`, `revision_history`: algorithm version, due dates, completed timestamps and snooze history.
- `study_plans`, `study_tasks`: plan window, daily hours, generated/manual source, task status and reschedule history.
- `timetables`, `timetable_entries`: audience scope, start/end, type, room/link and cancellation state.
- `queries`, `query_assignments`, `query_replies`, `query_ratings`: lifecycle, SLA timestamps, private attachments and reopen history.
- `notifications`, `notification_preferences`, `notification_deliveries`: channel, template, payload, read/delivery state and dedupe key.
- `articleship_opportunities`, `student_applications`, `career_guides`, `saved_opportunities`: normalized listing and application states.

### Database rules

Use UUIDs, UTC `timestamptz`, server-side timestamps, foreign keys with deliberate `RESTRICT`/`CASCADE` behavior, soft deletion for user-generated/content records, and check constraints for percentages, marks and status enums. Add composite indexes for the dominant filters: `(level_id, group_id, subject_id, active)`, `(user_id, status, due_at)`, `(faculty_id, status)`, and `(created_at DESC)`. Use partial indexes for active/published rows and GIN indexes for JSONB/FTS.

## 10. API module map

All endpoints are under `/api/v1`, return an envelope for lists (`items`, `page`, `page_size`, `total`), validate with Pydantic and use cursor pagination for high-volume feeds.

- `/auth`: register, login, refresh, logout, verify email, password reset, sessions, me.
- `/students`: own profile, progress, activity, library.
- `/faculty`: scoped students, evaluations, queries, authored content and analytics.
- `/admin`: CRUD and bulk operations for users, faculty, content, tests, settings and reports.
- `/resources`, `/videos`, `/mcq`, `/tests`, `/evaluations`, `/queries`, `/timetable`, `/progress`, `/study-plan`, `/revision`, `/notifications`, `/search`, `/analytics`, `/icai-updates`, `/career`.

Each mutation documents `401`, `403`, `404`, `409`, `422` and `429` behavior. Upload endpoints issue short-lived presigned URLs and finalize only after MIME, size, checksum and malware checks pass.

## 11. Authentication architecture

Password hashes use Argon2id via `pwdlib`. Access JWTs are short-lived (15 minutes by default) and contain only `sub`, `session_id`, `roles`, `permissions_version`, `iat` and `exp`. Refresh tokens are opaque, hashed at rest, single-use and rotated; reuse revokes the session family. Prefer an HttpOnly, Secure, SameSite cookie for refresh and an in-memory access token in the web client. Logout revokes the server-side session. Email verification and reset tokens are one-time, hashed and time limited. Account status and permission checks run on every protected API request.

## 12. File storage architecture

`StorageService` exposes `put`, `presign_get`, `presign_put`, `delete` and `head`. The local adapter writes outside the web root for development; the S3/R2 adapter uses private buckets, object tags and server-side encryption in production. Postgres stores only object key, owner, content type, size, checksum, scan status and retention metadata. Downloads require an authorization check and short-lived signed URL. Answer sheets and profile images use separate prefixes and access policies.

## 13. Search architecture

The unified search endpoint accepts query, entity filters, level/group/subject, attempt and cursor. MVP uses normalized text plus Postgres `websearch_to_tsquery`, weighted `tsvector` fields and `pg_trgm` for typo tolerance. Results return category, title, snippet, score, URL and permission-safe metadata. Search is always scoped to published/active rows and the requesting user's visibility. A `SearchProvider` interface allows moving indexing to Meilisearch/OpenSearch without changing frontend contracts.

## 14. Notification architecture

Domain events such as `test.published`, `evaluation.completed`, `query.answered`, `revision.due` and `announcement.published` are placed on a durable queue. A preference service resolves audience and channels, deduplicates by event/user/channel, then dispatches in-app immediately and email/push asynchronously. Delivery attempts, provider IDs and failures are stored. Quiet hours, unsubscribe rules and transactional-message exceptions are enforced centrally.

## 15. AI architecture

AI is an optional provider behind `AIProvider`: OpenAI-compatible, local or future vendor adapters. Retrieval only supplies authorized, attributed chunks from published resources. Prompts require citation metadata and label every answer as AI-generated. Official rules, tax limits and exam policy are never treated as facts without a cited primary source; low-confidence or uncited answers ask the learner to verify ICAI. Uploaded PDFs are virus scanned, OCR'd in a worker, chunked with source/page metadata and access-filtered. Store prompt/response audit metadata, redact sensitive fields, apply token/cost limits and let users delete AI history.

## 16. Security architecture

- Backend RBAC plus row/scope checks; deny by default.
- Argon2id passwords, short access TTL, refresh rotation/revocation, secure cookies.
- Pydantic validation, parameterized ORM queries, escaped rendering, CSP, HSTS, secure headers and strict CORS allowlist.
- CSRF token for cookie-authenticated state changes; SameSite cookies and origin checks.
- Rate limits for auth, search, AI, uploads and expensive reports using Redis.
- Upload allowlist, byte/file-size limits, magic-byte MIME checks, antivirus quarantine and private storage.
- Structured audit logs for privileged and sensitive actions; never log passwords, tokens or full answer sheets.
- Secrets only from environment/secret manager; separate keys per environment.
- Backups encrypted, restore tested, retention documented; dependency and container scans in CI.

## 17. Suggested folder structure

```text
studentapp/
├─ apps/web/                         # Next.js web client
│  ├─ app/                           # route groups and layouts
│  ├─ components/                    # cross-feature UI
│  ├─ features/                      # domain UI modules (Phase 1+)
│  ├─ lib/                           # API client, auth, config
│  └─ public/
├─ services/api/                     # FastAPI service
│  ├─ app/api/v1/endpoints/
│  ├─ app/core/                      # settings/security/errors
│  ├─ app/db/                        # engine, Base, migrations hooks
│  ├─ app/models/                    # SQLAlchemy models
│  ├─ app/schemas/                   # Pydantic DTOs
│  ├─ app/repositories/
│  ├─ app/services/
│  ├─ app/tasks/
│  ├─ alembic/
│  └─ tests/
├─ docs/
├─ infra/                            # compose, deployment, observability
└─ scripts/
```

## 18. Phase-wise roadmap

1. **Phase 0 — foundation:** architecture docs, repository layout, config, database Base/models/migration, auth/session/RBAC, audit model, health/API contract, responsive shell and design system.
2. **Phase 1 — learning library:** catalog/resources/videos, authorized ingestion, RTP/MTP/PYQ filters, bookmarks/progress, global search.
3. **Phase 2 — practice:** MCQ authoring/import, runner, timing, explanations, wrong-answer book and analytics.
4. **Phase 3 — preparation:** syllabus, revision algorithm, planner, timetable, adherence and reminders.
5. **Phase 4 — evaluation:** test series, assignments, secure uploads, faculty marking, student results.
6. **Phase 5 — operations:** query workflow, faculty portal, admin CRUD, announcements, ICAI updates.
7. **Phase 6 — insights:** past-paper facts, preparation score with transparent breakdown, student/faculty/admin analytics.
8. **Phase 7 — AI zone:** source-grounded AI assistant, document Q&A, recommendations and guardrails.
9. **Phase 8 — career:** articleship listings, applications, resume and career guides; moderated community foundation.
10. **Phase 9 — scale:** Expo mobile client, push, advanced search/analytics, performance tuning and measured service extraction.

## 19. MVP feature list

The first usable release includes account creation/login/logout, profile and role enforcement; a real student dashboard shell; academic taxonomy; authorized resources with metadata and bookmarks; responsive search; MCQ practice with explanations and mistakes; syllabus/revision basics; test assignment and result view; query tickets; in-app notifications; faculty scoped work queue; admin content/user operations; audit logs; secure file upload flow; and operational telemetry.

## 20. Production feature list

Production adds verified identity/recovery/MFA, full content and video library, all test/evaluation flows, spaced revision and plan generation, analytics and score explanations, source-grounded AI, articleship/career, push/email providers, moderation, mobile app, backups/DR, SLOs, accessibility audit, privacy/retention controls, load testing, feature flags, billing if introduced, and a documented incident response process.

## Exact implementation sequence

1. Freeze domain vocabulary and permission codes; keep this document as the architecture baseline.
2. Bootstrap web/API packages and environment templates; add health checks and CI checks.
3. Add one SQLAlchemy `Base`, core identity/RBAC/session/audit models, import all models in one registry.
4. Create and run the initial Alembic migration against a disposable PostgreSQL database; verify upgrade/downgrade.
5. Implement auth service and endpoint tests: registration, login, refresh rotation, logout, role/permission checks.
6. Build the shared web shell and design tokens; connect login state to API and make `401/403` states explicit.
7. Add Phase 1 domain tables/endpoints and integration tests before building feature screens.
8. Implement one vertical slice at a time (resource list → details → bookmark/progress → search) and verify it end to end.
9. Complete each roadmap phase with unit, API integration, accessibility and responsive checks before starting the next.
10. Before production: run migration checks, dependency scans, load tests, backup restore, security review and a staged rollout.

## Phase 0 acceptance checklist

- [x] Architecture and implementation sequence documented.
- [x] Single SQLAlchemy metadata registry and migration entry point created.
- [x] Environment variables documented without secrets.
- [x] JWT access + rotating refresh token service implemented.
- [x] Configurable roles/permissions with backend dependency hooks implemented.
- [x] Audit/session data model included.
- [x] Responsive base UI and role-aware navigation scaffolded.
- [ ] PostgreSQL/Redis-backed integration run in CI (next verification step).
- [ ] Email verification, password recovery and MFA (Phase 0.1/production hardening).
- [ ] Feature modules connected in Phases 1–9.
