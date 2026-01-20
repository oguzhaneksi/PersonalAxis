from fastapi import APIRouter
from orchestration.journal_service import JournalService
from api.schemas import QuickJournalRequest, FullJournalRequest
from datetime import datetime
from api.error_handlers import handle_notion_errors

router = APIRouter(prefix="/api/journal", tags=["Journal"])

@router.post("/quick")
@handle_notion_errors
async def quick_journal(request: QuickJournalRequest):
    """Create a quick journal entry."""
    journal_service = JournalService()
    today = datetime.now().strftime("%Y-%m-%d")
    title = request.title or f"Quick Entry {datetime.now().strftime('%H:%M')}"
    
    page_id = journal_service.save_journal_from_structured_data(
        date_str=today,
        title=title,
        content=request.content,
        insights="Mobile quick entry"
    )
    
    return {
        "success": bool(page_id),
        "data": {
            "page_id": page_id
        }
    }

@router.post("/")
@handle_notion_errors
async def save_journal(request: FullJournalRequest):
    """Save a full journal entry with AI output."""
    journal_service = JournalService()
    date_str = request.date.strftime("%Y-%m-%d") if request.date else datetime.now().strftime("%Y-%m-%d")
    
    action_items_data = []
    if request.action_items:
        for item in request.action_items:
            # Convert Pydantic model to dict and ensure date is string
            item_dict = item.model_dump()
            if item_dict.get("date"):
                item_dict["date"] = item_dict["date"].strftime("%Y-%m-%d")
            action_items_data.append(item_dict)

    page_id = journal_service.save_journal_from_structured_data(
        title=request.title,
        content=request.raw_content,
        date_str=date_str,
        emotions=request.emotions_detected,
        insights=request.key_insights,
        action_items=action_items_data
    )
    
    # Process Action Items to get names for response
    created_tasks = [item.title for item in request.action_items] if page_id and request.action_items else []
    
    return {
        "success": bool(page_id), 
        "data": {
            "page_id": page_id,
            "tasks_created": created_tasks
        }
    }
