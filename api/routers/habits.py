from fastapi import APIRouter
from orchestration.habit_service import HabitService
from datetime import datetime
from api.error_handlers import handle_notion_errors

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
