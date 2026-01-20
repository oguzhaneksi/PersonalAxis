import os
import datetime
import json
from typing import Optional, List, Dict
from .notion_service import NotionClient
from .context_builder import ContextBuilder
from utils.utils import parse_ai_json

class ContextGenerator:
    """
    Orchestrates data fetching and file generation for AI context.
    """

    def __init__(self):
        self.notion = NotionClient()
        self.builder = ContextBuilder()
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_period(self, review_type: str, period: Optional[str] = None, target_date: Optional[datetime.datetime] = None) -> str:
        """
        Calculates the period string based on review_type and optional period hint or target_date.
        Supports 'last' for previous period and None for current period.
        """
        if not target_date:
            target_date = datetime.datetime.now()
        
        if period == "last":
            if review_type == "weekly":
                target_date -= datetime.timedelta(days=7)
            elif review_type == "monthly":
                # First day of this month then minus one day
                target_date = target_date.replace(day=1) - datetime.timedelta(days=1)
            elif review_type == "quarterly":
                # Subtract 3 months
                month = target_date.month - 3
                year = target_date.year
                if month <= 0:
                    month += 12
                    year -= 1
                target_date = target_date.replace(year=year, month=month)
            elif review_type == "yearly":
                target_date = target_date.replace(year=target_date.year - 1)
            period = None # Trigger calculation based on target_date

        if not period:
            date_str = target_date.strftime("%Y-%m-%d")
            if review_type == "weekly":
                return self.notion._calculate_week(date_str)
            elif review_type == "monthly":
                return self.notion._calculate_month(date_str)
            elif review_type == "quarterly":
                return self.notion._calculate_quarter(date_str)
            elif review_type == "yearly":
                return self.notion._calculate_year(date_str)
        
        return period

    def generate_daily_context(self, return_content: bool = False) -> str:
        """
        Fetches daily data, builds context, and writes to output/context.md.
        
        Args:
            return_content: If True, returns the generated markdown string instead of file path.
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
            recent_journals=self._enrich_journals_with_content(journals[:5]), # Only last 5 for daily
            tasks=tasks
        )

        if return_content:
            return context

        file_path = os.path.join(self.output_dir, "context.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(context)
            
        print(f"✓ Daily context generated: {file_path}")
        return file_path

    def generate_review_context(self, review_type: str, period: Optional[str] = None, return_content: bool = False) -> str:
        """
        Fetches review data and writes to output/review_context.md.
        
        Args:
            review_type: Type of review (weekly, monthly, quarterly, yearly)
            period: Period identifier (e.g. 2026-W01) or "last" or None
            return_content: If True, returns generated markdown string.
        """
        period = self.get_period(review_type, period)
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
            journals=self._enrich_journals_with_content(journals)
        )

        if return_content:
            return context

        file_path = os.path.join(self.output_dir, f"{review_type}_{period}_context.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(context)
            
        print(f"✓ {review_type.capitalize()} review context generated: {file_path}")
        return file_path

    def save_journal(self, title: str, raw_input: str, date_str: Optional[str] = None) -> bool:
        """
        Parses JSON-formatted AI summary and saves to Notion via structural helper.
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

    def save_journal_from_structured_data(self, title: str, content: str, date_str: Optional[str] = None, emotions: List[str] = None, insights: str = None, action_items: List[Dict] = None) -> str:
        """
        Saves a journal entry and its action items to Notion.
        Returns the page ID.
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

    def _enrich_journals_with_content(self, journals: List[Dict]) -> List[Dict]:
        """
        Helper to fetch page content for a list of journal entries.
        """
        print(f"Enriching {len(journals)} journal entries with content...")
        for j in journals:
            page_id = j["id"]
            content = self.notion.fetch_page_content(page_id)
            # Add content to the journal object for the builder to use
            j["content"] = content
        return journals

    def save_review(self, review_type: str, period: Optional[str] = None, raw_input: str = "") -> bool:
        """
        Parses JSON-formatted AI review summary and saves to Notion via structural helper.
        """
        period = self.get_period(review_type, period)
        try:
            data = parse_ai_json(raw_input)
            
            summary = data.get("review_summary", "")
            assessment = data.get("period_assessment", "Karışık")
            wins = data.get("wins", [])
            challenges = data.get("challenges", [])
            goal_updates = data.get("goal_updates", [])
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"✗ Error: Failed to parse AI review output as JSON.\nDetails: {e}")
            return False

        # Save using structural helper
        review_id = self.save_review_from_structured_data(
            review_type=review_type,
            period=period,
            summary=summary,
            assessment=assessment,
            wins=wins,
            challenges=challenges,
            goal_updates=goal_updates
        )

        return bool(review_id)

    def save_review_from_structured_data(self, review_type: str, period: str, summary: str, assessment: str, wins: List[str] = None, challenges: List[str] = None, goal_updates: List[Dict] = None) -> str:
        """
        Saves a review session and updates associated goals.
        Returns the page ID.
        """
        review_id = self.notion.create_review_session(
            review_type=review_type,
            period=period,
            summary=summary,
            assessment=assessment,
            wins=wins,
            challenges=challenges
        )

        if review_id:
            print(f"✓ Review session saved to Notion (ID: {review_id})")
            
            # Update goals
            for update in (goal_updates or []):
                goal_name = update.get("goal_name")
                new_status = update.get("new_status")
                
                if goal_name and new_status:
                    # Search for goal ID by name
                    goal_id = self.notion.find_goal_by_name(goal_name)
                    if goal_id:
                        if self.notion.update_goal_progress(goal_id, status=new_status):
                            print(f"  + Goal updated: {goal_name} -> {new_status}")
                        else:
                            print(f"  - Failed to update goal: {goal_name}")
                    else:
                        print(f"  - Goal not found: {goal_name}")
        return review_id
