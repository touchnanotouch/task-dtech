from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


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


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int


class PaginatedResponse(BaseModel):
    data: list
    pagination: PaginationMeta


class WebhookPayload(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    signature: str


class WebhookResponse(BaseModel):
    status: str
    payment_id: int
