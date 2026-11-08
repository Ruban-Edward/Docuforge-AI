#!/bin/sh
set -e

echo "=== DocuForge AI Backend Starting ==="

# Function to wait for database if using postgres
if [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for database at $POSTGRES_HOST:${POSTGRES_PORT:-5432}..."
  python3 - << 'EOF'
import os
import sys
import time
import socket

host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", 5432))
timeout = 60
start_time = time.time()

while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"Database port reachable at {host}:{port}")
            sys.exit(0)
    except OSError:
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for database at {host}:{port}", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
EOF
fi

# Run database migrations
echo "Applying database migrations..."
if [ -f "alembic.ini" ]; then
  alembic upgrade head || {
    echo "Warning: alembic upgrade failed or not yet initialized; proceeding with app startup seeding."
  }
fi

# Run seed script (idempotent: seeds system roles and default admin user)
echo "Running database seeder..."
PYTHONPATH=/app python3 - <<'PY'
import asyncio
from app.database import AsyncSessionLocal
from app.db.seed import seed_system_roles, seed_default_admin

async def main():
    async with AsyncSessionLocal() as db:
        await seed_system_roles(db)
        await seed_default_admin(db)

asyncio.run(main())
PY

echo "Starting FastAPI application server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

