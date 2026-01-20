from fastapi import APIRouter, HTTPException
from api.schemas import SaveReviewRequest
from orchestration.review_service import ReviewService
from api.error_handlers import handle_notion_errors
import datetime

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

@router.post("/{review_type}")
@handle_notion_errors
async def save_review(review_type: str, request: SaveReviewRequest):
    """Save a periodic review session result to Notion."""
    
    if review_type != request.review_type:
        raise HTTPException(status_code=400, detail="Review type in URL must match body")

    review_service = ReviewService()
    
    # Calculate period for the given date
    target_dt = datetime.datetime.combine(request.date, datetime.time.min)
    period = review_service.calculate_period(review_type=review_type, target_date=target_dt)
    
    # Convert goal updates to dicts for the generator
    goal_updates_data = []
    if request.goal_updates:
        for update in request.goal_updates:
            goal_updates_data.append({
                "goal_name": update.goal_name,
                "new_status": update.new_status.value
            })

    # Save review session via review service
    page_id = review_service.save_review_from_structured_data(
        review_type=request.review_type,
        period=period,
        summary=request.review_summary,
        assessment=request.period_assessment.value,
        wins=request.wins,
        challenges=request.challenges,
        lessons_learned=request.lessons_learned,
        next_period_focus=request.next_period_focus,
        goal_updates=goal_updates_data
    )
    
    return {
        "success": bool(page_id),
        "data": {
            "page_id": page_id,
            "updated_goals": [u.goal_name for u in request.goal_updates] if page_id else []
        }
    }
