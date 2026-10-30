from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model" in data

def test_generate_script_validation_failure():
    payload = {"content_type": "youtube", "topic": "ab"}
    response = client.post("/api/generate-script", json=payload)
    assert response.status_code == 422

@patch("app.routes.scripts.gemini_service.generate_text", new_callable=AsyncMock)
def test_generate_youtube_script_success(mock_generate):
    mock_generate.return_value = "# [Video Title Suggestions]\n1. Top 5 AI Tools"
    payload = {
        "content_type": "youtube",
        "topic": "Top 5 AI productivity tools for developers",
        "duration": "8-10 minutes"
    }
    response = client.post("/api/generate-script", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Top 5 AI Tools" in data["script"]
