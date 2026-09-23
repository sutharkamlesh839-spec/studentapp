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
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
- **Workspace routes:** student, faculty and admin navigation routes are active with real interactions; remaining domains are not described as production-complete until their persistence APIs and tests are implemented.
- **Next:** extend the same verified vertical-slice pattern to MCQ, tests, evaluation, queries and notifications.
