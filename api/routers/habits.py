from fastapi import APIRouter
from orchestration.notion_service import NotionClient
from datetime import datetime

router = APIRouter(prefix="/api/habits", tags=["Habits"])

@router.get("/")
async def get_todays_habits():
    """Get today's habit tracking status."""
    client = NotionClient()
    today = datetime.now().strftime("%Y-%m-%d")
    
    entry = client.get_journal_entry(today)
    
    habits = {}
    if entry:
        props = entry.get("properties", {})
        # Scan for checkbox properties which are likely habits
        for name, prop in props.items():
            if prop["type"] == "checkbox":
                habits[name] = prop["checkbox"]
    
    return {
        "success": True,
        "data": {
            "date": today,
            "habits": habits
        }
    }
