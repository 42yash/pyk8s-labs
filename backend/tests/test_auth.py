# backend/tests/test_auth.py
import uuid
from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    """Test successful user registration."""
    email = f"testuser_{uuid.uuid4()}@example.com"
    response = client.post(
        "/api/v1/users/register",
        json={"email": email, "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data


def test_register_user_duplicate_email(client: TestClient):
    """Test that registering with a duplicate email fails."""
    email = f"duplicate_{uuid.uuid4()}@example.com"
    # First registration should succeed
    client.post(
        "/api/v1/users/register",
        json={"email": email, "password": "testpassword"},
    )

    # Second registration with the same email should fail
    response = client.post(
        "/api/v1/users/register",
        json={"email": email, "password": "anotherpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success(client: TestClient):
    """Test successful user login."""
    email = f"login_{uuid.uuid4()}@example.com"
    password = "a_secure_password"
    # Create the user first
    client.post(
        "/api/v1/users/register",
        json={"email": email, "password": password},
    )

    # Attempt to log in
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email


def test_login_failure_wrong_password(client: TestClient):
    """Test that login fails with an incorrect password."""
    email = f"login_fail_{uuid.uuid4()}@example.com"
    # Create the user
    client.post(
        "/api/v1/users/register",
        json={"email": email, "password": "correct_password"},
    )

    # Attempt to log in with the wrong password
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
