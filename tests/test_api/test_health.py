"""
Tests para endpoints de health check
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """Test del endpoint de health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_v1():
    """Test del endpoint de health v1"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

