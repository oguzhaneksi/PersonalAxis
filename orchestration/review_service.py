import datetime
import json
from typing import Optional, List, Dict
from .notion_service import NotionClient
from utils.utils import parse_ai_json


class ReviewService:
    """
    Handles all review-related operations including saving review sessions and updating goals.
    """

    def __init__(self):
        self.notion = NotionClient()

    def calculate_period(self, review_type: str, period: Optional[str] = None, target_date: Optional[datetime.datetime] = None) -> str:
        """
        Calculates the period string based on review_type and optional period hint or target_date.
        Supports 'last' for previous period and None for current period.
        
        Args:
            review_type: Type of review (weekly, monthly, quarterly, yearly)
            period: Period identifier (e.g. 2026-W01) or "last" or None
            target_date: Optional target date to calculate period from
            
        Returns:
            Period string (e.g., "2026-W01", "2026-01", "2026-Q1", "2026")
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
            period = None  # Trigger calculation based on target_date

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

    def save_review(self, review_type: str, period: Optional[str] = None, raw_input: str = "") -> bool:
        """
        Parses JSON-formatted AI review summary and saves to Notion via structural helper.
        
        Args:
            review_type: Type of review (weekly, monthly, quarterly, yearly)
            period: Period identifier or "last" or None
            raw_input: JSON-formatted AI output
            
        Returns:
            True if successful, False otherwise
        """
        period = self.calculate_period(review_type, period)
        
        try:
            data = parse_ai_json(raw_input)
            
            
            summary = data.get("review_summary", "")
            assessment = data.get("period_assessment", "Karışık")
            wins = data.get("wins", [])
            challenges = data.get("challenges", [])
            lessons_learned = data.get("lessons_learned", "")
            next_period_focus = data.get("next_period_focus", [])
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
            lessons_learned=lessons_learned,
            next_period_focus=next_period_focus,
            goal_updates=goal_updates
        )

        return bool(review_id)

    def save_review_from_structured_data(
        self, 
        review_type: str, 
        period: str, 
        summary: str, 
        assessment: str, 
        wins: List[str] = None, 
        challenges: List[str] = None, 
        lessons_learned: str = None,
        next_period_focus: List[str] = None,
        goal_updates: List[Dict] = None
    ) -> str:
        """
        Saves a review session and updates associated goals.
        
        Args:
            review_type: Type of review (weekly, monthly, quarterly, yearly)
            period: Period identifier
            summary: Review summary text
            assessment: Period assessment (Başarılı, Normal, Karışık, Zorlayıcı)
            wins: List of wins/achievements
            challenges: List of challenges faced
            lessons_learned: Key takeaways
            next_period_focus: Focus items for the next period
            goal_updates: List of goal update dictionaries
            
        Returns:
            The page ID if successful, empty string otherwise
        """
        review_id = self.notion.create_review_session(
            review_type=review_type,
            period=period,
            summary=summary,
            assessment=assessment,
            wins=wins,
            challenges=challenges,
            lessons_learned=lessons_learned,
            next_period_focus=next_period_focus
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
