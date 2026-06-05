from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool


class CreateUserRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=6)
    full_name: str = Field(max_length=255)


class UpdateUserRequest(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=6)
    full_name: str | None = Field(default=None, max_length=255)


class AccountOut(BaseModel):
    id: int
    balance: str
    created_at: datetime


class PaymentOut(BaseModel):
    id: int
    transaction_id: str
    account_id: int
    amount: str
    created_at: datetime


class WebhookPayload(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    signature: str

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")

        return v
