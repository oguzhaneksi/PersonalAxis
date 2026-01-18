from fastapi import APIRouter, Query
from orchestration.context_generator import ContextGenerator
from datetime import datetime
from api.exceptions import InvalidReviewTypeError
from api.error_handlers import handle_notion_errors

router = APIRouter(prefix="/api/context", tags=["Context"])

@router.get("/daily")
@handle_notion_errors
async def get_daily_context():
    """Generate daily context for AI coaching."""
    generator = ContextGenerator()
    context_md = generator.generate_daily_context(return_content=True)
    return {
        "success": True,
        "data": {
            "context": context_md,
            "timestamp": datetime.now().isoformat()
        }
    }

@router.get("/review/{review_type}")
@handle_notion_errors
async def get_review_context(
    review_type: str, 
    period: str = Query(None, description="e.g., 2026-W02")
):
    """Generate periodic review context."""
    if review_type not in ["weekly", "monthly", "quarterly", "yearly"]:
        raise InvalidReviewTypeError(review_type)

    generator = ContextGenerator()
    
    # Auto-calculate period if missing
    if not period:
        today_iso = datetime.now().isoformat()
        if review_type == "weekly":
            period = generator.notion._calculate_week(today_iso)
        elif review_type == "monthly":
            period = generator.notion._calculate_month(today_iso)
        elif review_type == "quarterly":
            period = generator.notion._calculate_quarter(today_iso)
        elif review_type == "yearly":
            period = generator.notion._calculate_year(today_iso)

    context_md = generator.generate_review_context(
        review_type, period, return_content=True
    )
    
    return {
        "success": True,
        "data": {
            "review_type": review_type,
            "period": period,
            "context": context_md
        }
    }
