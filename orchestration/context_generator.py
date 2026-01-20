import os
import datetime
from typing import Optional, List, Dict
from .notion_service import NotionClient
from .context_builder import ContextBuilder
from .journal_service import JournalService
from .habit_service import HabitService
from .goal_service import GoalService


class ContextGenerator:
    """
    Generates AI context from Notion data for daily coaching and periodic reviews.
    Focused solely on context generation - delegates other operations to specialized services.
    """

    def __init__(self):
        self.notion = NotionClient()
        self.builder = ContextBuilder()
        self.journal_service = JournalService()
        self.habit_service = HabitService()
        self.goal_service = GoalService()
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_daily_context(self, return_content: bool = False) -> str:
        """
        Fetches daily data, builds context, and writes to output/context.md.
        
        Args:
            return_content: If True, returns the generated markdown string instead of file path.
            
        Returns:
            File path or markdown content string
        """
        print("Fetching daily context data from Notion...")
        pillars = self.notion.fetch_all_pillars()
        goals = self.goal_service.get_active_goals()
        habits = self.habit_service.get_todays_habits()
        journals = self.notion.fetch_recent_journals(days=7)
        tasks = self.notion.fetch_tasks()

        context = self.builder.build_daily_context(
            pillars=pillars,
            goals=goals,
            habits=habits,
            recent_journals=self.journal_service.enrich_journals_with_content(journals[:5]),  # Only last 5 for daily
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
            
        Returns:
            File path or markdown content string
        """
        # Import here to avoid circular dependency
        from .review_service import ReviewService
        review_service = ReviewService()
        period = review_service.calculate_period(review_type, period)
        
        print(f"Fetching {review_type} review data for {period} from Notion...")
        
        # Map review_type to period_type in Notion
        type_map = {
            "weekly": "Haftalık",
            "monthly": "Aylık",
            "quarterly": "Çeyreklik",
            "yearly": "Yıllık"
        }
        notion_type = type_map.get(review_type, "Haftalık")

        goals = self.goal_service.get_active_goals(period_type=notion_type, period=period)
        
        # For journals, we'd ideally want to filter by the specific period.
        # For now, we'll fetch the last 30 days for any review, or we can improve filtering later.
        journals = self.notion.fetch_recent_journals(days=30) 

        context = self.builder.build_review_context(
            review_type=review_type,
            period=period,
            goals=goals,
            journals=self.journal_service.enrich_journals_with_content(journals)
        )

        if return_content:
            return context

        file_path = os.path.join(self.output_dir, f"{review_type}_{period}_context.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(context)
            
        print(f"✓ {review_type.capitalize()} review context generated: {file_path}")
        return file_path
