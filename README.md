# CA Student OS

A production-oriented foundation for a Chartered Accountancy student operating system for India.

> This repository is being built in vertical, testable phases. Phase 0 establishes the architecture, authentication/RBAC contracts, database metadata, audit/session primitives and the responsive product shell. Content and learning modules are intentionally added in later phases rather than represented as fake production data.

## Repository map

- `apps/web` — Next.js + TypeScript student/faculty/admin web client
- `services/api` — FastAPI + SQLAlchemy + Alembic API
- `docs/architecture.md` — product architecture, schema plan, permissions, roadmap and implementation sequence
- `infra` — deployment/runtime configuration (added with environment integration)

## Run the Phase 0 web shell

```powershell
cd apps/web
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open `http://localhost:3000`. The shell starts in development preview mode when `NEXT_PUBLIC_ENABLE_DEMO=true`; no production API data is written or implied by this fixture. Set it to `false` when running against the API.

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

## Status

- **Phase 0:** foundation scaffold implemented.
- **Next:** run the database migration/integration verification, then start Phase 1 resources and search as documented in `docs/architecture.md`.
