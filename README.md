# Payment API

Async REST API for payment processing with role-based access, account management, and idempotent webhook handling.

## Tech Stack

- **Language:** Python 3.13
- **Framework:** Sanic 25.12+
- **Database:** PostgreSQL 16 (via SQLAlchemy 2.0 async + asyncpg)
- **Auth:** JWT (PyJWT) + bcrypt
- **Validation:** Pydantic
- **Migrations:** Alembic
- **Infrastructure:** Docker Compose

## Architecture

```
handler -> service -> repository -> PostgreSQL
   |         |            |
  HTTP    business      data
  format   logic        access
```

- **api/** — request parsing, validation, HTTP responses (handlers, schemas, middleware)
- **services/** — business logic, transaction control, use cases
- **repositories/** — data access via SQLAlchemy (flush only, no commit)
- **models/** — SQLAlchemy ORM models
- **core/** — app factory, config (pydantic-settings), DB lifecycle, domain exceptions
- **security/** — JWT encode/decode, password hashing, webhook signature verification

Layer flow: `api -> services -> repositories -> models`

## Quick Start

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Service will be available at `http://localhost:8000`.

### Local development (requires PostgreSQL)

```bash
# Start PostgreSQL via Docker (or use your own instance)
docker compose -f docker/docker-compose.yml up -d db

pip install -e ".[dev]"
alembic upgrade head
sanic app.core.factory:create_app --host=0.0.0.0 --port=8000 --dev
```

## Seed Data

| Email | Password | Role |
|-------|----------|------|
| `user@test.com` | `user123` | Regular user |
| `admin@test.com` | `admin123` | Administrator |

User 1 has an account with balance `1000.00`.

## API

### Auth (public)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | Login, returns JWT Bearer token |
| GET  | `/api/v1/auth/me` | Current user info |

### Admin (requires admin token)

| Method | Path | Description |
|--------|------|-------------|
| GET    | `/api/v1/admin/users/?page=1&per_page=10` | List users (paginated) |
| GET    | `/api/v1/admin/users/<id>` | Get user by ID |
| POST   | `/api/v1/admin/users/` | Create user |
| PATCH  | `/api/v1/admin/users/<id>` | Update user |
| DELETE | `/api/v1/admin/users/<id>` | Delete user |
| GET    | `/api/v1/admin/users/<id>/accounts` | List user's accounts |

### Accounts (requires auth)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/accounts/` | List own accounts with balances |

### Payments (requires auth)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/payments/?page=1&per_page=10` | List own payments (paginated) |

### Webhook (public)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/webhook/` | Process external payment notification |

Payload: `transaction_id`, `account_id`, `user_id`, `amount`, `signature`

Signature: SHA256 of sorted key-value pairs + webhook secret.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `true` | Enable debug logging and SQL echo |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/payment_api` | Async DB connection |
| `JWT_SECRET` | `dev-jwt-secret-key-change-in-production!` | JWT signing key |
| `WEBHOOK_SECRET` | `dev-webhook-secret-key-change-in-production!` | Webhook HMAC key |
| `JWT_EXPIRATION_HOURS` | `24` | Token lifetime (hours) |

Copy `.env.example` to `.env` for local development.

## Tests

```bash
# Ensure DB is running
docker compose -f docker/docker-compose.yml up -d db

# Run all tests
pytest

# Run only unit tests (no DB required)
pytest tests/services/

# Run only integration tests
pytest tests/api/
```
