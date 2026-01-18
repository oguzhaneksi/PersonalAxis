from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch, MagicMock
import pytest
import datetime

client = TestClient(app)

# Patch os.getenv for Auth
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("PERSONALAXIS_API_KEY", "test_key")

def get_headers():
    return {"X-API-Key": "test_key"}

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

def test_auth_missing():
    response = client.get("/api/context/daily")
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["message"] == "Missing API Key"

def test_auth_invalid():
    response = client.get("/api/context/daily", headers={"X-API-Key": "wrong"})
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["message"] == "Invalid API key"

def test_auth_server_key_not_set(monkeypatch):
    # Remove the environment variable to simulate misconfiguration
    monkeypatch.delenv("PERSONALAXIS_API_KEY", raising=False)
    response = client.get("/api/context/daily", headers={"X-API-Key": "any_key"})
    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert data["error"]["message"] == "API key not configured in server"

@patch("api.routers.context.ContextGenerator")
def test_get_daily_context(mock_gen_cls):
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.return_value = "# Daily Context"
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 200
    assert response.json()["success"] is True

@patch("api.routers.journal.NotionClient")
def test_create_quick_journal(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_client.create_journal_entry.return_value = "new-page-id"
    
    payload = {"content": "Test journal"}
    response = client.post("/api/journal/quick", json=payload, headers=get_headers())
    assert response.status_code == 200
    assert response.json()["success"] is True

@patch("api.routers.journal.NotionClient")
def test_save_full_journal(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_client.create_journal_entry.return_value = "page-id"
    mock_client.create_task.return_value = "task-id"
    
    payload = {
        "title": "My Day",
        "raw_content": "Today was great.",
        "date": "2026-01-18",
        "emotions_detected": ["Happy"],
        "key_insights": "Focus is key",
        "action_items": [
            {
                "priority": "P1",
                "status": "Aktif",
                "title": "Buy milk",
                "date": "2026-01-19"
            }
        ]
    }
    
    response = client.post("/api/journal/", json=payload, headers=get_headers())
    assert response.status_code == 200
    assert response.json()["data"]["tasks_created"] == ["Buy milk"]

@patch("api.routers.reviews.NotionClient")
def test_save_review(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_client.save_review_session.return_value = "review-id"
    mock_client.find_goal_by_name.return_value = "goal-id"
    mock_client.update_goal_progress.return_value = True
    
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "review_summary": "Good week " * 5, # >50 chars
        "wins": ["Win 1"],
        "challenges": ["Chal 1"],
        "lessons_learned": "Learn more.",
        "next_period_focus": ["Focus 1"],
        "goal_updates": [
            {
                "goal_name": "Run 5k",
                "new_status": "Tamamlandı",
                "progress_delta": 10,
                "notes": "Done it"
            }
        ]
    }
    
    response = client.post("/api/reviews/weekly", json=payload, headers=get_headers())
    if response.status_code != 200:
        print(response.json())
        
    assert response.status_code == 200
    assert response.json()["data"]["updated_goals"] == ["Run 5k"]
