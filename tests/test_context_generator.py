import pytest
import json
from unittest.mock import MagicMock
from orchestration.journal_service import JournalService

def test_parse_gemini_output_json(mocker):
    # Mock NotionClient to avoid real API calls
    mock_notion = mocker.patch("orchestration.journal_service.NotionClient")
    
    journal_service = JournalService()
    
    # JSON formatted output
    json_output = {
        "raw_content": "Full session summary content",
        "emotions_detected": ["Anxiety", "Excitement"],
        "key_insights": "You are feeling overwhelmed by the new project but excited about the potential.",
        "action_items": [
            {"title": "Complete the architecture design", "priority": "P1", "status": "Aktif", "date": "2026-01-11"},
            {"title": "Draft the initial PR", "priority": "P2", "status": "Aktif", "date": "2026-01-11"},
            "Invalid item" 
        ]
    }
    raw_input = json.dumps(json_output)
    
    # Mock return values
    journal_service.notion.create_journal_entry.return_value = "dummy_page_id"
    journal_service.notion.create_task.return_value = "dummy_task_id"
    
    success = journal_service.save_journal("2026-01-11", raw_input)
    
    assert success is True
    
    # Check if create_journal_entry was called with correct insights/emotions
    journal_service.notion.create_journal_entry.assert_called_once()
    args, kwargs = journal_service.notion.create_journal_entry.call_args
    assert kwargs["emotions"] == ["Anxiety", "Excitement"]
    assert kwargs["insights"] == "You are feeling overwhelmed by the new project but excited about the potential."
    assert "Full session summary content" in kwargs["content"]
    
    # Check if tasks were created (including default P3 for non-pattern items)
    assert journal_service.notion.create_task.call_count == 3
    journal_service.notion.create_task.assert_any_call(name="Complete the architecture design", priority="P1", date="2026-01-11", status="Aktif")
    journal_service.notion.create_task.assert_any_call(name="Draft the initial PR", priority="P2", date="2026-01-11", status="Aktif")
    journal_service.notion.create_task.assert_any_call(name="Invalid item", priority="P3")

def test_parse_gemini_output_invalid_json(mocker):
    mock_notion = mocker.patch("orchestration.journal_service.NotionClient")
    journal_service = JournalService()
    
    raw_input = "Not a JSON object"
    
    success = journal_service.save_journal("2026-01-11", raw_input)
    
    # Should fail or handle gracefully. Given the change, we expect robustness.
    # If JSON fails, it should return False or handle as error.
    assert success is False

def test_parse_gemini_output_explicit_date(mocker):
    mock_notion = mocker.patch("orchestration.journal_service.NotionClient")
    journal_service = JournalService()
    
    json_output = {
        "raw_content": "Content",
        "emotions_detected": [],
        "key_insights": "",
        "action_items": []
    }
    raw_input = json.dumps(json_output)
    journal_service.notion.create_journal_entry.return_value = "dummy_id"
    
    # Use a past date
    past_date = "2025-12-25"
    success = journal_service.save_journal("Christmas", raw_input, date_str=past_date)
    
    assert success is True
    args, kwargs = journal_service.notion.create_journal_entry.call_args
    assert kwargs["date_str"] == past_date

def test_enrich_journals_with_content(mocker):
    mock_notion = mocker.patch("orchestration.journal_service.NotionClient")
    journal_service = JournalService()
    
    journals = [{"id": "j1"}, {"id": "j2"}]
    journal_service.notion.fetch_page_content.side_effect = ["Content 1", "Content 2"]
    
    enriched = journal_service.enrich_journals_with_content(journals)
    
    assert len(enriched) == 2
    assert enriched[0]["content"] == "Content 1"
    assert enriched[1]["content"] == "Content 2"
    assert journal_service.notion.fetch_page_content.call_count == 2
