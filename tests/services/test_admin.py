from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.core import (
    CannotDeleteLastAdmin,
    EmailAlreadyExists,
    UserNotFound,
)
from app.services import AdminService


class TestCreateUser:
    async def test_success(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        user_repo.get_by_email.return_value = None
        user_repo.create.return_value = make_user(
            id=2, email="new@test.com", full_name="New User", is_admin=False
        )

        svc = AdminService(user_repo, account_repo, password_provider)
        result = await svc.create_user(
            email="new@test.com", password="secret123", full_name="New User"
        )

        assert result == {
            "id": 2,
            "email": "new@test.com",
            "full_name": "New User",
            "is_admin": False,
        }
        mock_get_session.commit.assert_called_once()

    async def test_email_already_exists(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        user_repo.get_by_email.return_value = make_user()

        svc = AdminService(user_repo, account_repo, password_provider)
        with pytest.raises(EmailAlreadyExists):
            await svc.create_user(
                email="existing@test.com", password="secret123", full_name="Dupe"
            )


class TestUpdateUser:
    async def test_update_email(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        existing = make_user(email="old@test.com")
        user_repo.get_by_email.return_value = None
        user_repo.update.return_value = make_user(id=1, email="new@test.com", full_name="Updated")

        svc = AdminService(user_repo, account_repo, password_provider)
        result = await svc.update_user(1, email="new@test.com")

        assert result["email"] == "new@test.com"
        mock_get_session.commit.assert_called_once()

    async def test_update_not_found(self, mock_get_session, user_repo, account_repo, password_provider):
        user_repo.get_by_email.return_value = None
        user_repo.update.return_value = None

        svc = AdminService(user_repo, account_repo, password_provider)
        with pytest.raises(UserNotFound):
            await svc.update_user(999, email="nobody@test.com")

    async def test_email_conflict_with_another_user(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        user_repo.get_by_email.return_value = make_user(id=5)

        svc = AdminService(user_repo, account_repo, password_provider)
        with pytest.raises(EmailAlreadyExists):
            await svc.update_user(1, email="taken@test.com")


class TestDeleteUser:
    async def test_success(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        user_repo.count_admins.return_value = 2
        user_repo.get_by_id.return_value = make_user(is_admin=True)
        user_repo.delete.return_value = True

        svc = AdminService(user_repo, account_repo, password_provider)
        await svc.delete_user(1)

        mock_get_session.commit.assert_called_once()

    async def test_not_found(self, mock_get_session, user_repo, account_repo, password_provider):
        user_repo.count_admins.return_value = 2
        user_repo.get_by_id.return_value = None

        svc = AdminService(user_repo, account_repo, password_provider)
        with pytest.raises(UserNotFound):
            await svc.delete_user(999)

    async def test_last_admin_blocked(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        user_repo.count_admins.return_value = 1
        user_repo.get_by_id.return_value = make_user(is_admin=True)

        svc = AdminService(user_repo, account_repo, password_provider)
        with pytest.raises(CannotDeleteLastAdmin):
            await svc.delete_user(1)


class TestGetUser:
    async def test_found(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        user_repo.get_by_id.return_value = make_user()

        svc = AdminService(user_repo, account_repo, password_provider)
        result = await svc.get_user(1)

        assert result == {
            "id": 1,
            "email": "test@test.com",
            "full_name": "Test User",
            "is_admin": False,
        }

    async def test_not_found(self, mock_get_session, user_repo, account_repo, password_provider):
        user_repo.get_by_id.return_value = None

        svc = AdminService(user_repo, account_repo, password_provider)
        with pytest.raises(UserNotFound):
            await svc.get_user(999)


class TestListUsers:
    async def test_paginated(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        users = [make_user(id=1, email="a@t.com"), make_user(id=2, email="b@t.com")]
        user_repo.list_all.return_value = (users, 2)

        svc = AdminService(user_repo, account_repo, password_provider)
        result = await svc.list_users(page=1, per_page=10)

        assert result["data"] == [
            {"id": 1, "email": "a@t.com", "full_name": "Test User", "is_admin": False},
            {"id": 2, "email": "b@t.com", "full_name": "Test User", "is_admin": False},
        ]
        assert result["pagination"] == {"page": 1, "per_page": 10, "total": 2}

    async def test_empty(self, mock_get_session, user_repo, account_repo, password_provider):
        user_repo.list_all.return_value = ([], 0)

        svc = AdminService(user_repo, account_repo, password_provider)
        result = await svc.list_users()

        assert result["data"] == []
        assert result["pagination"]["total"] == 0


class TestGetUserAccounts:
    async def test_found(self, mock_get_session, user_repo, account_repo, password_provider, make_user):
        user_repo.get_by_id.return_value = make_user()
        account = MagicMock(spec=["id", "balance", "created_at"])
        account.id = 10
        account.balance = Decimal("500.00")
        account.created_at = datetime(2025, 1, 1, 12, 0, 0)
        account_repo.get_by_user.return_value = [account]

        svc = AdminService(user_repo, account_repo, password_provider)
        result = await svc.get_user_accounts(1)

        assert result == [
            {
                "id": 10,
                "balance": "500.00",
                "created_at": "2025-01-01T12:00:00",
            }
        ]

    async def test_user_not_found(self, mock_get_session, user_repo, account_repo, password_provider):
        user_repo.get_by_id.return_value = None

        svc = AdminService(user_repo, account_repo, password_provider)
        with pytest.raises(UserNotFound):
            await svc.get_user_accounts(999)
