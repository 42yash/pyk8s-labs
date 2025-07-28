# backend/tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from main import app
from db import get_db
from models.base import Base

# --- Test Database Setup ---
# Use an environment variable for the test database URL, falling back to a default
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://user:password@localhost:5433/pyk8s_db_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_test_database():
    """
    Fixture to set up the test database once per session.
    It creates all tables and cleans them up after tests are done.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(setup_test_database):
    """
    Fixture to provide a database session for each test.
    It creates a new session and rolls back any changes after the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """
    Fixture to provide a TestClient for the FastAPI app.
    It overrides the `get_db` dependency to use the isolated test database session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Clean up the override after the test
    del app.dependency_overrides[get_db]
