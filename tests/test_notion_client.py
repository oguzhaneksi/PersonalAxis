import pytest
from unittest.mock import MagicMock, patch
from orchestration.notion_service import NotionClient

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("NOTION_TOKEN", "fake_token")
    monkeypatch.setenv("PILLARS_DB_ID", "pillars_id")
    monkeypatch.setenv("LT_GOALS_DB_ID", "lt_goals_id")
    monkeypatch.setenv("HABITS_DB_ID", "habits_id")
    monkeypatch.setenv("PERIODIC_GOALS_DB_ID", "p_goals_id")
    monkeypatch.setenv("ACTIONS_DB_ID", "actions_id")
    monkeypatch.setenv("JOURNAL_DB_ID", "journal_id")
    monkeypatch.setenv("REVIEWS_DB_ID", "reviews_id")

def test_notion_client_init(mock_env):
    client = NotionClient()
    assert client.token == "fake_token"
    assert client.db_ids["pillars"] == "pillars_id"

@patch("orchestration.notion_service.Client")
def test_fetch_all_pillars(MockNotion, mock_env):
    # Setup mock response
    mock_instance = MockNotion.return_value
    mock_instance.databases.query.return_value = {
        "results": [{"id": "page1", "properties": {"Ad": {"title": [{"plain_text": "Pillar 1"}]}}}],
        "has_more": False
    }
    
    client = NotionClient()
    pillars = client.fetch_all_pillars()
    
    assert len(pillars) == 1
    assert pillars[0]["id"] == "page1"
    mock_instance.databases.query.assert_called_once()

@patch("orchestration.notion_service.Client")
def test_create_task(MockNotion, mock_env):
    mock_instance = MockNotion.return_value
    mock_instance.pages.create.return_value = {"id": "new_task_id"}
    
    client = NotionClient()
    task_id = client.create_task(name="Test Task", priority="P1")
    
    assert task_id == "new_task_id"
    mock_instance.pages.create.assert_called_once()
    args, kwargs = mock_instance.pages.create.call_args
    assert kwargs["properties"]["Ad"]["title"][0]["text"]["content"] == "Test Task"
    assert kwargs["properties"]["Öncelik"]["select"]["name"] == "P1"
