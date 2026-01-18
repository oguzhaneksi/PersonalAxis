from fastapi import APIRouter, Query, HTTPException
from orchestration.context_generator import ContextGenerator
from datetime import datetime

router = APIRouter(prefix="/api/context", tags=["Context"])

@router.get("/daily")
async def get_daily_context():
    """Generate daily context for AI coaching."""
    generator = ContextGenerator()
    try:
        context_md = generator.generate_daily_context(return_content=True)
        return {
            "success": True,
            "data": {
                "context": context_md,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        # Error will be caught by global handler, but we ensure it propagates
        raise e

@router.get("/review/{review_type}")
async def get_review_context(
    review_type: str, 
    period: str = Query(None, description="e.g., 2026-W02")
):
    """Generate periodic review context."""
    if review_type not in ["weekly", "monthly", "quarterly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid review type")

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
        else:
            raise HTTPException(status_code=400, detail="Could not determine period automatically")

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
