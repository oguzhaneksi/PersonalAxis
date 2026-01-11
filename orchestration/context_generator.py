import os
import datetime
import json
from typing import Optional
from .notion_client import NotionClient
from .context_builder import ContextBuilder

class ContextGenerator:
    """
    Orchestrates data fetching and file generation for AI context.
    """

    def __init__(self):
        self.notion = NotionClient()
        self.builder = ContextBuilder()
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_daily_context(self) -> str:
        """
        Fetches daily data, builds context, and writes to output/context.md.
        """
        print("Fetching daily context data from Notion...")
        pillars = self.notion.fetch_all_pillars()
        goals = self.notion.fetch_active_goals()
        habits = self.notion.fetch_active_habits()
        journals = self.notion.fetch_recent_journals(days=7)
        tasks = self.notion.fetch_tasks()

        context = self.builder.build_daily_context(
            pillars=pillars,
            goals=goals,
            habits=habits,
            recent_journals=journals,
            tasks=tasks
        )

        file_path = os.path.join(self.output_dir, "context.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(context)
            
        print(f"✓ Daily context generated: {file_path}")
        return file_path

    def generate_review_context(self, review_type: str, period: str) -> str:
        """
        Fetches review data and writes to output/review_context.md.
        """
        print(f"Fetching {review_type} review data for {period} from Notion...")
        
        # Map review_type to period_type in Notion
        type_map = {
            "weekly": "Haftalık",
            "monthly": "Aylık",
            "quarterly": "Çeyreklik",
            "yearly": "Yıllık"
        }
        notion_type = type_map.get(review_type, "Haftalık")

        goals = self.notion.fetch_active_goals(period_type=notion_type, period=period)
        
        # For journals, we'd ideally want to filter by the specific period.
        # For now, we'll fetch the last 30 days for any review, or we can improve filtering later.
        journals = self.notion.fetch_recent_journals(days=30) 

        context = self.builder.build_review_context(
            review_type=review_type,
            period=period,
            goals=goals,
            journals=journals
        )

        file_path = os.path.join(self.output_dir, f"{review_type}_{period}_context.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(context)
            
        print(f"✓ {review_type.capitalize()} review context generated: {file_path}")
        return file_path

    def save_journal(self, title: str, raw_input: str, date_str: Optional[str] = None) -> bool:
        """
        Parses JSON-formatted AI summary and saves to Notion.
        """

        try:
            # Attempt to parse as JSON
            # Note: AI might wrap JSON in markdown blocks, so we should try to extract it
            json_str = raw_input.strip()
            if json_str.startswith("```json"):
                json_str = json_str.replace("```json", "").replace("```", "").strip()
            elif json_str.startswith("```"):
                 json_str = json_str.replace("```", "").strip()
            
            data = json.loads(json_str)
            
            raw_content = data.get("raw_content", "")
            emotions = data.get("emotions_detected", [])
            insights = data.get("key_insights", "")
            action_items = data.get("action_items", [])
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"✗ Error: Failed to parse AI output as JSON. Please ensure Gemini provided the correct format.\nDetails: {e}")
            return False

        # Save to Notion
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            
        entry_id = self.notion.create_journal_entry(
            date_str=date_str,
            title=title,
            content=raw_content,
            emotions=emotions,
            insights=insights
        )

        if entry_id:
            print(f"✓ Journal entry saved to Notion (ID: {entry_id})")
            
            # Create tasks from action items
            for item in action_items:
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
            return True
        return False
