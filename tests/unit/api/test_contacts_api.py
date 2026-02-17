#!/usr/bin/env python3
"""Unit tests for contacts API endpoints."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from archive_manager.adapters.api import create_app
from archive_manager.infrastructure.config import Settings


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Yield a test client with active lifespan."""
    app = create_app(Settings.for_testing())
    with TestClient(app) as c:
        yield c


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """Health endpoint should return API status."""
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_create_and_list_contacts_flow(client: TestClient) -> None:
    """Create one contact and then list it."""
    create_response = client.post(
        "/api/v1/contacts",
        json={
            "first_name": "Ana",
            "last_name": "Lopez",
            "email": "ana@example.com",
            "phone": "600000000",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/contacts")
    assert list_response.status_code == 200

    payload = list_response.json()
    assert payload["total"] == 1
    assert payload["current_page"] == 1
    assert len(payload["contacts"]) == 1
    assert payload["contacts"][0]["email"] == "ana@example.com"


def test_search_email_not_found_returns_404(client: TestClient) -> None:
    """Email search should return 404 for missing contact."""
    response = client.get("/api/v1/contacts/search/email", params={"email": "x@y.com"})

    assert response.status_code == 404


def test_delete_nonexistent_contact_returns_404(client: TestClient) -> None:
    """Delete endpoint should return 404 when contact is missing."""
    response = client.delete("/api/v1/contacts/999")

    assert response.status_code == 404


def test_get_contact_by_id_returns_data(client: TestClient) -> None:
    """Get by ID should return the contact data."""
    # Create
    created = client.post(
        "/api/v1/contacts",
        json={
            "first_name": "Get",
            "last_name": "ById",
            "email": "id@test.com",
            "phone": "699887766",
        },
    ).json()
    contact_id = created["contact_id"]

    # Get
    response = client.get(f"/api/v1/contacts/{contact_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["contact_id"] == contact_id
    assert data["email"] == "id@test.com"


def test_get_contact_by_id_not_found(client: TestClient) -> None:
    """Get by ID should return 404 for unknown ID."""
    response = client.get("/api/v1/contacts/999999")
    assert response.status_code == 404
