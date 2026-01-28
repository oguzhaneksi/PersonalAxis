from typing import List, Dict, Optional
from .notion_service import NotionClient
from .habit_stats_service import HabitStatsService


class HabitService:
    """
    Handles all habit-related operations.
    """

    def __init__(self):
        self.notion = NotionClient()
        self.stats_service = HabitStatsService()

    def get_todays_habits(self) -> List[Dict]:
        """
        Fetch all active habits from Notion.
        
        Returns:
            List of habit objects.
        """
        return self.notion.fetch_active_habits()

    def log_habit_completion(
        self,
        habit_id: str,
        date_str: str,
        completed: bool,
        notes: Optional[str] = None,
        journal_id: Optional[str] = None
    ) -> Dict:
        """
        Log a habit completion and update habit statistics.
        
        Args:
            habit_id: ID of the habit
            date_str: Date in ISO format (YYYY-MM-DD)
            completed: Whether the habit was completed
            notes: Optional notes
            journal_id: Optional journal entry ID
            
        Returns:
            Dict with log_id and updated statistics.
        """
        # Check if a log entry already exists for this habit and date
        existing_logs = self.notion.fetch_habit_logs(
            habit_id=habit_id,
            start_date=date_str,
            end_date=date_str
        )
        
        log_id = None
        if existing_logs:
            # Update the existing log (take the first one if multiples exist)
            log_id = existing_logs[0]["id"]
            
            # Avoid overriding notes or journal_id with empty values if they exist
            update_params = {
                "log_id": log_id,
                "completed": completed
            }
            if notes:
                update_params["notes"] = notes
            if journal_id:
                update_params["journal_id"] = journal_id
                
            success = self.notion.update_habit_log(**update_params)
            if not success:
                raise Exception(f"Failed to update habit log {log_id}")
        else:
            # Create the habit log
            log_id = self.notion.create_habit_log(
                habit_id=habit_id,
                date_str=date_str,
                completed=completed,
                notes=notes or "",
                journal_id=journal_id
            )
            
            if not log_id:
                raise Exception("Failed to create habit log")
        
        # Fetch the specific habit by ID to get the latest properties for stats (optimized vs fetching all)
        habit = self.notion.fetch_active_habit(habit_id)
        
        if not habit:
            # Habit might be inactive or not found; skip stats update
            return {"log_id": log_id, "stats_updated": False}
        
        # Calculate updated stats
        completion_rate, streak, last_completion = self.stats_service.calculate_stats_for_habit(habit)
        
        # Update the habit with new stats
        success = self.notion.update_habit(
            habit_id=habit_id,
            completion_rate=completion_rate,
            streak=streak,
            last_completion=last_completion
        )
        
        return {
            "log_id": log_id,
            "stats_updated": success,
            "completion_rate": completion_rate,
            "streak": streak
        }

    def get_habit_history(
        self,
        habit_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch historical habit logs for a specific habit.
        
        Args:
            habit_id: ID of the habit
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format)
            
        Returns:
            List of formatted habit log entries.
        """
        logs = self.notion.fetch_habit_logs(
            habit_id=habit_id,
            start_date=start_date,
            end_date=end_date
        )
        
        formatted_logs = []
        for log in logs:
            props = log.get("properties", {})
            
            # Extract date
            date_val = None
            if "Tarih" in props and props["Tarih"].get("date"):
                date_val = props["Tarih"]["date"].get("start")
            
            # Extract completed status
            completed = props.get("Tamamlandı", {}).get("checkbox", False)
            
            # Extract notes
            notes = ""
            if "Notlar" in props and props["Notlar"].get("rich_text"):
                notes = props["Notlar"]["rich_text"][0].get("plain_text", "")
            
            formatted_logs.append({
                "id": log["id"],
                "date": date_val,
                "completed": completed,
                "notes": notes
            })
        
        return formatted_logs

    def get_all_habits_stats(self) -> List[Dict]:
        """
        Get comprehensive statistics for all active habits.
        
        Returns:
            List of habits with their statistics.
        """
        habits = self.notion.fetch_active_habits()
        
        results = []
        for habit in habits:
            props = habit.get("properties", {})
            
            # Extract basic info
            name = "Unnamed"
            if "Ad" in props and props["Ad"].get("title"):
                name = props["Ad"]["title"][0].get("plain_text", "Unnamed")
            
            frequency = "Günlük"
            if "Frekans" in props and props["Frekans"].get("select"):
                frequency = props["Frekans"]["select"].get("name", "Günlük")
            
            # Extract stats
            completion_rate = props.get("Tamamlama Oranı", {}).get("number", 0.0)
            streak = props.get("Streak", {}).get("number", 0)
            
            last_completion = None
            if "Son Tamamlama" in props and props["Son Tamamlama"].get("date"):
                last_completion = props["Son Tamamlama"]["date"].get("start")
            
            results.append({
                "id": habit["id"],
                "name": name,
                "frequency": frequency,
                "completion_rate": completion_rate,
                "streak": streak,
                "last_completion": last_completion
            })
        
        return results
