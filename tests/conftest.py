import os
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session


os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://localhost:5432/test")


@pytest.fixture
def db_session() -> Mock:
    return Mock(spec=Session)
