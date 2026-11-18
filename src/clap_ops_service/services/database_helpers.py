from collections.abc import Iterator
from contextlib import contextmanager

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from clap_ops_service.services.exceptions import (
    ConflictError,
    DatabaseOperationError,
)


@contextmanager
def database_operation(
    db: Session,
    operation: str,
    unique_conflict_message: str | None = None,
) -> Iterator[None]:
    try:
        yield
    except IntegrityError as error:
        db.rollback()
        if (
            unique_conflict_message is not None
            and isinstance(error.orig, UniqueViolation)
        ):
            raise ConflictError(unique_conflict_message) from error
        raise DatabaseOperationError(f"Could not {operation}") from error
    except (SQLAlchemyError, OSError) as error:
        db.rollback()
        raise DatabaseOperationError(f"Could not {operation}") from error
