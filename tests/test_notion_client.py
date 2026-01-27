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

@patch("orchestration.notion_service.Client")
def test_fetch_page_content(MockNotion, mock_env):
    mock_instance = MockNotion.return_value
    # Mock blocks response
    mock_instance.blocks.children.list.return_value = {
        "results": [
            {
                "type": "paragraph",
                "paragraph": {"rich_text": [{"plain_text": "Sample paragraph"}]}
            },
            {
                "type": "heading_2",
                "heading_2": {"rich_text": [{"plain_text": "Section Title"}]}
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"plain_text": "Item 1"}]}
            }
        ],
        "has_more": False
    }
    
    client = NotionClient()
    content = client.fetch_page_content("fake_page_id")
    
    assert "Sample paragraph" in content
    assert "## Section Title" in content
    assert "- Item 1" in content
    mock_instance.blocks.children.list.assert_called_once_with(block_id="fake_page_id", start_cursor=None)

def test_parse_blocks_to_markdown():
    client = NotionClient.__new__(NotionClient) # Create without init to avoid env check
    blocks = [
        {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Para"}]}},
        {"type": "divider", "divider": {}},
        {"type": "to_do", "to_do": {"rich_text": [{"plain_text": "Task"}], "checked": True}},
        {"type": "quote", "quote": {"rich_text": [{"plain_text": "Quote"}]}},
        {"type": "callout", "callout": {"rich_text": [{"plain_text": "Callout"}], "icon": {"emoji": "💡"}}}
    ]
    
    md = client._parse_blocks_to_markdown(blocks)
    
    assert "Para" in md
    assert "---" in md
    assert "- [x] Task" in md
    assert "> Quote" in md
    assert "> 💡 Callout" in md

@patch("orchestration.notion_service.Client")
def test_create_journal_entry(MockNotion, mock_env):
    mock_instance = MockNotion.return_value
    mock_instance.pages.create.return_value = {"id": "new_journal_id"}
    
    client = NotionClient()
    journal_id = client.create_journal_entry(
        date_str="2026-01-27",
        title="2026-01-27",
        content="Test content",
        emotions=["Happy"],
        insights="Life is good"
    )
    
    assert journal_id == "new_journal_id"
    mock_instance.pages.create.assert_called_once()
    args, kwargs = mock_instance.pages.create.call_args
    properties = kwargs["properties"]
    
    # Check that manual period fields are NOT in properties
    assert "Hafta" not in properties
    assert "Ay" not in properties
    assert "Çeyrek" not in properties
    assert "Yıl" not in properties
    
    # Check required fields
    assert properties["Tarih Kodu"]["title"][0]["text"]["content"] == "2026-01-27"
    assert properties["Tarih"]["date"]["start"] == "2026-01-27"

@patch("orchestration.notion_service.Client")
def test_fetch_journals_by_period(MockNotion, mock_env):
    mock_instance = MockNotion.return_value
    mock_instance.databases.query.return_value = {"results": [], "has_more": False}
    
    client = NotionClient()
    client.fetch_journals_by_period("Hafta", "2026-W04")
    
    mock_instance.databases.query.assert_called_once()
    args, kwargs = mock_instance.databases.query.call_args
    query_filter = kwargs["filter"]
    
    # Check that it uses formula filter
    assert "formula" in query_filter
    assert query_filter["formula"]["string"]["equals"] == "2026-W04"
    assert "rich_text" not in query_filter
