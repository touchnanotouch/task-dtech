class AppError(Exception):
    """Base domain exception."""


class InvalidCredentials(AppError):
    """Wrong email or password."""


class InvalidToken(AppError):
    """Missing, expired or malformed JWT."""


class Forbidden(AppError):
    """Not enough permissions."""


class UserNotFound(AppError):
    """User not found by id."""


class EmailAlreadyExists(AppError):
    """User with this email already exists."""


class CannotDeleteLastAdmin(AppError):
    """Cannot delete the only administrator left."""


class InvalidSignature(AppError):
    """Webhook signature mismatch."""


EXCEPTION_MAP: dict[type[AppError], int] = {
    InvalidCredentials: 401,
    InvalidToken: 401,
    Forbidden: 403,
    UserNotFound: 404,
    EmailAlreadyExists: 409,
    CannotDeleteLastAdmin: 409,
    InvalidSignature: 422,
}
