from fastapi import APIRouter, Query
from orchestration.habit_service import HabitService
from datetime import datetime
from typing import Optional
from api.error_handlers import handle_notion_errors
from api.schemas import HabitLogRequest

router = APIRouter(prefix="/api/habits", tags=["Habits"])

@router.get("/")
@handle_notion_errors
async def get_todays_habits():
    """Get today's habit tracking status."""
    habit_service = HabitService()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Per instructions: Fetch from habits database instead of journal entry
    habits_list = habit_service.get_todays_habits()
    
    habits = []
    if habits_list:
        for h in habits_list:
            props = h.get("properties", {})
            
            # Extract name
            name = "Adsız"
            if "Ad" in props and props["Ad"].get("title"):
                name = props["Ad"]["title"][0]["plain_text"]
            
            # Extract frequency
            frequency = "Belirsiz"
            if "Frekans" in props and props["Frekans"].get("select"):
                frequency = props["Frekans"]["select"]["name"]
            
            # Extract last completion date
            last_completed = None
            if "Son Tamamlama" in props and props["Son Tamamlama"].get("date"):
                last_completed = props["Son Tamamlama"]["date"].get("start")
            
            habits.append({
                "name": name,
                "frequency": frequency,
                "last_completed": last_completed
            })
    
    return {
        "success": True,
        "data": {
            "date": today,
            "habits": habits
        }
    }


@router.post("/log")
@handle_notion_errors
async def log_habit_completion(request: HabitLogRequest):
    """
    Log a habit completion or skip.
    Creates a habit log entry and updates habit statistics.
    """
    habit_service = HabitService()
    
    result = habit_service.log_habit_completion(
        habit_id=request.habit_id,
        date_str=request.date.isoformat(),
        completed=request.completed,
        notes=request.notes,
        journal_id=request.journal_id
    )
    
    return {
        "success": True,
        "data": {
            "log_id": result["log_id"],
            "stats_updated": result["stats_updated"],
            "completion_rate": result.get("completion_rate", 0.0),
            "streak": result.get("streak", 0)
        }
    }


@router.get("/{habit_id}/history")
@handle_notion_errors
async def get_habit_history(
    habit_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Fetch historical habit completion logs for a specific habit.
    Optionally filter by date range.
    """
    habit_service = HabitService()
    
    history = habit_service.get_habit_history(
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "success": True,
        "data": {
            "habit_id": habit_id,
            "total_logs": len(history),
            "history": history
        }
    }


@router.get("/stats")
@handle_notion_errors
async def get_habits_stats():
    """
    Get comprehensive statistics for all active habits.
    Includes completion rates, streaks, and last completion dates.
    """
    habit_service = HabitService()
    
    stats = habit_service.get_all_habits_stats()
    
    return {
        "success": True,
        "data": {
            "total_habits": len(stats),
            "habits": stats
        }
    }
