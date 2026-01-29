import pytest
from unittest.mock import patch
from orchestration.habit_service import HabitService

@pytest.fixture
def habit_service():
    with patch('orchestration.habit_service.NotionClient'), \
         patch('orchestration.habit_service.HabitStatsService'):
        service = HabitService()
        return service

def test_log_habit_completion_update_existing_no_notes_override(habit_service):
    """Test that existing notes are not overridden if provided notes are empty."""
    # Setup mocks
    mock_notion = habit_service.notion
    mock_notion.fetch_habit_logs.return_value = [{"id": "existing_log_id"}]
    mock_notion.update_habit_log.return_value = True
    
    # Mock habit retrieval and stats update to satisfy the rest of the function
    mock_notion.fetch_active_habit.return_value = {"id": "habit_id", "properties": {}}
    habit_service.stats_service.calculate_stats_for_habit.return_value = (0.5, 5, "2026-01-27")
    mock_notion.update_habit.return_value = True

    # Call with empty notes
    habit_service.log_habit_completion(
        habit_id="habit_id",
        date_str="2026-01-28",
        completed=True,
        notes="",  # Empty string
        journal_id=None
    )

    # Verify update_habit_log was called WITHOUT notes parameter
    mock_notion.update_habit_log.assert_called_once()
    args, kwargs = mock_notion.update_habit_log.call_args
    assert "notes" not in kwargs
    assert kwargs["log_id"] == "existing_log_id"
    assert kwargs["completed"] is True

def test_log_habit_completion_update_existing_with_notes(habit_service):
    """Test that existing notes ARE overridden if provided notes are NOT empty."""
    # Setup mocks
    mock_notion = habit_service.notion
    mock_notion.fetch_habit_logs.return_value = [{"id": "existing_log_id"}]
    mock_notion.update_habit_log.return_value = True
    
    mock_notion.fetch_active_habit.return_value = {"id": "habit_id", "properties": {}}
    habit_service.stats_service.calculate_stats_for_habit.return_value = (0.5, 5, "2026-01-27")
    mock_notion.update_habit.return_value = True

    # Call with non-empty notes
    habit_service.log_habit_completion(
        habit_id="habit_id",
        date_str="2026-01-28",
        completed=True,
        notes="Important new note",
        journal_id=None
    )

    # Verify update_habit_log was called WITH notes parameter
    mock_notion.update_habit_log.assert_called_once()
    args, kwargs = mock_notion.update_habit_log.call_args
    assert kwargs["notes"] == "Important new note"
    assert kwargs["log_id"] == "existing_log_id"

def test_log_habit_completion_update_existing_no_journal_override(habit_service):
    """Test that journal_id is not overridden if provided journal_id is None."""
    mock_notion = habit_service.notion
    mock_notion.fetch_habit_logs.return_value = [{"id": "existing_log_id"}]
    mock_notion.update_habit_log.return_value = True
    
    mock_notion.fetch_active_habit.return_value = {"id": "habit_id", "properties": {}}
    habit_service.stats_service.calculate_stats_for_habit.return_value = (0.5, 5, "2026-01-27")
    mock_notion.update_habit.return_value = True

    # Call with journal_id=None
    habit_service.log_habit_completion(
        habit_id="habit_id",
        date_str="2026-01-28",
        completed=True,
        notes="Keep notes",
        journal_id=None
    )

    # Verify update_habit_log was called WITHOUT journal_id
    mock_notion.update_habit_log.assert_called_once()
    args, kwargs = mock_notion.update_habit_log.call_args
    assert "journal_id" not in kwargs
    assert kwargs["notes"] == "Keep notes"

def test_log_habit_completion_update_existing_with_journal(habit_service):
    """Test that journal_id ARE overridden if provided journal_id is NOT None."""
    mock_notion = habit_service.notion
    mock_notion.fetch_habit_logs.return_value = [{"id": "existing_log_id"}]
    mock_notion.update_habit_log.return_value = True
    
    mock_notion.fetch_active_habit.return_value = {"id": "habit_id", "properties": {}}
    habit_service.stats_service.calculate_stats_for_habit.return_value = (0.5, 5, "2026-01-27")
    mock_notion.update_habit.return_value = True

    # Call with non-empty journal_id
    habit_service.log_habit_completion(
        habit_id="habit_id",
        date_str="2026-01-28",
        completed=True,
        notes="Keep notes",
        journal_id="new_journal_id"
    )

    # Verify update_habit_log was called WITH journal_id
    mock_notion.update_habit_log.assert_called_once()
    args, kwargs = mock_notion.update_habit_log.call_args
    assert kwargs["journal_id"] == "new_journal_id"
