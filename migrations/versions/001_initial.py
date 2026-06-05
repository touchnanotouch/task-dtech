import sqlalchemy as sa
import bcrypt as _bcrypt

from decimal import Decimal

from alembic import op


revision = "001"

down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users --------------------------------------------------------------------

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column(
            "is_admin", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # accounts -----------------------------------------------------------------

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "balance", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # payments -----------------------------------------------------------------

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transaction_id", sa.String(255), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_payments_user_id", "payments", ["user_id"])

    # seed data ----------------------------------------------------------------

    user_pw = _bcrypt.hashpw(b"user123", _bcrypt.gensalt()).decode()
    admin_pw = _bcrypt.hashpw(b"admin123", _bcrypt.gensalt()).decode()

    op.execute(
        sa.text(
            "INSERT INTO users (email, password_hash, full_name, is_admin) "
            "VALUES (:email, :pw, :name, :admin)"
        ).bindparams(email="user@test.com", pw=user_pw, name="Test User", admin=False)
    )

    op.execute(
        sa.text(
            "INSERT INTO users (email, password_hash, full_name, is_admin) "
            "VALUES (:email, :pw, :name, :admin)"
        ).bindparams(email="admin@test.com", pw=admin_pw, name="Test Admin", admin=True)
    )

    op.execute(
        sa.text(
            "INSERT INTO accounts (user_id, balance) "
            "SELECT id, :balance FROM users WHERE email = :email"
        ).bindparams(balance=Decimal("1000.00"), email="user@test.com")
    )


def downgrade() -> None:
    op.drop_index("ix_payments_user_id")
    op.drop_table("payments")
    op.drop_table("accounts")
    op.drop_table("users")
