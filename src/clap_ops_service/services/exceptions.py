class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class ConflictError(Exception):
    """Raised when an operation conflicts with existing data."""


class DatabaseOperationError(Exception):
    """Raised when a database operation cannot be completed."""
