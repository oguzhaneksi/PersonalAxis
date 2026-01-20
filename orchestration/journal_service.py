import datetime
import json
from typing import Optional, List, Dict
from .notion_service import NotionClient
from utils.utils import parse_ai_json


class JournalService:
    """
    Handles all journal-related operations including saving entries and enriching content.
    """

    def __init__(self):
        self.notion = NotionClient()

    def save_journal(self, title: str, raw_input: str, date_str: Optional[str] = None) -> bool:
        """
        Parses JSON-formatted AI summary and saves to Notion via structural helper.
        
        Args:
            title: Title for the journal entry
            raw_input: JSON-formatted AI output
            date_str: Optional date string (YYYY-MM-DD)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = parse_ai_json(raw_input)
            
            raw_content = data.get("raw_content", "")
            emotions = data.get("emotions_detected", [])
            insights = data.get("key_insights", "")
            action_items = data.get("action_items", [])
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"✗ Error: Failed to parse AI output as JSON. Please ensure Gemini provided the correct format.\nDetails: {e}")
            return False

        # Save using structural helper
        entry_id = self.save_journal_from_structured_data(
            title=title,
            content=raw_content,
            date_str=date_str,
            emotions=emotions,
            insights=insights,
            action_items=action_items
        )

        return bool(entry_id)

    def save_journal_from_structured_data(
        self, 
        title: str, 
        content: str, 
        date_str: Optional[str] = None, 
        emotions: List[str] = None, 
        insights: str = None, 
        action_items: List[Dict] = None
    ) -> str:
        """
        Saves a journal entry and its action items to Notion.
        
        Args:
            title: Title for the journal entry
            content: Main content of the journal
            date_str: Optional date string (YYYY-MM-DD)
            emotions: List of detected emotions
            insights: Key insights from the journal
            action_items: List of action items to create as tasks
            
        Returns:
            The page ID if successful, empty string otherwise
        """
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        entry_id = self.notion.create_journal_entry(
            date_str=date_str,
            title=title,
            content=content,
            emotions=emotions,
            insights=insights
        )

        if entry_id:
            print(f"✓ Journal entry saved to Notion (ID: {entry_id})")
            
            # Create tasks from action items
            for item in (action_items or []):
                if isinstance(item, dict):
                    task_name = item.get("title", "Untitled Task")
                    priority = item.get("priority", "P3")
                    status = item.get("status", "Aktif")
                    task_date = item.get("date")
                    
                    self.notion.create_task(
                        name=task_name, 
                        priority=priority, 
                        date=task_date, 
                        status=status
                    )
                    print(f"  + Task created: {task_name} ({priority})")
                else:
                    # Fallback for unexpected formats
                    self.notion.create_task(name=str(item), priority="P3")
                    print(f"  + Task created: {item} (P3 - Default)")
        
        return entry_id

    def enrich_journals_with_content(self, journals: List[Dict]) -> List[Dict]:
        """
        Fetches page content for a list of journal entries.
        
        Args:
            journals: List of journal entry dictionaries
            
        Returns:
            The same list with 'content' field added to each entry
        """
        print(f"Enriching {len(journals)} journal entries with content...")
        for j in journals:
            page_id = j["id"]
            content = self.notion.fetch_page_content(page_id)
            # Add content to the journal object for the builder to use
            j["content"] = content
        return journals
