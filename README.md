# DocuForge AI

DocuForge AI is an AI-powered documentation standardisation platform built as a Docker-first monorepo with a FastAPI backend, PostgreSQL database, and React frontend.

## Environment setup

Use the backend virtual environment for local Python development:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The project uses Docker for PostgreSQL and keeps the backend image self-contained; do not copy the host `.venv` into the container.

## Local backend development

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Local backend development connects to PostgreSQL via the published Docker port (for example `localhost:5432`), while containerised services use the `db` hostname on the internal Docker network.

## Local frontend development

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Frontend defaults are served at http://localhost:5173.

## Full stack with Docker Compose

```bash
docker compose up --build
```

This starts:

- PostgreSQL on `localhost:5432`
- FastAPI backend on `http://localhost:8000`
- React frontend on `http://localhost:5173`

The backend waits for the database health check before continuing startup, and the default admin user is created by the seed process.

## Default credentials

The system auto-seeds an administrative user on first startup:

- Email: admin@docuforge.ai
- Username: admin
- Password: DocuForgeAdmin2026!

## Database and migrations

The backend includes an Alembic migration history in `backend/alembic/versions` and the app can run migrations with:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. alembic upgrade head
```

For a fresh local reset:

```bash
cd backend
rm -f docuforge_dev.db
source .venv/bin/activate
PYTHONPATH=. alembic upgrade head
```

## Docker-only PostgreSQL

The repository is intentionally configured for Docker-managed PostgreSQL instead of a local server installation. The root `docker-compose.yml` defines the `db` service with a persistent named volume and a health check.

## API

The backend exposes versioned routes under `/api/v1`, including:

- `/api/v1/auth/login`
- `/api/v1/auth/refresh`
- `/api/v1/users`
- `/api/v1/departments`
- `/api/v1/templates`
- `/api/v1/admin/stats`

## Role model

The supported roles are:

- super_admin
- admin
- manager
- developer

This matches the architecture and access matrix in the project documentation.

## Documentation

Detailed technical design and planning documents are in the [`docs/`](docs/) directory:

- [Requirements Specification](docs/REQUIREMENTS.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [API Specification](docs/API_SPECIFICATION.md)
- [Technical Decisions](docs/TECHNICAL_DECISIONS.md)
- [Development Plan](docs/DEVELOPMENT_PLAN.md)
- [Development Progress](docs/DEVELOPMENT_PROGRESS.md)
