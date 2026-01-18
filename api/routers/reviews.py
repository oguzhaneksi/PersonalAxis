from fastapi import APIRouter, HTTPException
from api.schemas import SaveReviewRequest
from orchestration.notion_service import NotionClient

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

@router.post("/{review_type}")
async def save_review(review_type: str, request: SaveReviewRequest):
    """Save a periodic review session result to Notion."""
    
    if review_type != request.review_type:
        raise HTTPException(status_code=400, detail="Review type in URL must match body")

    client = NotionClient()
    
    # We need to adapt the rich request object to the simpler NotionClient signature,
    # or extend NotionClient. For now, we'll format the summary to include the extra fields.
    
    full_summary = request.review_summary
    full_summary += f"\n\n### Lessons Learned\n{request.lessons_learned}"
    
    if request.next_period_focus:
        full_summary += "\n\n### Next Period Focus\n" + "\n".join([f"- {item}" for item in request.next_period_focus])

    # Save main review
    page_id = client.save_review_session(
        review_type=request.review_type,
        date_str=request.date.strftime("%Y-%m-%d"),
        content=full_summary,
        # Rating is not in the new schema, so we default or omit. 
        # Wait, schematic doesn't have rating. We should pass None.
        rating=None, 
        # emotions not in schema anymore? Wait, user provided schemas doesn't have emotions in SaveReviewRequest?
        # Checking user provided schema... "SaveReviewRequest" has no emotions.
        emotions=None
    )
    
    # Process Goal Updates
    updated_goals = []
    if request.goal_updates:
        for update in request.goal_updates:
            goal_id = client.find_goal_by_name(update.goal_name)
            if goal_id:
                notion_status = update.new_status.value
                
                if client.update_goal_progress(goal_id, status=notion_status):
                    updated_goals.append(update.goal_name)
            else:
                print(f"Goal not found: {update.goal_name}")

    return {
        "success": bool(page_id),
        "data": {
            "page_id": page_id,
            "updated_goals": updated_goals
        }
    }
