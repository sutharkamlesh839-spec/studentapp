# CA Student OS

A production-oriented foundation for a Chartered Accountancy student operating system for India.

> This repository is being built in vertical, testable phases. Phase 0 establishes the architecture, authentication/RBAC contracts, database metadata, audit/session primitives and the responsive product shell. Content and learning modules are intentionally added in later phases rather than represented as fake production data.

## Repository map

- `apps/web` — Next.js + TypeScript student/faculty/admin web client
- `services/api` — FastAPI + SQLAlchemy + Alembic API
- `docs/architecture.md` — product architecture, schema plan, permissions, roadmap and implementation sequence
- `infra` — deployment/runtime configuration (added with environment integration)

## Run the web app

The repository root intentionally has no `npm run dev` script. Run the frontend from `apps/web`:

```powershell
cd apps/web
npm install
Copy-Item .env.example .env.local -Force
npm run dev
```

Open `http://localhost:3000`. Local `.env.local` uses `http://localhost:8000` for the API. The shell starts in preview mode when `NEXT_PUBLIC_ENABLE_DEMO=true`; set it to `false` when running against the real dashboard API.

## Run the API

```powershell
cd services/api
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API exposes `GET /health` and versioned routes under `/api/v1`. For a real integration run, set `DATABASE_URL` to PostgreSQL and run `alembic upgrade head`; SQLite is available for quick local API checks only.

## Quality commands

```powershell
# Web
cd apps/web
npm run lint
npm run typecheck
npm run build

# API
cd services/api
pytest
alembic check
```

## Deployment

See `docs/deployment.md` for Windows PowerShell, Docker Compose, Vercel, Render/Railway, PostgreSQL, Redis and S3/R2 instructions. A production-like stack is available at `infra/docker-compose.production.yml`.

## Status

- **Foundation:** authentication, refresh sessions, RBAC, audit/session models, responsive shell and protected login gate implemented.
- **Working vertical slice:** resources API, PostgreSQL/SQLite migration, admin upload, private file download, bookmarks and completion progress.
- **Learning vertical slice:** persisted MCQs with answer history and mistakes, syllabus tracking, study planner, revision queue, test publishing/attempts, faculty queries, notifications and analytics APIs are implemented with frontend connections for the student/admin flows.
- **Operations vertical slice:** level-scoped videos, career/articleship opportunities, official updates, PDF answer-sheet submission, admin-to-faculty assignment, faculty-only review queues, protected PDF downloads, annotated PDF review, marks/feedback persistence, student notifications, faculty query replies, admin user lists and audit-log APIs are implemented with protected frontend workspaces.
- **Official ICAI catalogue:** admins can sync a level/subject/chapter-indexed catalogue from the official New Scheme landing page. CA OS stores metadata and redirects to ICAI's official source; it does not mirror copyrighted PDFs.
- **AI:** an optional OpenAI-compatible provider integration is available at `/api/v1/ai/assist`; it remains disabled until the deployment supplies `AI_PROVIDER_URL` and `AI_API_KEY`.
- **Still in progress:** richer admin editing/bulk tools, production provider verification and PostgreSQL/Redis/S3 integration testing are not called complete until exercised on the deployment environment.
