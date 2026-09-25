# CA Student OS deployment guide

This repository now has a deployable container path for the current working vertical slice: authentication, RBAC, resource upload/download, bookmarks/progress, active web workspaces and the responsive product shell.

## 1. Local PowerShell run

Run the web and API from their own directories. The repository root intentionally has no `npm run dev` script.

```powershell
cd C:\Users\SUTHA\Downloads\studentapp\apps\web
npm install
Copy-Item .env.example .env.local -Force
npm run dev
```

In another PowerShell window:

```powershell
cd C:\Users\SUTHA\Downloads\studentapp\services\api
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env -Force
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`apps/web/.env.local` points directly to `http://localhost:8000`. The browser never uses a container-only hostname.

## 2. Create the first administrator

There is deliberately no shared administrator password. Create one locally or in the deployment runtime:

```powershell
cd services\api
.\.venv\Scripts\Activate.ps1
python scripts\create_admin.py
```

The command prompts for an email, name and password. It creates or promotes the account to `super_admin`, hashes the password with Argon2id and never writes the password to the repository.

## 3. Docker Compose production-like run

Docker Desktop is required.

```powershell
cd infra
Copy-Item .env.production.example .env.production -Force
# Edit .env.production and replace every replace-with value.
docker compose --env-file .env.production -f docker-compose.production.yml up --build -d
```

Open:

```text
http://localhost:3000
```

The browser calls relative `/api/v1/...` routes. The Next.js server rewrites them internally to the `api` container. This avoids the common production mistake of calling `localhost` from browser code.

To create an administrator inside the API container:

```powershell
docker compose --env-file .env.production -f docker-compose.production.yml exec api python scripts/create_admin.py
```

To inspect logs:

```powershell
docker compose --env-file .env.production -f docker-compose.production.yml logs -f api web
```

To stop the stack without deleting volumes:

```powershell
docker compose --env-file .env.production -f docker-compose.production.yml down
```

## 4. Production environment variables

Required:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `JWT_SECRET_KEY` — a unique random secret, never a sample value
- `CORS_ORIGINS` — exact public web origin(s), comma-separated

For Cloudflare R2 or AWS S3:

- `STORAGE_DRIVER=s3`
- `S3_ENDPOINT_URL`
- `S3_BUCKET`
- `S3_REGION`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`

When `STORAGE_DRIVER=local`, files live in the API `api-storage` volume. Use S3/R2 for multi-instance production so uploads survive container replacement and are shared across replicas.

## 5. Vercel + managed API deployment

### Frontend

- Root directory: `apps/web`
- Build command: `npm run build`
- Start command: `npm run start`
- `NEXT_PUBLIC_API_BASE_URL`: the public API origin, for example `https://api.example.com`
- `NEXT_PUBLIC_ENABLE_DEMO=false`

If you deploy the web and API behind one origin, leave `NEXT_PUBLIC_API_BASE_URL` empty and set `API_INTERNAL_URL` on the Next server to the private API origin.

### API on Render/Railway/VPS

- Root directory: `services/api`
- Build: `pip install -e .`
- Pre-deploy: `alembic upgrade head`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Use managed PostgreSQL and Redis.
- Set `APP_ENV=production` and all required secrets.
- Persist answer sheets/resources in R2/S3, not the ephemeral container filesystem.

### Managed database

Use a managed PostgreSQL connection string with the async driver:

```text
postgresql+asyncpg://user:password@host:5432/studentos
```

Run migrations exactly once per release job:

```powershell
alembic upgrade head
```

Do not run `Base.metadata.create_all()` in production. Alembic is the source of truth.

## 6. Deployment acceptance checklist

- [ ] Secrets replaced and not committed.
- [ ] `CORS_ORIGINS` matches the public frontend origin exactly.
- [ ] HTTPS is enabled at the edge.
- [ ] PostgreSQL backups and restore test are configured.
- [ ] Redis is private and authenticated where the provider requires it.
- [ ] `STORAGE_DRIVER=s3` is used for more than one API replica.
- [ ] `alembic upgrade head` succeeded.
- [ ] `/api/v1/health` and `/api/v1/health/ready` return success.
- [ ] Admin created with `scripts/create_admin.py`.
- [ ] Login, logout, refresh and session revocation verified.
- [ ] Resource upload, download, bookmark and completion verified.
- [ ] PDF paper upload, admin assignment, faculty-only queue/access, reviewed PDF download, marks/feedback and student notification verified.
- [ ] Web `NEXT_PUBLIC_ENABLE_DEMO=false` verified.
- [ ] Error tracking, structured logs and uptime checks are configured.

## 7. Scope note

A deployment is not the same as feature completeness. The implemented slices are real and persisted, including the PDF paper assignment/review workflow, but production readiness still requires provider-specific verification, operational controls and the remaining roadmap work. No domain is described as production-complete until its API, persistence, authorization and deployment checks pass the same acceptance checklist.
