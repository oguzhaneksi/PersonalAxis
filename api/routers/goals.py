from fastapi import APIRouter
from orchestration.notion_service import NotionClient

router = APIRouter(prefix="/api/goals", tags=["Goals"])

@router.get("/status")
async def get_goals_status():
    """Get status of active goals."""
    client = NotionClient()
    # Fetch all active goals (Weekly, Monthly, Quarterly, Yearly)
    goals = client.fetch_active_goals()
    return {
        "success": True, 
        "data": {
            "goals": goals
        }
    }
