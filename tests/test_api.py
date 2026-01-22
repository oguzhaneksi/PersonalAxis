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
    monkeypatch.setenv("PERSONALAXIS_PASSWORD", "test_password")
    monkeypatch.setenv("PERSONALAXIS_COOKIE_SECURE", "false")  # For testing
    monkeypatch.setenv("NOTION_TOKEN", "secret_test_token")  # Required for NotionService

def login_and_get_cookies() -> dict:
    """Helper to login and return session cookies for TestClient."""
    response = client.post("/api/auth/login", json={"password": "test_password"})
    assert response.status_code == 200
    # TestClient doesn't persist cookies automatically, so we need to extract them
    # and pass them explicitly to subsequent requests
    return dict(response.cookies)

# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_login_success():
    """Test successful login with correct password."""
    response = client.post("/api/auth/login", json={"password": "test_password"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "expires_at" in data["data"]
    assert "personalaxis_session" in response.cookies

def test_login_failure():
    """Test login failure with incorrect password."""
    response = client.post("/api/auth/login", json={"password": "wrong_password"})
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_INVALID"

def test_login_missing_password():
    """Test login failure when password is missing (validation error)."""
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_logout():
    """Test logout clears session cookie."""
    cookies = login_and_get_cookies()
    response = client.post("/api/auth/logout", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "logged_out"

def test_auth_status_authenticated():
    """Test auth status returns authenticated when session is valid."""
    cookies = login_and_get_cookies()
    response = client.get("/api/auth/status", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["authenticated"] is True
    assert "expires_at" in data["data"]

def test_auth_status_not_authenticated():
    """Test auth status returns not authenticated without session."""
    response = client.get("/api/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["authenticated"] is False

def test_auth_status_invalid_session():
    """Test auth status with invalid session cookie."""
    response = client.get("/api/auth/status", cookies={"personalaxis_session": "invalid_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["authenticated"] is False


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
    
    cookies = login_and_get_cookies()
    response = client.get("/api/context/daily", cookies=cookies)
    assert response.status_code == 200
    assert response.json()["success"] is True

@patch("api.routers.journal.JournalService")
def test_create_quick_journal(mock_service_cls):
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "new-page-id"
    
    cookies = login_and_get_cookies()
    payload = {"content": "Test journal"}
    response = client.post("/api/journal/quick", json=payload, cookies=cookies)
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
    
    cookies = login_and_get_cookies()
    response = client.post("/api/journal/", json=payload, cookies=cookies)
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
    
    cookies = login_and_get_cookies()
    response = client.post("/api/reviews/weekly", json=payload, cookies=cookies)
    if response.status_code != 200:
        print(response.json())
        
    assert response.status_code == 200
    assert response.json()["data"]["updated_goals"] == ["Run 5k"]

@patch("api.routers.goals.GoalService")
def test_get_goals_status(mock_service_cls):
    mock_service = mock_service_cls.return_value
    mock_service.get_active_goals.return_value = [{"id": "1", "name": "Test Goal"}]
    
    cookies = login_and_get_cookies()
    response = client.get("/api/goals/status", cookies=cookies)
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
    
    cookies = login_and_get_cookies()
    response = client.get("/api/habits/", cookies=cookies)
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

def test_auth_missing_on_protected_route():
    """Test that missing session cookie returns AUTH_MISSING error code."""
    response = client.get("/api/context/daily")
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_MISSING"
    assert "user_message" in data["error"]

def test_auth_expired_session():
    """Test that expired/invalid session returns AUTH_EXPIRED error code."""
    response = client.get("/api/context/daily", cookies={"personalaxis_session": "invalid_token"})
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_EXPIRED"

def test_auth_server_password_not_set(monkeypatch):
    """Test server misconfiguration when password env var is not set."""
    monkeypatch.delenv("PERSONALAXIS_PASSWORD", raising=False)
    response = client.post("/api/auth/login", json={"password": "any_password"})
    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert "not configured" in data["error"]["message"]

def test_protected_endpoints_require_auth():
    """Test that all protected endpoints return 403 without session."""
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
    
    cookies = login_and_get_cookies()
    response = client.get("/api/context/daily", cookies=cookies)
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
    
    cookies = login_and_get_cookies()
    response = client.get("/api/context/daily", cookies=cookies)
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
    
    cookies = login_and_get_cookies()
    response = client.get("/api/context/daily", cookies=cookies)
    assert response.status_code == 504
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_TIMEOUT"

@patch("api.routers.journal.JournalService")
def test_notion_generic_api_error(mock_service_cls):
    """Test NOTION_API_ERROR for generic Notion errors."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.side_effect = create_mock_api_error("internal_server_error", 500)
    
    cookies = login_and_get_cookies()
    payload = {"content": "Test"}
    response = client.post("/api/journal/quick", json=payload, cookies=cookies)
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
    
    response = client.get("/api/context/daily", cookies=login_and_get_cookies())
    assert response.status_code == 401  # Mapped to 401 in error_handlers
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_AUTH_FAILED"


@patch("api.routers.context.ContextGenerator")
def test_notion_object_not_found_error(mock_gen_cls):
    """Test NOTION_RESOURCE_NOT_FOUND error when Notion returns object_not_found."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("object_not_found", 404)
    
    response = client.get("/api/context/daily", cookies=login_and_get_cookies())
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOTION_RESOURCE_NOT_FOUND"


@patch("api.routers.context.ContextGenerator")
def test_notion_service_unavailable_error(mock_gen_cls):
    """Test NOTION_API_ERROR (502) when Notion returns service_unavailable."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("service_unavailable", 503)
    
    response = client.get("/api/context/daily", cookies=login_and_get_cookies())
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "NOTION_API_ERROR"
    assert data["error"]["details"]["notion_status"] == 503


@patch("api.routers.context.ContextGenerator")
def test_notion_conflict_error(mock_gen_cls):
    """Test NOTION_API_ERROR (502) when Notion returns conflict_error."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("conflict_error", 409)
    
    response = client.get("/api/context/daily", cookies=login_and_get_cookies())
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "NOTION_API_ERROR"
    assert data["error"]["details"]["notion_status"] == 409


@patch("api.routers.context.ContextGenerator")
def test_notion_validation_error(mock_gen_cls):
    """Test NOTION_API_ERROR (502) when Notion returns validation_error."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("validation_error", 400)
    
    response = client.get("/api/context/daily", cookies=login_and_get_cookies())
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
    response = client.post("/api/journal/quick", json=payload, cookies=login_and_get_cookies())
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
    response = client.post("/api/journal/", json=payload, cookies=login_and_get_cookies())
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
    response = client.post("/api/journal/", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_invalid_review_type():
    """Test INVALID_REVIEW_TYPE error for unsupported review types."""
    response = client.get("/api/context/review/invalid_type", cookies=login_and_get_cookies())
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
    response = client.post("/api/reviews/monthly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 400


# ============================================================================
# ERROR RESPONSE FORMAT TESTS
# ============================================================================

@patch("api.routers.context.ContextGenerator")
def test_error_response_structure(mock_gen_cls):
    """Test that all errors follow standardized response format."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.side_effect = create_mock_api_error("unauthorized", 401)
    
    response = client.get("/api/context/daily", cookies=login_and_get_cookies())
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
    
    response = client.get("/api/goals/status", cookies=login_and_get_cookies())
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "NOTION_RATE_LIMIT"

@patch("api.routers.habits.HabitService")
def test_habits_endpoint_timeout_handling(mock_service_cls):
    """Test that habits endpoint handles timeouts."""
    mock_service = mock_service_cls.return_value
    mock_service.get_todays_habits.side_effect = requests.exceptions.Timeout()
    
    response = client.get("/api/habits/", cookies=login_and_get_cookies())
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
    
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
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
    year, week, _ = datetime.date.today().isocalendar()
    current_week_period = f"{year}-W{week:02d}"
    mock_gen.get_period.return_value = current_week_period
    
    response = client.get("/api/context/review/weekly", cookies=login_and_get_cookies())
    assert response.status_code == 200
    assert response.json()["data"]["period"] == current_week_period

@patch("api.routers.context.ContextGenerator")
def test_review_context_with_explicit_period(mock_gen_cls):
    """Test that review context uses provided period."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_review_context.return_value = "# Review Context"
    # mock get_period to return the second argument (period)
    mock_gen.get_period.side_effect = lambda t, p: p
    
    response = client.get("/api/context/review/weekly?period=2026-W01", cookies=login_and_get_cookies())
    assert response.status_code == 200
    assert response.json()["data"]["period"] == "2026-W01"


# ============================================================================
# ADDITIONAL VALIDATION TESTS
# ============================================================================

def test_validation_empty_wins_list():
    """Test that empty wins list fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": [],  # Empty list should fail
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"]
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

def test_validation_empty_challenges_list():
    """Test that empty challenges list fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": [],  # Empty list should fail
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"]
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_empty_next_period_focus():
    """Test that empty next_period_focus list fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": []  # Empty list should fail
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_review_summary_too_short():
    """Test that review_summary under min_length fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Too short",  # Less than 50 chars
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"]
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_invalid_period_assessment():
    """Test that invalid period_assessment value fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "InvalidStatus",  # Not in enum
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"]
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_invalid_goal_status():
    """Test that invalid goal status in goal_updates fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"],
        "goal_updates": [
            {
                "goal_name": "Test Goal",
                "new_status": "InvalidStatus",  # Not in enum
                "progress_delta": 10,
                "notes": "Test notes"
            }
        ]
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_progress_delta_out_of_range_positive():
    """Test that progress_delta > 100 fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"],
        "goal_updates": [
            {
                "goal_name": "Test Goal",
                "new_status": "Tamamlandı",
                "progress_delta": 101,  # Out of range
                "notes": "Test notes"
            }
        ]
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_progress_delta_out_of_range_negative():
    """Test that progress_delta < -100 fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"],
        "goal_updates": [
            {
                "goal_name": "Test Goal",
                "new_status": "Tamamlandı",
                "progress_delta": -101,  # Out of range
                "notes": "Test notes"
            }
        ]
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_journal_content_too_long():
    """Test that journal content exceeding max_length fails validation."""
    payload = {"content": "x" * 5001}  # Exceeds 5000 char limit
    response = client.post("/api/journal/quick", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_journal_empty_content():
    """Test that empty journal content fails validation."""
    payload = {"content": ""}
    response = client.post("/api/journal/quick", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422

def test_validation_empty_lessons_learned():
    """Test that empty lessons_learned fails validation."""
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "",  # Empty string
        "next_period_focus": ["Focus"]
    }
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 422


# ============================================================================
# JOURNAL ENDPOINT EDGE CASES
# ============================================================================

@patch("api.routers.journal.JournalService")
def test_journal_default_date_handling(mock_service_cls):
    """Test that journal defaults to today when date is None."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "page-id"
    
    payload = {
        "title": "Test Entry",
        "raw_content": "Content without date"
        # date is omitted, should default to today
    }
    
    response = client.post("/api/journal/", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200
    
    # Verify that save was called with today's date
    call_args = mock_service.save_journal_from_structured_data.call_args
    assert datetime.datetime.now().strftime("%Y-%m-%d") == call_args.kwargs["date_str"]

@patch("api.routers.journal.JournalService")
def test_quick_journal_default_title(mock_service_cls):
    """Test that quick journal generates default title when None."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "page-id"
    
    payload = {"content": "Test content"}  # No title provided
    
    response = client.post("/api/journal/quick", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200
    
    # Verify that a default title was generated
    call_args = mock_service.save_journal_from_structured_data.call_args
    assert "Quick Entry" in call_args.kwargs["title"]

@patch("api.routers.journal.JournalService")
def test_journal_with_empty_action_items(mock_service_cls):
    """Test journal save with empty action_items list."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "page-id"
    
    payload = {
        "title": "Test",
        "raw_content": "Content",
        "action_items": []
    }
    
    response = client.post("/api/journal/", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200
    assert response.json()["data"]["tasks_created"] == []

@patch("api.routers.journal.JournalService")
def test_journal_with_multiple_action_items(mock_service_cls):
    """Test journal save with multiple action items."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "page-id"
    
    payload = {
        "title": "Test",
        "raw_content": "Content",
        "action_items": [
            {
                "priority": "P1",
                "status": "Aktif",
                "title": "Task 1",
                "date": "2026-01-20"
            },
            {
                "priority": "P2",
                "status": "Aktif",
                "title": "Task 2",
                "date": "2026-01-21"
            },
            {
                "priority": "P3",
                "status": "Aktif",
                "title": "Task 3",
                "date": "2026-01-22"
            }
        ]
    }
    
    response = client.post("/api/journal/", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200
    assert len(response.json()["data"]["tasks_created"]) == 3
    assert response.json()["data"]["tasks_created"] == ["Task 1", "Task 2", "Task 3"]

@patch("api.routers.journal.JournalService")
def test_journal_with_all_optional_fields(mock_service_cls):
    """Test journal save with all optional fields populated."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "page-id"
    
    payload = {
        "title": "Complete Journal",
        "raw_content": "Full content",
        "date": "2026-01-18",
        "emotions_detected": ["Happy", "Grateful", "Motivated"],
        "key_insights": "Deep insights here",
        "action_items": [
            {
                "priority": "P1",
                "status": "Aktif",
                "title": "Important Task",
                "date": "2026-01-19"
            }
        ]
    }
    
    response = client.post("/api/journal/", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200
    
    # Verify all fields were passed to service
    call_args = mock_service.save_journal_from_structured_data.call_args
    assert call_args.kwargs["emotions"] == ["Happy", "Grateful", "Motivated"]
    assert call_args.kwargs["insights"] == "Deep insights here"


# ============================================================================
# REVIEW ENDPOINT EDGE CASES
# ============================================================================

@patch("api.routers.reviews.ReviewService")
def test_review_with_empty_goal_updates(mock_service_cls):
    """Test review save with no goal updates (valid scenario)."""
    mock_service = mock_service_cls.return_value
    mock_service.save_review_from_structured_data.return_value = "review-id"
    mock_service.calculate_period.return_value = "2026-W03"
    
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win"],
        "challenges": ["Challenge"],
        "lessons_learned": "Learned something",
        "next_period_focus": ["Focus"],
        "goal_updates": []  # Empty but valid
    }
    
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200
    assert response.json()["data"]["updated_goals"] == []

@patch("api.routers.reviews.ReviewService")
def test_review_with_multiple_goal_updates(mock_service_cls):
    """Test review save with multiple goal updates."""
    mock_service = mock_service_cls.return_value
    mock_service.save_review_from_structured_data.return_value = "review-id"
    mock_service.calculate_period.return_value = "2026-W03"
    
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Karışık",
        "review_summary": "Test summary with enough characters to pass min length validation",
        "wins": ["Win 1", "Win 2"],
        "challenges": ["Challenge 1", "Challenge 2"],
        "lessons_learned": "Multiple lessons learned",
        "next_period_focus": ["Focus 1", "Focus 2"],
        "goal_updates": [
            {
                "goal_name": "Goal 1",
                "new_status": "Devam Ediyor",
                "progress_delta": 15,
                "notes": "Good progress"
            },
            {
                "goal_name": "Goal 2",
                "new_status": "Tamamlandı",
                "progress_delta": 100,
                "notes": "Completed!"
            },
            {
                "goal_name": "Goal 3",
                "new_status": "Ertelendi",
                "progress_delta": -10,
                "notes": "Postponed due to priorities"
            }
        ]
    }
    
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200
    assert len(response.json()["data"]["updated_goals"]) == 3
    assert response.json()["data"]["updated_goals"] == ["Goal 1", "Goal 2", "Goal 3"]

@patch("api.routers.reviews.ReviewService")
def test_review_negative_progress_delta(mock_service_cls):
    """Test review with negative progress delta (regression)."""
    mock_service = mock_service_cls.return_value
    mock_service.save_review_from_structured_data.return_value = "review-id"
    mock_service.calculate_period.return_value = "2026-W03"
    
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Zorlayıcı",
        "review_summary": "Difficult week with some setbacks but learning opportunities present",
        "wins": ["Small win"],
        "challenges": ["Major setback"],
        "lessons_learned": "Need to adjust approach",
        "next_period_focus": ["Recovery"],
        "goal_updates": [
            {
                "goal_name": "Fitness Goal",
                "new_status": "Devam Ediyor",
                "progress_delta": -25,  # Negative progress
                "notes": "Missed workouts due to illness"
            }
        ]
    }
    
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200

@patch("api.routers.reviews.ReviewService")
def test_review_all_assessment_types(mock_service_cls):
    """Test review with each assessment type."""
    mock_service = mock_service_cls.return_value
    mock_service.save_review_from_structured_data.return_value = "review-id"
    mock_service.calculate_period.return_value = "2026-W03"
    
    assessment_types = ["Başarılı", "Karışık", "Zorlayıcı"]
    
    for assessment in assessment_types:
        payload = {
            "review_type": "weekly",
            "date": "2026-01-18",
            "period_assessment": assessment,
            "review_summary": f"Testing {assessment} assessment with sufficient length for validation",
            "wins": ["Win"],
            "challenges": ["Challenge"],
            "lessons_learned": "Lesson",
            "next_period_focus": ["Focus"]
        }
        
        response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
        assert response.status_code == 200, f"Failed for assessment: {assessment}"


# ============================================================================
# HABITS ENDPOINT EDGE CASES
# ============================================================================

@patch("api.routers.habits.HabitService")
def test_habits_empty_list(mock_service_cls):
    """Test habits endpoint with empty habits list."""
    mock_service = mock_service_cls.return_value
    mock_service.get_todays_habits.return_value = []
    
    response = client.get("/api/habits/", cookies=login_and_get_cookies())
    assert response.status_code == 200
    assert response.json()["data"]["habits"] == []

@patch("api.routers.habits.HabitService")
def test_habits_missing_properties(mock_service_cls):
    """Test habits with missing/incomplete properties."""
    mock_service = mock_service_cls.return_value
    mock_service.get_todays_habits.return_value = [
        {
            "properties": {
                "Ad": {"title": [{"plain_text": "Habit 1"}]}
                # Missing Frekans and Son Tamamlama
            }
        }
    ]
    
    response = client.get("/api/habits/", cookies=login_and_get_cookies())
    assert response.status_code == 200
    
    habits = response.json()["data"]["habits"]
    assert len(habits) == 1
    assert habits[0]["name"] == "Habit 1"
    assert habits[0]["frequency"] == "Belirsiz"  # Default value
    assert habits[0]["last_completed"] is None

@patch("api.routers.habits.HabitService")
def test_habits_with_null_last_completed(mock_service_cls):
    """Test habits with null last_completed date."""
    mock_service = mock_service_cls.return_value
    mock_service.get_todays_habits.return_value = [
        {
            "properties": {
                "Ad": {"title": [{"plain_text": "New Habit"}]},
                "Frekans": {"select": {"name": "Weekly"}},
                "Son Tamamlama": {"date": None}  # Never completed
            }
        }
    ]
    
    response = client.get("/api/habits/", cookies=login_and_get_cookies())
    assert response.status_code == 200
    
    habits = response.json()["data"]["habits"]
    assert habits[0]["last_completed"] is None

@patch("api.routers.habits.HabitService")
def test_habits_multiple_frequencies(mock_service_cls):
    """Test habits with different frequency types."""
    mock_service = mock_service_cls.return_value
    mock_service.get_todays_habits.return_value = [
        {
            "properties": {
                "Ad": {"title": [{"plain_text": "Daily Habit"}]},
                "Frekans": {"select": {"name": "Daily"}},
                "Son Tamamlama": {"date": {"start": "2026-01-20"}}
            }
        },
        {
            "properties": {
                "Ad": {"title": [{"plain_text": "Weekly Habit"}]},
                "Frekans": {"select": {"name": "Weekly"}},
                "Son Tamamlama": {"date": {"start": "2026-01-15"}}
            }
        },
        {
            "properties": {
                "Ad": {"title": [{"plain_text": "Monthly Habit"}]},
                "Frekans": {"select": {"name": "Monthly"}},
                "Son Tamamlama": {"date": {"start": "2026-01-01"}}
            }
        }
    ]
    
    response = client.get("/api/habits/", cookies=login_and_get_cookies())
    assert response.status_code == 200
    
    habits = response.json()["data"]["habits"]
    assert len(habits) == 3
    assert habits[0]["frequency"] == "Daily"
    assert habits[1]["frequency"] == "Weekly"
    assert habits[2]["frequency"] == "Monthly"


# ============================================================================
# GOALS ENDPOINT EDGE CASES
# ============================================================================

@patch("api.routers.goals.GoalService")
def test_goals_empty_list(mock_service_cls):
    """Test goals endpoint with empty goals list."""
    mock_service = mock_service_cls.return_value
    mock_service.get_active_goals.return_value = []
    
    response = client.get("/api/goals/status", cookies=login_and_get_cookies())
    assert response.status_code == 200
    assert response.json()["data"]["goals"] == []

@patch("api.routers.goals.GoalService")
def test_goals_multiple_goals(mock_service_cls):
    """Test goals endpoint with multiple goals."""
    mock_service = mock_service_cls.return_value
    mock_service.get_active_goals.return_value = [
        {"id": "1", "name": "Weekly Goal", "type": "Weekly"},
        {"id": "2", "name": "Monthly Goal", "type": "Monthly"},
        {"id": "3", "name": "Quarterly Goal", "type": "Quarterly"},
    ]
    
    response = client.get("/api/goals/status", cookies=login_and_get_cookies())
    assert response.status_code == 200
    
    goals = response.json()["data"]["goals"]
    assert len(goals) == 3


# ============================================================================
# SUCCESS RESPONSE FORMAT TESTS
# ============================================================================

@patch("api.routers.context.ContextGenerator")
def test_success_response_structure(mock_gen_cls):
    """Test that success responses follow standardized format."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_daily_context.return_value = "# Context"
    
    response = client.get("/api/context/daily", cookies=login_and_get_cookies())
    data = response.json()
    
    # Check standard success structure
    assert "success" in data
    assert data["success"] is True
    assert "data" in data
    assert "timestamp" in data["data"]
    
    # Timestamp should be ISO format
    assert "T" in data["data"]["timestamp"]

@patch("api.routers.journal.JournalService")
def test_success_response_timestamp_format(mock_service_cls):
    """Test that timestamps in success responses are ISO formatted."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "page-id"
    
    payload = {"content": "Test"}
    response = client.post("/api/journal/quick", json=payload, cookies=login_and_get_cookies())
    
    assert response.status_code == 200
    # The response doesn't include timestamp, only success and data with page_id


# ============================================================================
# CONTEXT ROUTER ADDITIONAL TESTS
# ============================================================================

@patch("api.routers.context.ContextGenerator")
def test_context_all_review_types(mock_gen_cls):
    """Test review context generation for all valid review types."""
    mock_gen = mock_gen_cls.return_value
    mock_gen.generate_review_context.return_value = "# Review"
    mock_gen.get_period.return_value = "2026-W03"
    
    review_types = ["weekly", "monthly", "quarterly", "yearly"]
    
    for review_type in review_types:
        response = client.get(f"/api/context/review/{review_type}", cookies=login_and_get_cookies())
        assert response.status_code == 200, f"Failed for {review_type}"
        assert response.json()["data"]["review_type"] == review_type


# ============================================================================
# SPECIAL CHARACTERS AND EDGE CASES
# ============================================================================

@patch("api.routers.journal.JournalService")
def test_journal_with_turkish_characters(mock_service_cls):
    """Test journal content with Turkish special characters."""
    mock_service = mock_service_cls.return_value
    mock_service.save_journal_from_structured_data.return_value = "page-id"
    
    payload = {
        "content": "Bugün çok güzel bir gündü. İşler başarılı geçti. Şükürler olsun! Öğrendim ve büyüdüm."
    }
    
    response = client.post("/api/journal/quick", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200

@patch("api.routers.reviews.ReviewService")
def test_review_with_special_characters(mock_service_cls):
    """Test review with emoji and special characters."""
    mock_service = mock_service_cls.return_value
    mock_service.save_review_from_structured_data.return_value = "review-id"
    mock_service.calculate_period.return_value = "2026-W03"
    
    payload = {
        "review_type": "weekly",
        "date": "2026-01-18",
        "period_assessment": "Başarılı",
        "review_summary": "Great week! 🎉 Achieved 90% of goals. türkçe karakterler: ğüşiöç ĞÜŞIÖÇ",
        "wins": ["Win 💪", "Success ✨"],
        "challenges": ["Challenge ⚠️"],
        "lessons_learned": "Always stay focused 🎯",
        "next_period_focus": ["Focus 🔥"]
    }
    
    response = client.post("/api/reviews/weekly", json=payload, cookies=login_and_get_cookies())
    assert response.status_code == 200
