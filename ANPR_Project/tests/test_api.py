"""
Unit tests for FastAPI endpoints.
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).parent.parent))

from api import app

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_stats_endpoint():
    res = client.get("/api/stats")
    assert res.status_code == 200
    assert "total_scans" in res.json()
