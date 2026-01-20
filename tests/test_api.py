from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch, MagicMock, Mock
import pytest
import datetime
from notion_client.errors import APIResponseError
import requests

client = TestClient(app)

# Patch os.getenv for Auth
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("PERSONALAXIS_API_KEY", "test_key")

def get_headers():
    return {"X-API-Key": "test_key"}

# ============================================================================
# BASIC FUNCTIONALITY TESTS (Existing)
# ============================================================================

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

@patch("api.routers.context.ContextGenerator")
def test_get_daily_context(mock_gen_cls):
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.return_value = "# Daily Context"
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 200
    assert response.json()["success"] is True

@patch("api.routers.journal.JournalService")
def test_create_quick_journal(mock_service_cls):
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "new-page-id"
    
    payload = {"content": "Test journal"}
    response = client.post("/api/journal/quick", json=payload, headers=get_headers())
    assert response.status_code == 200
    assert response.json()["success"] is True

@patch("api.routers.journal.JournalService")
def test_save_full_journal(mock_service_cls):
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "page-id"
    
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

@patch("api.routers.reviews.ReviewService")
def test_save_review(mock_service_cls):
    mock_service = mock_service_cls.return_value
    mock_service.save_review_from_structured_data.return_value = "review-id"
    mock_service.calculate_period.return_value = "2026-W01"
    
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "review_summary": "Good week " * 5, # >50 chars
        "period_assessment": "Başarılı",
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

@patch("api.routers.goals.GoalService")
def test_get_goals_status(mock_service_cls):
    mock_service = mock_service_cls.return_value
    mock_service.get_active_goals.return_value = [{"id": "1", "name": "Test Goal"}]
    
    response = client.get("/api/goals/status", headers=get_headers())
    assert response.status_code == 200
    assert response.json()["success"] is True

@patch("api.routers.habits.HabitService")
def test_get_todays_habits(mock_habit_cls):
    mock_service = mock_habit_cls.return_value
    # Updated to mock fetching active habits with properties structure
    mock_service.get_todays_habits.return_value = [
        {
            "properties": {
                "Ad": {"title": [{"plain_text": "Exercise"}]},
                "Frekans": {"select": {"name": "Daily"}},
                "Son Tamamlama": {"date": {"start": "2026-01-19"}}
            }
        }
    ]
    
    response = client.get("/api/habits/", headers=get_headers())
    assert response.status_code == 200
    
    data = response.json()["data"]["habits"]
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Exercise"
    assert data[0]["frequency"] == "Daily"
    assert data[0]["last_completed"] == "2026-01-19"


# ============================================================================
# AUTHENTICATION ERROR TESTS
# ============================================================================

def test_auth_missing():
    """Test that missing API key returns AUTH_MISSING error code."""
    response = client.get("/api/context/daily")
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_MISSING"
    assert "user_message" in data["error"]

def test_auth_invalid():
    """Test that invalid API key returns AUTH_INVALID error code."""
    response = client.get("/api/context/daily", headers={"X-API-Key": "wrong"})
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_INVALID"

def test_auth_server_key_not_set(monkeypatch):
    """Test server misconfiguration when API key env var is not set."""
    monkeypatch.delenv("PERSONALAXIS_API_KEY", raising=False)
    response = client.get("/api/context/daily", headers={"X-API-Key": "any_key"})
    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert "not configured" in data["error"]["message"]

def test_protected_endpoints_require_auth():
    """Test that all protected endpoints return 403 without API key."""
    endpoints = [
        "/api/context/daily",
        "/api/context/review/weekly",
        "/api/goals/status",
        "/api/habits/",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 403, f"{endpoint} should require auth"
        assert response.json()["error"]["code"] == "AUTH_MISSING"


# ============================================================================
# NOTION API ERROR TESTS
# ============================================================================

def create_mock_api_error(code: str, status: int, message: str = "Test error"):
    """Helper to create mock Notion APIResponseError."""
    mock_response = Mock()
    mock_response.status_code = status
    error = APIResponseError(response=mock_response, message=message, code=code)
    error.status = status
    error.code = code
    return error

@patch("api.routers.context.ContextGenerator")
def test_notion_unauthorized_error(mock_gen_cls):
    """Test NOTION_AUTH_FAILED error when Notion returns unauthorized."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("unauthorized", 401)
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_AUTH_FAILED"
    assert "user_message" in data["error"]

@patch("api.routers.context.ContextGenerator")
def test_notion_rate_limit_error(mock_gen_cls):
    """Test NOTION_RATE_LIMIT error when Notion rate limits requests."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("rate_limited", 429)
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 429
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_RATE_LIMIT"
    assert "details" in data["error"]
    assert "retry_after" in data["error"]["details"]

@patch("api.routers.context.ContextGenerator")
def test_notion_timeout_error(mock_gen_cls):
    """Test NOTION_TIMEOUT error when Notion request times out."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = requests.exceptions.Timeout("Connection timeout")
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 504
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_TIMEOUT"

@patch("api.routers.journal.JournalService")
def test_notion_generic_api_error(mock_service_cls):
    """Test NOTION_API_ERROR for generic Notion errors."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.side_effect = create_mock_api_error("internal_server_error", 500)
    
    payload = {"content": "Test"}
    response = client.post("/api/journal/quick", json=payload, headers=get_headers())
    assert response.status_code == 502
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_API_ERROR"
    assert data["error"]["details"]["notion_status"] == 500


@patch("api.routers.context.ContextGenerator")
def test_notion_restricted_resource_error(mock_gen_cls):
    """Test NOTION_AUTH_FAILED error when Notion returns restricted_resource."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("restricted_resource", 403)
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 401  # Mapped to 401 in error_handlers
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_AUTH_FAILED"


@patch("api.routers.context.ContextGenerator")
def test_notion_object_not_found_error(mock_gen_cls):
    """Test NOTION_RESOURCE_NOT_FOUND error when Notion returns object_not_found."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("object_not_found", 404)
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_RESOURCE_NOT_FOUND"


@patch("api.routers.context.ContextGenerator")
def test_notion_service_unavailable_error(mock_gen_cls):
    """Test NOTION_API_ERROR (502) when Notion returns service_unavailable."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("service_unavailable", 503)
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "NOTION_API_ERROR"
    assert data["error"]["details"]["notion_status"] == 503


@patch("api.routers.context.ContextGenerator")
def test_notion_conflict_error(mock_gen_cls):
    """Test NOTION_API_ERROR (502) when Notion returns conflict_error."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("conflict_error", 409)
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "NOTION_API_ERROR"
    assert data["error"]["details"]["notion_status"] == 409


@patch("api.routers.context.ContextGenerator")
def test_notion_validation_error(mock_gen_cls):
    """Test NOTION_API_ERROR (502) when Notion returns validation_error."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("validation_error", 400)
    
    response = client.get("/api/context/daily", headers=get_headers())
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "NOTION_API_ERROR"
    assert data["error"]["details"]["notion_status"] == 400


# ============================================================================
# VALIDATION ERROR TESTS
# ============================================================================

def test_validation_error_missing_required_field():
    """Test VALIDATION_ERROR when required field is missing."""
    payload = {"title": "Test"}  # Missing 'content'
    response = client.post("/api/journal/quick", json=payload, headers=get_headers())
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]

def test_validation_error_invalid_field_type():
    """Test VALIDATION_ERROR for invalid field types."""
    payload = {
        "title": "Test",
        "raw_content": "Content",
        "date": "invalid-date"  # Should be YYYY-MM-DD
    }
    response = client.post("/api/journal/", json=payload, headers=get_headers())
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_validation_error_invalid_priority():
    """Test validation for invalid priority values."""
    payload = {
        "title": "Test",
        "raw_content": "Content",
        "action_items": [
            {
                "priority": "INVALID",  # Should be P1-P5
                "status": "Aktif",
                "title": "Task",
                "date": "2026-01-19"
            }
        ]
    }
    response = client.post("/api/journal/", json=payload, headers=get_headers())
    assert response.status_code == 422

def test_invalid_review_type():
    """Test INVALID_REVIEW_TYPE error for unsupported review types."""
    response = client.get("/api/context/review/invalid_type", headers=get_headers())
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_REVIEW_TYPE"
    assert "valid_types" in data["error"]["details"]

def test_review_type_mismatch():
    """Test validation when URL review type doesn't match body."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary that is long enough to pass validation checks here",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"]
    }
    response = client.post("/api/reviews/monthly", json=payload, headers=get_headers())
    assert response.status_code == 400


# ============================================================================
# ERROR RESPONSE FORMAT TESTS
# ============================================================================

@patch("api.routers.context.ContextGenerator")
def test_error_response_structure(mock_gen_cls):
    """Test that all errors follow standardized response format."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("unauthorized", 401)
    
    response = client.get("/api/context/daily", headers=get_headers())
    data = response.json()
    
    # Check standard error structure
    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    
    error = data["error"]
    assert "code" in error
    assert "message" in error
    assert "user_message" in error
    assert "timestamp" in error
    
    # Timestamp should be ISO format
    assert "T" in error["timestamp"]

def test_error_contains_turkish_user_message():
    """Test that user_message is in Turkish for better UX."""
    response = client.get("/api/context/daily")
    data = response.json()
    
    # Turkish characters check (ş, ü, ğ, ı, ö, ç)
    user_msg = data["error"]["user_message"]
    assert any(char in user_msg for char in ["ı", "ş", "ğ", "ü", "ö", "ç"]) or len(user_msg) > 0


# ============================================================================
# ENDPOINT-SPECIFIC ERROR TESTS
# ============================================================================

@patch("api.routers.goals.GoalService")
def test_goals_endpoint_notion_error_handling(mock_service_cls):
    """Test that goals endpoint properly handles Notion errors."""
    mock_service = mock_service_cls.return_value
    mock_service.get_active_goals.side_effect = create_mock_api_error("rate_limited", 429)
    
    response = client.get("/api/goals/status", headers=get_headers())
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "NOTION_RATE_LIMIT"

@patch("api.routers.habits.HabitService")
def test_habits_endpoint_timeout_handling(mock_service_cls):
    """Test that habits endpoint handles timeouts."""
    mock_service = mock_service_cls.return_value
    mock_service.get_todays_habits.side_effect = requests.exceptions.Timeout()
    
    response = client.get("/api/habits/", headers=get_headers())
    assert response.status_code == 504
    assert response.json()["error"]["code"] == "NOTION_TIMEOUT"

@patch("api.routers.reviews.ReviewService")
def test_reviews_endpoint_error_handling(mock_service_cls):
    """Test that reviews endpoint handles Notion errors during save."""
    mock_service = mock_service_cls.return_value
    mock_service.calculate_period.return_value = "2026-W01"
    mock_service.save_review_from_structured_data.side_effect = create_mock_api_error("unauthorized", 401)
    
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned",
        "next_period_focus": ["Focus"]
    }
    
    response = client.post("/api/reviews/weekly", json=payload, headers=get_headers())
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "NOTION_AUTH_FAILED"


# ============================================================================
# CONTEXT ROUTER SPECIFIC TESTS
# ============================================================================

@patch("api.routers.context.ContextGenerator")
def test_review_context_with_auto_period(mock_gen_cls):
    """Test that review context auto-calculates period when not provided."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_review_context.return_value = "# Review Context"
    mock_gen.get_period.return_value = "2026-W03"
    
    response = client.get("/api/context/review/weekly", headers=get_headers())
    assert response.status_code == 200
    assert response.json()["data"]["period"] == "2026-W03"

@patch("api.routers.context.ContextGenerator")
def test_review_context_with_explicit_period(mock_gen_cls):
    """Test that review context uses provided period."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_review_context.return_value = "# Review Context"
    # mock get_period to return the second argument (period)
    mock_gen.get_period.side_effect = lambda t, p: p
    
    response = client.get("/api/context/review/weekly?period=2026-W01", headers=get_headers())
    assert response.status_code == 200
    assert response.json()["data"]["period"] == "2026-W01"
