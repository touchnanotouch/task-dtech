import os

os.environ.setdefault("WEBHOOK_SECRET", "dev-webhook-secret")
os.environ.setdefault("JWT_SECRET", "dev-jwt-secret")

import hashlib

from decimal import Decimal

import psycopg2
import pytest

from app.core import create_app, Settings
from app.core.database import get_session


TEST_DB_NAME = "payment_api_test"


def _create_test_db():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="postgres",
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB_NAME,)
    )
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    cur.close()
    conn.close()


def _run_migrations():
    os.environ["DATABASE_URL"] = (
        f"postgresql+asyncpg://postgres:postgres@localhost:5432/{TEST_DB_NAME}"
    )
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


def _migrate_and_seed():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        dbname=TEST_DB_NAME,
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
    )
    has_table = cur.fetchone()[0]

    if not has_table:
        _run_migrations()
    else:
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        if count == 0:
            _run_migrations()

    cur.close()
    conn.close()


def _truncate_tables():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        dbname=TEST_DB_NAME,
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "TRUNCATE TABLE payments, accounts, users RESTART IDENTITY CASCADE"
    )
    cur.close()
    conn.close()


def _seed_data():
    import bcrypt as _bcrypt

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        dbname=TEST_DB_NAME,
    )
    conn.autocommit = True
    cur = conn.cursor()

    user_pw = _bcrypt.hashpw(b"user123", _bcrypt.gensalt()).decode()
    admin_pw = _bcrypt.hashpw(b"admin123", _bcrypt.gensalt()).decode()

    cur.execute(
        "INSERT INTO users (email, password_hash, full_name, is_admin) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        ("user@test.com", user_pw, "Test User", False),
    )
    user_id = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO users (email, password_hash, full_name, is_admin) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        ("admin@test.com", admin_pw, "Test Admin", True),
    )
    admin_id = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO accounts (user_id, balance) VALUES (%s, %s)",
        (user_id, Decimal("1000.00")),
    )

    cur.close()
    conn.close()

    return user_id, admin_id


@pytest.fixture(scope="session")
def app():
    _create_test_db()
    _migrate_and_seed()

    os.environ["DATABASE_URL"] = (
        f"postgresql+asyncpg://postgres:postgres@localhost:5432/{TEST_DB_NAME}"
    )

    application = create_app()

    yield application

    import asyncio
    try:
        asyncio.run(application.shutdown())
    except AttributeError:
        pass


@pytest.fixture
def test_client(app):
    return app.test_client


@pytest.fixture
def seed():
    _truncate_tables()
    return _seed_data()


@pytest.fixture
def user_token(test_client, seed):
    user_id, _ = seed
    _, resp = test_client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "user123"},
    )
    return resp.json["access_token"]


@pytest.fixture
def admin_token(test_client, seed):
    _, resp = test_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    return resp.json["access_token"]


def webhook_signature(transaction_id, account_id, user_id, amount, secret=None):
    if secret is None:
        secret = os.environ.get("WEBHOOK_SECRET", "dev-webhook-secret")
    keys = sorted(["account_id", "amount", "transaction_id", "user_id"])
    values = {
        "account_id": str(account_id),
        "amount": str(amount),
        "transaction_id": transaction_id,
        "user_id": str(user_id),
    }
    raw = "".join(values[k] for k in keys) + secret
    return hashlib.sha256(raw.encode()).hexdigest()
