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

# ============================================================================
# FETCH_ACTIVE_HABIT TESTS (Phase 7.3 Refactoring)
# ============================================================================

@patch("orchestration.notion_service.Client")
def test_fetch_active_habit_success(MockNotion, mock_env):
    """Test successfully fetching an active habit by ID."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.retrieve.return_value = {
        "id": "habit123",
        "parent": {
            "type": "database_id",
            "database_id": "habits_id"
        },
        "properties": {
            "Ad": {"title": [{"plain_text": "Morning Meditation"}]},
            "Durum": {"select": {"name": "Aktif"}},
            "Frekans": {"select": {"name": "Günlük"}}
        }
    }
    
    client = NotionClient()
    habit = client.fetch_active_habit("habit123")
    
    assert habit is not None
    assert habit["id"] == "habit123"
    assert habit["properties"]["Durum"]["select"]["name"] == "Aktif"
    mock_instance.pages.retrieve.assert_called_once_with(page_id="habit123")


@patch("orchestration.notion_service.Client")
def test_fetch_active_habit_inactive_status(MockNotion, mock_env):
    """Test fetching a habit with inactive status returns None."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.retrieve.return_value = {
        "id": "habit456",
        "parent": {
            "type": "database_id",
            "database_id": "habits_id"
        },
        "properties": {
            "Ad": {"title": [{"plain_text": "Old Habit"}]},
            "Durum": {"select": {"name": "Beklemede"}}
        }
    }
    
    client = NotionClient()
    habit = client.fetch_active_habit("habit456")
    
    assert habit is None
    mock_instance.pages.retrieve.assert_called_once()


@patch("orchestration.notion_service.Client")
def test_fetch_active_habit_wrong_database(MockNotion, mock_env):
    """Test fetching a page from wrong database returns None."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.retrieve.return_value = {
        "id": "goal789",
        "parent": {
            "type": "database_id",
            "database_id": "p_goals_id"  # Wrong database
        },
        "properties": {
            "Ad": {"title": [{"plain_text": "Some Goal"}]},
            "Durum": {"select": {"name": "Aktif"}}
        }
    }
    
    client = NotionClient()
    habit = client.fetch_active_habit("goal789")
    
    assert habit is None


@patch("orchestration.notion_service.Client")
def test_fetch_active_habit_not_found(MockNotion, mock_env):
    """Test fetching non-existent habit handles exception and returns None."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.retrieve.side_effect = Exception("Object not found")
    
    client = NotionClient()
    habit = client.fetch_active_habit("nonexistent_id")
    
    assert habit is None
    mock_instance.pages.retrieve.assert_called_once()


@patch("orchestration.notion_service.Client")
def test_fetch_active_habit_api_error(MockNotion, mock_env):
    """Test API error during habit fetch returns None."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.retrieve.side_effect = Exception("API rate limit exceeded")
    
    client = NotionClient()
    habit = client.fetch_active_habit("habit999")
    
    assert habit is None


@patch("orchestration.notion_service.Client")
def test_fetch_active_habit_missing_status_field(MockNotion, mock_env):
    """Test habit with missing status field returns None."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.retrieve.return_value = {
        "id": "habit_no_status",
        "parent": {
            "type": "database_id",
            "database_id": "habits_id"
        },
        "properties": {
            "Ad": {"title": [{"plain_text": "Incomplete Habit"}]}
            # Missing "Durum" property
        }
    }
    
    client = NotionClient()
    habit = client.fetch_active_habit("habit_no_status")
    
    assert habit is None


@patch("orchestration.notion_service.Client")
def test_fetch_active_habit_with_dashes_in_db_id(MockNotion, mock_env):
    """Test database ID comparison works with or without dashes."""
    mock_instance = MockNotion.return_value
    # Notion returns IDs with dashes
    mock_instance.pages.retrieve.return_value = {
        "id": "habit-with-dashes",
        "parent": {
            "type": "database_id",
            "database_id": "hab-its_id"  # Matches 'habits_id' after - removal
        },
        "properties": {
            "Durum": {"select": {"name": "Aktif"}}
        }
    }
    
    client = NotionClient()
    # Should handle dash comparison correctly
    habit = client.fetch_active_habit("habit-with-dashes")
    
    # Should be found because dash removal makes them match
    assert habit is not None
    assert habit["id"] == "habit-with-dashes"
    mock_instance.pages.retrieve.assert_called_once()


@patch("orchestration.notion_service.Client")
def test_fetch_active_habit_empty_parent(MockNotion, mock_env):
    """Test habit with empty or malformed parent returns None."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.retrieve.return_value = {
        "id": "orphan_habit",
        "parent": {},  # Missing database_id
        "properties": {
            "Durum": {"select": {"name": "Aktif"}}
        }
    }
    
    client = NotionClient()
    habit = client.fetch_active_habit("orphan_habit")
    
    # Should handle gracefully - parent type check will fail
    assert habit is None


# ============================================================================
# UPDATE_HABIT_LOG TESTS
# ============================================================================

@patch("orchestration.notion_service.Client")
def test_update_habit_log_both_fields(MockNotion, mock_env):
    """Test updating both completed status and notes."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.update.return_value = {"id": "log123"}
    
    client = NotionClient()
    result = client.update_habit_log(
        log_id="log123",
        completed=True,
        notes="Completed in the morning"
    )
    
    assert result is True
    mock_instance.pages.update.assert_called_once()
    args, kwargs = mock_instance.pages.update.call_args
    assert kwargs["page_id"] == "log123"
    assert kwargs["properties"]["Tamamlandı"]["checkbox"] is True
    assert kwargs["properties"]["Notlar"]["rich_text"][0]["text"]["content"] == "Completed in the morning"


@patch("orchestration.notion_service.Client")
def test_update_habit_log_only_completed(MockNotion, mock_env):
    """Test updating only the completed status."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.update.return_value = {"id": "log456"}
    
    client = NotionClient()
    result = client.update_habit_log(
        log_id="log456",
        completed=False
    )
    
    assert result is True
    mock_instance.pages.update.assert_called_once()
    args, kwargs = mock_instance.pages.update.call_args
    assert kwargs["page_id"] == "log456"
    assert kwargs["properties"]["Tamamlandı"]["checkbox"] is False
    assert "Notlar" not in kwargs["properties"]


@patch("orchestration.notion_service.Client")
def test_update_habit_log_only_notes(MockNotion, mock_env):
    """Test updating only the notes field."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.update.return_value = {"id": "log789"}
    
    client = NotionClient()
    result = client.update_habit_log(
        log_id="log789",
        notes="Updated notes"
    )
    
    assert result is True
    mock_instance.pages.update.assert_called_once()
    args, kwargs = mock_instance.pages.update.call_args
    assert kwargs["page_id"] == "log789"
    assert kwargs["properties"]["Notlar"]["rich_text"][0]["text"]["content"] == "Updated notes"
    assert "Tamamlandı" not in kwargs["properties"]


@patch("orchestration.notion_service.Client")
def test_update_habit_log_empty_notes(MockNotion, mock_env):
    """Test updating with empty notes string."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.update.return_value = {"id": "log_empty"}
    
    client = NotionClient()
    result = client.update_habit_log(
        log_id="log_empty",
        completed=True,
        notes=""
    )
    
    assert result is True
    mock_instance.pages.update.assert_called_once()
    args, kwargs = mock_instance.pages.update.call_args
    assert kwargs["properties"]["Tamamlandı"]["checkbox"] is True
    assert kwargs["properties"]["Notlar"]["rich_text"][0]["text"]["content"] == ""


@patch("orchestration.notion_service.Client")
def test_update_habit_log_no_properties(MockNotion, mock_env):
    """Test update with no properties returns True without API call."""
    mock_instance = MockNotion.return_value
    
    client = NotionClient()
    result = client.update_habit_log(log_id="log_none")
    
    assert result is True
    mock_instance.pages.update.assert_not_called()


@patch("orchestration.notion_service.Client")
def test_update_habit_log_api_error(MockNotion, mock_env):
    """Test handling of API errors during update."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.update.side_effect = Exception("API error")
    
    client = NotionClient()
    result = client.update_habit_log(
        log_id="log_error",
        completed=True
    )
    
    assert result is False
    mock_instance.pages.update.assert_called_once()


@patch("orchestration.notion_service.Client")
def test_update_habit_log_long_notes_truncated(MockNotion, mock_env):
    """Test that notes longer than 2000 characters are truncated."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.update.return_value = {"id": "log_long"}
    
    long_notes = "A" * 3000  # Create 3000 character string
    
    client = NotionClient()
    result = client.update_habit_log(
        log_id="log_long",
        notes=long_notes
    )
    
    assert result is True
    args, kwargs = mock_instance.pages.update.call_args
    actual_notes = kwargs["properties"]["Notlar"]["rich_text"][0]["text"]["content"]
    assert len(actual_notes) == 2000
    assert actual_notes == "A" * 2000


@patch("orchestration.notion_service.Client")
def test_update_habit_log_toggle_completed_false(MockNotion, mock_env):
    """Test explicitly setting completed to False."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.update.return_value = {"id": "log_false"}
    
    client = NotionClient()
    result = client.update_habit_log(
        log_id="log_false",
        completed=False,
        notes="Decided not to do it today"
    )
    
    assert result is True
    args, kwargs = mock_instance.pages.update.call_args
    assert kwargs["properties"]["Tamamlandı"]["checkbox"] is False
    assert "Decided not to do it today" in kwargs["properties"]["Notlar"]["rich_text"][0]["text"]["content"]


@patch("orchestration.notion_service.Client")
def test_update_habit_log_with_special_characters(MockNotion, mock_env):
    """Test updating notes with special characters and emojis."""
    mock_instance = MockNotion.return_value
    mock_instance.pages.update.return_value = {"id": "log_special"}
    
    client = NotionClient()
    result = client.update_habit_log(
        log_id="log_special",
        notes="Great session! 💪 Felt amazing 🎉"
    )
    
    assert result is True
    args, kwargs = mock_instance.pages.update.call_args
    assert kwargs["properties"]["Notlar"]["rich_text"][0]["text"]["content"] == "Great session! 💪 Felt amazing 🎉"
