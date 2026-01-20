from fastapi import APIRouter
from orchestration.goal_service import GoalService
from api.error_handlers import handle_notion_errors

router = APIRouter(prefix="/api/goals", tags=["Goals"])

@router.get("/status")
@handle_notion_errors
async def get_goals_status():
    """Get status of active goals."""
    goal_service = GoalService()
    # Fetch all active goals (Weekly, Monthly, Quarterly, Yearly)
    goals = goal_service.get_active_goals()
    return {
        "success": True, 
        "data": {
            "goals": goals
        }
    }
