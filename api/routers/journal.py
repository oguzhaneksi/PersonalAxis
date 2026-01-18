from fastapi import APIRouter
from orchestration.notion_service import NotionClient
from api.schemas import QuickJournalRequest, FullJournalRequest
from datetime import datetime
from api.error_handlers import handle_notion_errors

router = APIRouter(prefix="/api/journal", tags=["Journal"])

@router.post("/quick")
@handle_notion_errors
async def quick_journal(request: QuickJournalRequest):
    """Create a quick journal entry."""
    client = NotionClient()
    today = datetime.now().strftime("%Y-%m-%d")
    title = request.title or f"Quick Entry {datetime.now().strftime('%H:%M')}"
    
    page_id = client.create_journal_entry(
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
    client = NotionClient()
    date_str = request.date.strftime("%Y-%m-%d") if request.date else datetime.now().strftime("%Y-%m-%d")
    
    page_id = client.create_journal_entry(
        date_str=date_str,
        title=request.title,
        content=request.raw_content,
        emotions=request.emotions_detected,
        insights=request.key_insights
    )
    
    # Process Action Items if any
    created_tasks = []
    if page_id and request.action_items:
        for item in request.action_items:
            task_id = client.create_task(
                name=item.title,
                priority=item.priority,
                date=item.date.strftime("%Y-%m-%d"),
                status=item.status
            )
            if task_id:
                created_tasks.append(item.title)
    
    return {
        "success": bool(page_id), 
        "data": {
            "page_id": page_id,
            "tasks_created": created_tasks
        }
    }
