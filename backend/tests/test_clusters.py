# backend/tests/test_clusters.py
import uuid
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


@pytest.fixture
def authenticated_client(client: TestClient) -> TestClient:
    """Fixture to create and log in a user, returning an authenticated client."""
    email = f"authed_user_{uuid.uuid4()}@example.com"
    password = "password123"

    # Register
    client.post("/api/v1/users/register", json={"email": email, "password": password})

    # Login
    response = client.post(
        "/api/v1/auth/token", data={"username": email, "password": password}
    )
    token = response.json()["access_token"]

    client.headers = {"Authorization": f"Bearer {token}"}
    return client


def test_cluster_endpoints_unauthenticated(client: TestClient):
    """Test that unauthenticated requests to cluster endpoints fail."""
    response = client.get("/api/v1/clusters")
    assert response.status_code == 401

    response = client.post("/api/v1/clusters", json={"name": "test", "ttl_hours": 1})
    assert response.status_code == 401


@patch("api.run_cluster_provisioning")  # Mock the background task
def test_create_and_list_cluster(mock_provision_task, authenticated_client: TestClient):
    """Test creating a new cluster and verifying it appears in the list."""
    cluster_name = f"test-cluster-{uuid.uuid4().hex[:6]}"

    # 1. Create a new cluster
    create_response = authenticated_client.post(
        "/api/v1/clusters",
        json={"name": cluster_name, "ttl_hours": 1, "provider": "kind"},
    )
    assert create_response.status_code == 202
    create_data = create_response.json()
    assert create_data["name"] == cluster_name
    assert create_data["status"] == "PROVISIONING"

    # Verify the background task was called
    mock_provision_task.assert_called_once()

    # 2. List clusters
    list_response = authenticated_client.get("/api/v1/clusters")
    assert list_response.status_code == 200
    list_data = list_response.json()

    # Find the cluster we just created in the list
    created_cluster = next((c for c in list_data if c["name"] == cluster_name), None)
    assert created_cluster is not None
    assert created_cluster["status"] == "PROVISIONING"


def test_create_cluster_duplicate_name(authenticated_client: TestClient):
    """Test that creating a cluster with a duplicate name for the same user fails."""
    cluster_name = f"duplicate-cluster-{uuid.uuid4().hex[:6]}"

    # Create the first cluster (should succeed)
    with patch("api.run_cluster_provisioning"):
        response1 = authenticated_client.post(
            "/api/v1/clusters",
            json={"name": cluster_name, "ttl_hours": 1, "provider": "kind"},
        )
        assert response1.status_code == 202

    # Attempt to create a second cluster with the same name (should fail)
    with patch("api.run_cluster_provisioning"):
        response2 = authenticated_client.post(
            "/api/v1/clusters",
            json={"name": cluster_name, "ttl_hours": 2, "provider": "kind"},
        )
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
