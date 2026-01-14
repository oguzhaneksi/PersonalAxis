import pytest
from click.testing import CliRunner
from orchestration.main import cli
from unittest.mock import MagicMock, patch
import datetime

@pytest.fixture
def runner():
    return CliRunner()

def test_daily_context_cli(runner, mocker):
    mock_gen = mocker.patch("orchestration.main.ContextGenerator")
    mock_gen.return_value.generate_daily_context.return_value = "output/context.md"
    
    result = runner.invoke(cli, ["daily-context"])
    
    assert result.exit_code == 0
    assert "Success! Context is ready at: output/context.md" in result.output
    mock_gen.return_value.generate_daily_context.assert_called_once()

def test_daily_context_cli_with_notify(runner, mocker):
    mock_gen = mocker.patch("orchestration.main.ContextGenerator")
    mock_notify = mocker.patch("orchestration.main.notify")
    mock_gen.return_value.generate_daily_context.return_value = "output/context.md"
    
    result = runner.invoke(cli, ["daily-context", "--notify"])
    
    assert result.exit_code == 0
    mock_notify.assert_called_once_with("PersonalAxis", "Daily context generation completed.")

def test_daily_context_cli_failure_with_notify(runner, mocker):
    mock_gen = mocker.patch("orchestration.main.ContextGenerator")
    mock_notify = mocker.patch("orchestration.main.notify")
    mock_gen.return_value.generate_daily_context.side_effect = Exception("Notion API Error")
    
    result = runner.invoke(cli, ["daily-context", "--notify"])
    
    assert result.exit_code == 0 # We catch the exception in the CLI
    assert "Error: Notion API Error" in result.output
    mock_notify.assert_called_once_with("PersonalAxis Error", "Daily context failed: Notion API Error")

def test_review_context_cli_last_period(runner, mocker):
    mock_gen = mocker.patch("orchestration.main.ContextGenerator")
    mock_notion_class = mocker.patch("orchestration.notion_service.NotionClient")
    mock_notion = mock_notion_class.return_value
    
    # Mock datetime to a specific date (Wednesday, Jan 14, 2026)
    fixed_now = datetime.datetime(2026, 1, 14)
    mocker.patch("orchestration.main.datetime.datetime", mocker.Mock(now=lambda: fixed_now))
    
    # Mock period calculation
    mock_notion._calculate_week.return_value = "2026-W02" # Week before 2026-W03
    
    # Running weekly review for 'last' period
    result = runner.invoke(cli, ["review-context", "--type", "weekly", "--period", "last"])
    
    assert result.exit_code == 0
    # For weekly 'last', it should subtract 7 days from Jan 14 -> Jan 7
    # calculate_week should be called for Jan 7
    mock_notion._calculate_week.assert_called_once_with("2026-01-07")

def test_quick_journal_cli(runner, mocker):
    mock_notion_class = mocker.patch("orchestration.notion_service.NotionClient")
    mock_notion = mock_notion_class.return_value
    mock_notion.create_journal_entry.return_value = "new_page_id"
    
    # Simulating piping content
    result = runner.invoke(cli, ["quick-journal"], input="This is a quick test entry\nWith multiple lines.")
    
    assert result.exit_code == 0
    assert "Successfully saved quick journal entry!" in result.output
    mock_notion.create_journal_entry.assert_called_once()
    args, kwargs = mock_notion.create_journal_entry.call_args
    assert "This is a quick test entry" in kwargs["content"]
    assert "With multiple lines." in kwargs["content"]

def test_goal_status_cli(runner, mocker):
    mock_notion_class = mocker.patch("orchestration.notion_service.NotionClient")
    mock_notion = mock_notion_class.return_value
    mock_notion.fetch_active_goals.return_value = [
        {
            "properties": {
                "Ad": {"title": [{"plain_text": "Goal 1"}]},
                "Durum": {"select": {"name": "Devam Ediyor"}}
            }
        },
        {
            "properties": {
                "Ad": {"title": [{"plain_text": "Goal 2"}]},
                "Durum": {"select": {"name": "Başlanmadı"}}
            }
        }
    ]
    
    result = runner.invoke(cli, ["goal-status"])
    
    assert result.exit_code == 0
    assert "--- Aktif Hedefler ---" in result.output
    assert "• Goal 1 [Devam Ediyor]" in result.output
    assert "• Goal 2 [Başlanmadı]" in result.output

def test_notify_helper(mocker):
    from orchestration.main import notify
    mock_run = mocker.patch("subprocess.run")
    
    notify("Test Title", "Test Message")
    
    mock_run.assert_called_once()
    # Check if osascript was called with correctly escaped string
    args = mock_run.call_args[0][0]
    assert "osascript" in args
    assert "display notification \"Test Message\" with title \"Test Title\"" in args[2]
