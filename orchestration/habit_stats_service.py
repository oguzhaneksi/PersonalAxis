import datetime
from typing import Dict, Optional, Tuple
from .notion_service import NotionClient
from .util import safe_get_text


class HabitStatsService:
    """
    Calculates and updates habit statistics based on habit logs.
    Computes streaks, completion rates, and updates habit records.
    """

    def __init__(self):
        self.notion = NotionClient()

    def _parse_date(self, date_str: str) -> Optional[datetime.date]:
        """Parse ISO date string to date object."""
        if not date_str:
            return None
        try:
            return datetime.datetime.fromisoformat(date_str).date()
        except (ValueError, AttributeError, TypeError):
            return None

    def calculate_streak(self, habit_id: str, frequency: str) -> int:
        """
        Calculate the current consecutive completion streak for a habit.
        
        Args:
            habit_id: ID of the habit
            frequency: Habit frequency (Günlük, Haftalık, Aylık)
            
        Returns:
            Current streak count (number of consecutive periods completed).
        """
        # Fetch all habit logs for this habit, sorted by date descending
        logs = self.notion.fetch_habit_logs(habit_id=habit_id)
        
        if not logs:
            return 0

        # Filter only completed logs and parse dates
        completed_dates = []
        for log in logs:
            completed = log["properties"].get("Tamamlandı", {}).get("checkbox", False)
            if completed:
                date_str = safe_get_text(log["properties"].get("Tarih", {}))
                date_obj = self._parse_date(date_str)
                if date_obj:
                    completed_dates.append(date_obj)
        
        if not completed_dates:
            return 0

        # Sort dates in descending order (most recent first)
        completed_dates.sort(reverse=True)
        
        # Calculate streak based on frequency
        streak = 0
        today = datetime.date.today()
        
        if frequency == "Günlük":
            # Check consecutive days
            expected_date = today
            for comp_date in completed_dates:
                # Allow completion on today or yesterday to maintain streak
                if comp_date == expected_date:
                    streak += 1
                    expected_date = comp_date - datetime.timedelta(days=1)
                elif comp_date == expected_date - datetime.timedelta(days=1):
                    streak += 1
                    expected_date = comp_date - datetime.timedelta(days=1)
                else:
                    break
                    
        elif frequency == "Haftalık":
            # Check consecutive weeks (ISO week numbers)
            current_week = today.isocalendar()[1]
            current_year = today.isocalendar()[0]
            expected_week = current_week
            expected_year = current_year
            
            for comp_date in completed_dates:
                comp_week = comp_date.isocalendar()[1]
                comp_year = comp_date.isocalendar()[0]
                
                # Check if this date falls in the expected week
                if comp_year == expected_year and comp_week == expected_week:
                    streak += 1
                    # Move to previous week
                    expected_week -= 1
                    if expected_week < 1:
                        expected_week = 52  # Approximate
                        expected_year -= 1
                else:
                    break
                    
        elif frequency == "Aylık":
            # Check consecutive months
            current_month = today.month
            current_year = today.year
            expected_month = current_month
            expected_year = current_year
            
            for comp_date in completed_dates:
                comp_month = comp_date.month
                comp_year = comp_date.year
                
                if comp_year == expected_year and comp_month == expected_month:
                    streak += 1
                    # Move to previous month
                    expected_month -= 1
                    if expected_month < 1:
                        expected_month = 12
                        expected_year -= 1
                else:
                    break
        
        return streak

    def calculate_completion_rate(
        self, 
        habit_id: str, 
        period_days: int, 
        frequency: str
    ) -> float:
        """
        Calculate the completion rate for a habit over a given period.
        
        Args:
            habit_id: ID of the habit
            period_days: Number of days to look back (e.g., 7, 30)
            frequency: Habit frequency (Günlük, Haftalık, Aylık)
            
        Returns:
            Completion rate as a decimal (0.0-1.0) for Notion percent field.
        """
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=period_days)
        
        # Fetch logs for the period
        logs = self.notion.fetch_habit_logs(
            habit_id=habit_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        if not logs:
            return 0.0

        # Count completed logs
        completed_count = 0
        for log in logs:
            completed = log["properties"].get("Tamamlandı", {}).get("checkbox", False)
            if completed:
                completed_count += 1
        
        # Calculate expected completions based on frequency
        if frequency == "Günlük":
            expected_count = period_days
        elif frequency == "Haftalık":
            expected_count = period_days // 7
        elif frequency == "Aylık":
            expected_count = period_days // 30
        else:
            expected_count = period_days  # Default to daily
        
        if expected_count == 0:
            return 0.0
        
        # Return as decimal (0.0-1.0) for Notion percent field
        rate = completed_count / expected_count
        return min(rate, 1.0)  # Cap at 1.0 (100%)

    def get_last_completion_date(self, habit_id: str) -> Optional[str]:
        """
        Get the most recent completion date for a habit.
        
        Args:
            habit_id: ID of the habit
            
        Returns:
            ISO date string of last completion, or None if never completed.
        """
        logs = self.notion.fetch_habit_logs(habit_id=habit_id)
        
        for log in logs:
            completed = log["properties"].get("Tamamlandı", {}).get("checkbox", False)
            if completed:
                date_str = safe_get_text(log["properties"].get("Tarih", {}))
                if date_str:
                    return date_str
        
        return None

    def calculate_stats_for_habit(self, habit: Dict) -> Tuple[float, int, Optional[str]]:
        """
        Calculate all statistics for a single habit.
        
        Args:
            habit: Habit object from Notion
            
        Returns:
            Tuple of (completion_rate, streak, last_completion_date)
        """
        habit_id = habit["id"]
        frequency = safe_get_text(habit["properties"].get("Frekans", {}))
        
        # Default to Günlük if frequency is missing
        if not frequency:
            frequency = "Günlük"
        
        # Calculate stats
        streak = self.calculate_streak(habit_id, frequency)
        completion_rate = self.calculate_completion_rate(habit_id, 30, frequency)  # Last 30 days
        last_completion = self.get_last_completion_date(habit_id)
        
        return completion_rate, streak, last_completion

    def calculate_stats_for_all_habits(self) -> Dict[str, Dict]:
        """
        Calculate and update statistics for all active habits.
        
        Returns:
            Dictionary mapping habit IDs to their calculated stats.
        """
        print("Fetching active habits...")
        habits = self.notion.fetch_active_habits()
        
        if not habits:
            print("No active habits found.")
            return {}
        
        print(f"Calculating stats for {len(habits)} habits...")
        results = {}
        
        for habit in habits:
            habit_id = habit["id"]
            habit_name = safe_get_text(habit["properties"].get("Ad", {}))
            
            try:
                completion_rate, streak, last_completion = self.calculate_stats_for_habit(habit)
                
                # Update the habit in Notion
                success = self.notion.update_habit(
                    habit_id=habit_id,
                    completion_rate=completion_rate,
                    streak=streak,
                    last_completion=last_completion
                )
                
                if success:
                    print(f"✓ {habit_name}: {completion_rate * 100:.1f}% rate, {streak} streak")
                    results[habit_id] = {
                        "name": habit_name,
                        "completion_rate": completion_rate,
                        "streak": streak,
                        "last_completion": last_completion
                    }
                else:
                    print(f"✗ Failed to update {habit_name}")
                    
            except Exception as e:
                print(f"✗ Error calculating stats for {habit_name}: {e}")
        
        print(f"\nCompleted: {len(results)}/{len(habits)} habits updated successfully.")
        return results
