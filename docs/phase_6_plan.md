# Phase 6 Implementation Plan: Mobile Access (iOS First)

Phase 5 is complete. The system is now fully functional as a CLI. Now we add mobile access.

## 📋 Executive Summary

**Goal:** Run PersonalAxis CLI commands from mobile devices (prioritize iOS).

**Strategy:** REST API + PWA (with iOS Shortcuts as bonus)

### ✅ Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Deployment | Cloudflare Tunnel | Free, data stays local, perfect for private MVP |
| Initial Scope | API + PWA | More useful than Shortcuts alone, 2-3 weeks |
| Security | API Key + Cloudflare Access | Balance of simplicity and security |
| PWA Design | Minimal → Dashboard | Start simple, iterate to dashboard |
| Domain | Random Cloudflare subdomain | Acceptable for MVP, custom domain later |

---

## 🎯 Requirements Analysis

### Existing CLI Commands (to be wrapped)

| Command | HTTP Method | Endpoint | Complexity |
|--------:|------------:|---------:|-----------:|
| `daily-context` | GET | `/api/context/daily` | Low |
| `review-context --type X` | GET | `/api/context/review/{type}` | Low |
| `quick-journal` | POST | `/api/journal/quick` | Low |
| `goal-status` | GET | `/api/goals/status` | Low |
| `habits` | GET | `/api/habits` | Low |
| `save-journal` | POST | `/api/journal` | Medium |
| `save-review` | POST | `/api/reviews/{type}` | Medium |

### Mobile Usage Scenarios

1. **Morning Routine:** Generate daily context → send to AI (copy/share)
2. **Quick Journal:** Add a thought/note (one tap)
3. **Goal Check:** View active goals
4. **Weekly Review:** Generate review context, save result
5. **Habit Tracking:** View/mark today's habits

---

## 🚧 Potential Obstacles & Solutions

### 1. **Server Hosting** ✅ DECIDED
- **Problem:** CLI currently runs locally; mobile access needs a server
- **Solution:** Cloudflare Tunnel (free, data remains local)
- **Fallback:** If Mac sleeps, API unavailable → document wake schedule or use Amphetamine app

### 2. **Authentication / Security** ✅ DECIDED
- **Problem:** Exposing API to the internet is a security risk
- **Solution:** API Key + Cloudflare Access combination
  - API Key: Simple header-based auth for all requests
  - Cloudflare Access: Zero-trust layer, device/email verification
- **Implementation:** 
  1. Generate strong API key (32+ chars)
  2. Configure Cloudflare Access policy (email allowlist)
  3. Both layers must pass for request to succeed

### 3. **Notion Token Security** ✅ SOLVED
- **Problem:** NOTION_TOKEN must remain server-side, not leak to clients
- **Solution:** Keep token only on backend; API acts as a proxy ✅

### 4. **iOS PWA Limitations**
- **Problem:** iOS Safari has PWA restrictions (no push, limited background)
- **Mitigations:**
  - Use "Add to Home Screen" for app-like experience
  - Implement pull-to-refresh instead of push
  - iOS Shortcuts as optional power-user feature

### 5. **Offline Usage** → Phase 7
- **Problem:** Notion API requires internet
- **Current approach:** Show clear "offline" state in PWA
- **Future:** Local SQLite cache with sync

---

## 🏗️ Architecture Design

```
┌──────────────────────────────────────────────────────────────────┐
│                        MOBILE CLIENTS                            │
├──────────────────┬──────────────────┬───────────────────────────┤
│   iOS Shortcuts  │   PWA (Safari)   │   Native App (Future)     │
└────────┬─────────┴────────┬─────────┴─────────────┬─────────────┘
         │                  │                       │
         └──────────────────┼───────────────────────┘
                            │ HTTPS
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE TUNNEL                             │
│                   (*.trycloudflare.com)                          │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│                   (localhost:8000)                               │
├──────────────────────────────────────────────────────────────────┤
│  /api/context/*     │  /api/journal/*   │  /api/goals/*         │
│  /api/habits/*      │  /api/reviews/*   │  /api/health          │
├──────────────────────────────────────────────────────────────────┤
│                  Existing Orchestration Layer                    │
│     (notion_service.py, context_builder.py, context_generator)   │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                       NOTION API                                 │
│                   (api.notion.com)                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📱 Mobile Access Strategy (Refined)

### Primary: PWA + REST API (2-3 weeks)
Main deliverable. Works on iOS Safari, Android Chrome, and desktop browsers.

**PWA v1.0 (Minimal)**
- 6 action buttons (one per main function)
- Simple response display (copy/share)
- Basic loading/error states
- "Add to Home Screen" instructions

**PWA v1.1 (Dashboard) - Future iteration**
- Activity feed / recent actions
- Goal progress visualization
- Habit streak display
- Quick stats

### Secondary: iOS Shortcuts (Bonus, Week 3)
Optional power-user feature. Not required for MVP but easy to add once API exists.

### Deferred: Native iOS App → Phase 7+
Only if PWA proves insufficient for daily use.

---

## 📁 File Structure (Refined)

```
PersonalAxis/
├── api/                          # NEW: FastAPI Backend
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry + router includes
│   ├── config.py                 # Settings, env loading
│   ├── auth.py                   # API key middleware
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── context.py           # /api/context/* endpoints
│   │   ├── journal.py           # /api/journal/* endpoints
│   │   ├── goals.py             # /api/goals/* endpoints
│   │   ├── habits.py            # /api/habits/* endpoints
│   │   └── reviews.py           # /api/reviews/* endpoints
│   └── schemas.py               # Pydantic request/response models
│
├── web/                          # NEW: PWA Frontend
│   ├── index.html               # Single page app
│   ├── manifest.json            # PWA manifest
│   ├── sw.js                    # Service Worker (offline handling)
│   ├── css/
│   │   └── app.css              # Mobile-first styles
│   ├── js/
│   │   └── app.js               # API client + UI logic
│   └── icons/                   # PWA icons (192x192, 512x512)
│
├── deployment/                   # NEW: Deployment configs
│   ├── cloudflare/
│   │   ├── tunnel-config.yml    # Tunnel configuration
│   │   └── access-policy.md     # Cloudflare Access setup guide
│   └── launchd/
│       ├── com.personalaxis.api.plist      # API server autostart
│       └── com.personalaxis.tunnel.plist   # Tunnel autostart
│
├── orchestration/               # EXISTING (minor modifications)
│   ├── context_generator.py     # Add return_content parameter
│   └── ...
│
├── tests/                       # EXISTING + NEW
│   ├── test_api.py              # NEW: API unit tests
│   ├── test_api_integration.py  # NEW: Integration tests
│   └── ...
│
├── automation/                  # EXISTING (unchanged)
├── prompts/                     # EXISTING (unchanged)
└── docs/                        # EXISTING
```

**Note:** `ios/shortcuts/` directory removed from MVP scope. iOS Shortcuts are optional and can be created manually using the API documentation.

---

## 🔧 Detailed Implementation Plan

### Task 6.1: FastAPI Backend (Core API)

#### 6.1.1 Dependencies

```python
# requirements.txt additions
fastapi==0.128.0
uvicorn[standard]==0.40.0
pydantic==2.12.5
python-multipart==0.0.21  # for form data
```

#### 6.1.2 API Endpoints

```python
# api/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PersonalAxis API",
    description="AI-Powered Life OS - Mobile API",
    version="1.0.0"
)

# CORS for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
```

#### 6.1.3 Context Router

```python
# api/routers/context.py
from fastapi import APIRouter, Query
from orchestration.context_generator import ContextGenerator

router = APIRouter(prefix="/api/context", tags=["Context"])

@router.get("/daily")
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
async def get_review_context(
    review_type: str,  # weekly, monthly, quarterly, yearly
    period: str = Query(None, description="e.g., 2026-W02")
):
    """Generate periodic review context."""
    generator = ContextGenerator()
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
```

#### 6.1.4 Journal Router

```python
# api/routers/journal.py
from fastapi import APIRouter
from pydantic import BaseModel
from orchestration.notion_service import NotionClient

router = APIRouter(prefix="/api/journal", tags=["Journal"])

class QuickJournalRequest(BaseModel):
    content: str
    title: str | None = None

@router.post("/quick")
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

class FullJournalRequest(BaseModel):
    title: str
    content: str
    date: str | None = None
    emotions: list[str] | None = None
    insights: str | None = None

@router.post("/")
async def save_journal(request: FullJournalRequest):
    """Save a full journal entry with AI output."""
    client = NotionClient()
    date_str = request.date or datetime.now().strftime("%Y-%m-%d")
    
    page_id = client.create_journal_entry(
        date_str=date_str,
        title=request.title,
        content=request.content,
        emotions=request.emotions,
        insights=request.insights
    )
    
    return {
        "success": bool(page_id), 
        "data": {
            "page_id": page_id
        }
    }
```

#### 6.1.5 Goals Router

```python
# api/routers/goals.py
from fastapi import APIRouter
from orchestration.notion_service import NotionClient

router = APIRouter(prefix="/api/goals", tags=["Goals"])

@router.get("/status")
async def get_goals_status():
    """Get status of active goals (Quarterly & Weekly)."""
    client = NotionClient()
    # Fetch active goals for current period
    goals = client.get_active_goals_summary()
    return {
        "success": True, 
        "data": {
            "goals": goals
        }
    }
```

#### 6.1.6 Habits Router

```python
# api/routers/habits.py
from fastapi import APIRouter
from orchestration.notion_service import NotionClient
from datetime import datetime

router = APIRouter(prefix="/api/habits", tags=["Habits"])

@router.get("/")
async def get_todays_habits():
    """Get today's habit tracking status."""
    client = NotionClient()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get or create today's journal entry to read habits
    entry = client.get_journal_entry(today)
    
    return {
        "success": True,
        "data": {
            "date": today,
            "habits": entry.get("habits", {}) if entry else {}
        }
    }
```

#### 6.1.7 Reviews Router

```python
# api/routers/reviews.py
from fastapi import APIRouter
from pydantic import BaseModel
from orchestration.notion_service import NotionClient

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

class SaveReviewRequest(BaseModel):
    review_type: str  # weekly, monthly, quarterly, yearly
    date: str
    content: str
    rating: int | None = None
    emotions: list[str] | None = None

@router.post("/{review_type}")
async def save_review(review_type: str, request: SaveReviewRequest):
    """Save a periodic review session result to Notion."""
    client = NotionClient()
    
    page_id = client.save_review_session(
        review_type=review_type,
        date_str=request.date,
        content=request.content,
        rating=request.rating,
        emotions=request.emotions
    )
    
    return {
        "success": bool(page_id),
        "data": {
            "page_id": page_id
        }
    }
```

#### 6.1.8 Authentication Middleware

```python
# api/auth.py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    expected_key = os.getenv("PERSONALAXIS_API_KEY")
    if not expected_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    if api_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

#### 6.1.9 Error Handling & Validation

Standardized error response format for all endpoints:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Technical description for logs",
    "user_message": "Kaygı verici olmayan, kullanıcı dostu mesaj",
    "details": {},
    "timestamp": "2026-01-18T10:50:00Z"
  }
}
```

#### 6.1.10 Pydantic Schemas (Detailed)

Strict validation is crucial. We will centralize schemas in `api/schemas.py`.

```python
# api/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import date as dt_date
from enum import Enum

# --- Common Models ---

class StandardResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[dict] = None

# --- Journal Models ---

class ActionItem(BaseModel):
    priority: Literal["P1", "P2", "P3", "P4", "P5"]
    status: Literal["Aktif"] = "Aktif"
    title: str = Field(..., description="Task name in Turkish")
    date: dt_date

class QuickJournalRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Raw journal entry content")
    title: Optional[str] = Field(None, max_length=200, description="Optional title, defaults to timestamp")

class FullJournalRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    raw_content: str = Field(..., min_length=1)
    date: Optional[dt_date] = Field(None, description="Date in ISO format (YYYY-MM-DD)")
    emotions_detected: Optional[List[str]] = Field(None, max_length=10)
    key_insights: Optional[str] = None
    action_items: Optional[List[ActionItem]] = Field(None, description="Actionable tasks derived from journal")

# --- Review Models ---

ReviewType = Literal['weekly', 'monthly', 'quarterly', 'yearly']

class PeriodAssessment(str, Enum):
    SUCCESSFUL = "Başarılı"
    MIXED = "Karışık"
    CHALLENGING = "Zorlayıcı"

class GoalStatus(str, Enum):
    NOT_STARTED = "Başlamadı"
    IN_PROGRESS = "Devam Ediyor"
    COMPLETED = "Tamamlandı"
    POSTPONED = "Ertelendi"

class GoalUpdate(BaseModel):
    goal_name: str = Field(..., min_length=1, description="Exact name of the goal from context")
    new_status: GoalStatus
    progress_delta: int = Field(
        ...,
        ge=-100,
        le=100,
        description="Change in progress for this period. Can be negative if regressed."
    )
    notes: str = Field(..., min_length=1, description="Brief reasoning for change")

class SaveReviewRequest(BaseModel):
    review_type: ReviewType
    date: dt_date = Field(..., description="Review date YYYY-MM-DD")
    review_summary: str = Field(..., min_length=50)
    wins: List[str] = Field(..., min_length=1, max_length=50)
    challenges: List[str] = Field(..., min_length=1, max_length=50)
    lessons_learned: str = Field(..., min_length=1, description="Key takeaway from this period for future use.")
    goal_updates: List[GoalUpdate] = Field(default_factory=list)
    next_period_focus: List[str] = Field(..., min_length=1, max_length=20)
    
    @field_validator('review_type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ['weekly', 'monthly', 'quarterly', 'yearly']:
            raise ValueError(f"Invalid review type: {v}")
        return v
```

**Key Error Scenarios to Handle:**
1.  **Notion API Issues:**
    - `429 Too Many Requests`: Retry with exponential backoff (server-side) or return `429` to client with `retry_after`.
    - `401 Unauthorized`: Log critical alert, return `500` or `401` to client.
    - `404 Not Found`: Return `404` with specific database name.
2.  **Validation Issues:**
    - `422 Unprocessable Entity`: Automatic via Pydantic for malformed JSON or invalid types.
    - Custom validation for review types and date formats.
3.  **System Issues:**
    - `503 Service Unavailable`: Used during server startup or if Notion is down.
    - `504 Gateway Timeout`: If Notion takes >30s to respond.

**Possible Error Codes:**

| Error Code | HTTP Status | Description |
| :--- | :--- | :--- |
| `AUTH_MISSING` | 403 | API key header is missing in the request. |
| `AUTH_INVALID` | 403 | Provided API key is incorrect. |
| `NOTION_AUTH_FAILED` | 401/500 | Notion token is invalid or integration has no access. |
| `NOTION_RATE_LIMIT` | 429 | Notion API rate limit exceeded. |
| `NOTION_API_ERROR` | 500/502 | Generic error returned by the Notion API. |
| `NOTION_RESOURCE_NOT_FOUND` | 404 | Targeted Database or Page not found in Notion. |
| `NOTION_TIMEOUT` | 504 | Connection to Notion API timed out. |
| `VALIDATION_ERROR` | 422 | Request body or parameters failed validation (Pydantic). |
| `INVALID_REVIEW_TYPE` | 422 | Unsupported review type (must be weekly, monthly, etc). |
| `INVALID_PERIOD_FORMAT` | 422 | Date or period string (e.g. 2026-W01) is malformed. |
| `INTERNAL_ERROR` | 500 | Unexpected server-side exception. |
| `OFFLINE` | (Client) | Handled by PWA when no internet is detected. |

---

### Task 6.2: iOS Shortcuts (Optional - Week 3)

> **Note:** This is a bonus feature, not required for MVP. The API documentation will enable users to create their own shortcuts if desired.

#### 6.2.1 Shortcut: Daily Context

```
Name: PersonalAxis - Daily Context
Actions:
1. Get contents of URL
   - URL: https://<tunnel-id>.cfargotunnel.com/api/context/daily
   - Method: GET
   - Headers: X-API-Key: [your-key]
2. Get Dictionary Value (context)
3. Quick Look / Share Sheet
```

#### 6.2.2 Shortcut: Quick Journal

```
Name: PersonalAxis - Quick Note
Actions:
1. Ask for Input (Text): "What's on your mind?"
2. Get contents of URL
   - URL: https://<tunnel-id>.cfargotunnel.com/api/journal/quick
   - Method: POST
   - Headers: X-API-Key: [your-key]
   - Body: {"content": "[Provided Input]"}
3. Show Notification: "Saved ✓"
```

#### 6.2.3 Shortcut: Goal Status

```
Name: PersonalAxis - Goal Status
Actions:
1. Get contents of URL
   - URL: https://<tunnel-id>.cfargotunnel.com/api/goals/status
   - Method: GET
   - Headers: X-API-Key: [your-key]
2. Get Dictionary Value (goals)
3. Repeat with Each
   - Format: "• [Name] [[Status]]"
4. Combine Text
5. Quick Look
```

---

### Task 6.3: Cloudflare Tunnel Deployment

#### 6.3.1 Setup

```bash
# macOS
brew install cloudflared

# Create tunnel (one-time)
cloudflared tunnel create personalaxis
# This generates: ~/.cloudflared/<tunnel-id>.json

# Note the tunnel ID and random subdomain
# Format: <tunnel-id>.cfargotunnel.com
```

#### 6.3.2 Quick Tunnel (Development)

For quick testing without permanent setup:
```bash
# Temporary tunnel (new URL each time)
cloudflared tunnel --url http://localhost:8000
# Output: https://random-words.trycloudflare.com
```

#### 6.3.3 Named Tunnel Config (Production)

```yaml
# deployment/cloudflare/tunnel-config.yml
tunnel: <tunnel-id>
credentials-file: /Users/<user>/.cloudflared/<tunnel-id>.json

ingress:
  - service: http://localhost:8000
```

#### 6.3.4 Cloudflare Access Setup

1. Go to Cloudflare Zero Trust Dashboard
2. Create Access Application:
   - Name: PersonalAxis API
   - Domain: `<tunnel-id>.cfargotunnel.com`
   - Policy: Allow emails `your-email@domain.com`
3. This adds browser-based auth before API key check

#### 6.3.5 Auto-start on macOS Boot

```xml
<!-- deployment/launchd/com.personalaxis.tunnel.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.personalaxis.tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/cloudflared</string>
        <string>tunnel</string>
        <string>--config</string>
        <string>/path/to/PersonalAxis/deployment/cloudflare/tunnel-config.yml</string>
        <string>run</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/path/to/PersonalAxis/logs/tunnel.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/PersonalAxis/logs/tunnel.error.log</string>
</dict>
</plist>
```

---

### Task 6.4: PWA Frontend

#### 6.4.1 PWA v1.0 - Minimal Design

```
┌─────────────────────────────────────┐
│  PersonalAxis           [⟳] [?]    │  ← Refresh + Help icons
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────────┐│
│  │     🌅 Daily Context            ││  ← Primary action, larger
│  └─────────────────────────────────┘│
│                                     │
│  ┌───────────┐ ┌───────────────────┐│
│  │ 📝 Quick  │ │ 🎯 Goal Status    ││
│  │ Journal   │ │                   ││
│  └───────────┘ └───────────────────┘│
│                                     │
│  ┌───────────┐ ┌───────────────────┐│
│  │ ✅ Habits │ │ 🔄 Review Context ││
│  │           │ │                   ││
│  └───────────┘ └───────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │     📊 Save Review              ││
│  └─────────────────────────────────┘│
│                                     │
├─────────────────────────────────────┤
│ 🟢 Connected │ v1.0.0              │  ← Status bar
└─────────────────────────────────────┘
```

#### 6.4.2 Action Flow: Daily Context

```
┌─────────────────────────────────────┐
│  ← Daily Context                    │
├─────────────────────────────────────┤
│  📅 2026-01-15 08:30                │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐│
│  │ # Hayat Bağlamın                ││
│  │                                 ││
│  │ ## Aktif Sütunlar               ││
│  │ - Self (Kişisel Gelişim)        ││
│  │ - Work & Craft                  ││
│  │ ...                             ││
│  │                                 ││
│  │ [scrollable markdown view]      ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌───────────┐ ┌───────────────────┐│
│  │ 📋 Copy   │ │ 📤 Share          ││
│  └───────────┘ └───────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

#### 6.4.3 Action Flow: Quick Journal

```
┌─────────────────────────────────────┐
│  ← Quick Journal                    │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────────┐│
│  │                                 ││
│  │ What's on your mind?            ││
│  │                                 ││
│  │ [multi-line textarea]           ││
│  │                                 ││
│  │                                 ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │          💾 Save to Notion      ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ✓ Saved successfully!           ││  ← Success toast
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

#### 6.4.4 Error & Loading States

The PWA must handle errors gracefully with clear user communication:

**Loading State:**
- Pulsing skeleton screens or a centered "JARVIS is thinking..." spinner.
- Disable action buttons during active requests.

**Standard Error Toast/Modal:**
```
┌─────────────────────────────────────┐
│  ⚠️ Bir Şeyler Ters Gitti           │
├─────────────────────────────────────┤
│  [İkon: Network/Lock/Cloud]         │
│                                     │
│  "Notion bağlantısı şu an kurulamıyor.│
│   Sistem 5 saniye içinde tekrar     │
│   deneyecek."                       │
│                                     │
│  [ Kapat ]       [ Şimdi Dene ]     │
└─────────────────────────────────────┘
```

**Specific Error Handlers:**
- **Offline:** Persistent top bar "İnternet Bağlantısı Yok".
- **403 Forbidden:** Force logout/clear API key and show "Yetkisiz Erişim" screen.
- **429 Rate Limit:** Show countdown timer: "Çok fazla istek. [15] saniye bekleyin."
- **500/503:** "Sunucu şu an meşgul veya bakımda. Lütfen daha sonra deneyin."


#### 6.4.5 PWA Technical Requirements

| Feature | Implementation |
|---------|----------------|
| Offline detection | `navigator.onLine` + Service Worker |
| Add to Home Screen | `manifest.json` with icons |
| Mobile viewport | `<meta name="viewport">` |
| Touch-friendly | Min 44px tap targets |
| Dark mode | `prefers-color-scheme` media query |
| Safe areas | `env(safe-area-inset-*)` for notch |

---

## 🧪 Test Plan (Refined)

### Unit Tests (Automated)

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient

def test_health_endpoint():
    """Health check should always return 200."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_endpoints_require_auth():
    """Protected endpoints should return 403 without API key."""
    endpoints = [
        "/api/context/daily",
        "/api/context/review/weekly",
        "/api/goals/status",
        "/api/habits",
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 403

def test_daily_context_with_valid_key(mock_notion):
    """Daily context should return markdown content."""
    response = client.get(
        "/api/context/daily",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    assert "context" in response.json()
    assert "Hayat Bağlamın" in response.json()["context"]

def test_quick_journal_creates_entry(mock_notion):
    """Quick journal should create Notion page."""
    response = client.post(
        "/api/journal/quick",
        json={"content": "Test note from API"},
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_daily_context_notion_error():
    """Should return 500/502 if Notion API fails."""
    with mock.patch("orchestration.notion_service.NotionClient") as mock_client:
        mock_client.return_value.get_active_pillars.side_effect = APIResponseError(
            response=mock.Mock(status_code=500), body={}, message="Notion Down"
        )
        response = client.get("/api/context/daily", headers={"X-API-Key": "test-key"})
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "NOTION_API_ERROR"

def test_invalid_review_type():
    """Should return 400/422 for unsupported review types."""
    response = client.get("/api/context/review/invalid_type", headers={"X-API-Key": "test-key"})
    assert response.status_code == 422 

def test_rate_limit_handling():
    """Should return 429 when rate limit is exceeded."""
    # (Testing slowapi limiter)
    for _ in range(11):
        response = client.get("/api/context/daily", headers={"X-API-Key": "test-key"})
    assert response.status_code == 429
    assert "retry-after" in response.headers
```

### Integration Tests (Manual with Real Notion)

| Test | Command | Expected Result |
|------|---------|-----------------|
| Health | `curl .../api/health` | `{"status": "healthy"}` |
| Context | `curl -H "X-API-Key: ..." .../api/context/daily` | Markdown with pillars, goals |
| Journal | `curl -X POST -d '{"content":"test"}' ...` | New page in Notion |
| Goals | `curl -H "X-API-Key: ..." .../api/goals/status` | List of active goals |

### PWA Tests (Manual on iOS Device)

| Test Case | Steps | Expected |
|-----------|-------|----------|
| Home Load | Open PWA URL | 6 buttons visible, status green |
| Daily Context | Tap button → wait | Markdown displayed, copy works |
| Quick Journal | Enter text → Save | Success toast, entry in Notion |
| Offline | Enable airplane mode → tap any button | "No connection" message |
| Add to Home | Share → Add to Home Screen | App icon on home screen |
| Reopen | Kill app → open from icon | App loads correctly |
| Cloudflare Access | First visit on new device | Email verification prompt |

### Load & Stability Tests

```bash
# Concurrent requests (should handle 10 simultaneous)
for i in {1..10}; do
  curl -H "X-API-Key: $KEY" "$URL/api/context/daily" &
done
wait

# API restart recovery
launchctl stop com.personalaxis.api
sleep 5
launchctl start com.personalaxis.api
curl $URL/api/health  # Should work after restart
```

---

## 🚀 Deployment Plan (Refined)

### Week 1: Core API Development

**Days 1-2: API Foundation**
```bash
# Setup
pip install fastapi uvicorn pydantic python-multipart

# Development server
uvicorn api.main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/api/health
curl -H "X-API-Key: dev-key" http://localhost:8000/api/context/daily
```

**Days 3-4: All Endpoints + Auth**
- Implement all 7 endpoint groups
- Add API key middleware
- Write unit tests

**Day 5: Cloudflare Tunnel**
```bash
# Install
brew install cloudflared

# Quick test tunnel
cloudflared tunnel --url http://localhost:8000

# Test from phone browser
# https://random-words.trycloudflare.com/api/health
```

### Week 2: PWA Development

**Days 1-2: PWA Structure**
- index.html with all screens
- manifest.json for "Add to Home Screen"
- Basic CSS (mobile-first)

**Days 3-4: JavaScript Client**
- API client class
- Screen navigation
- Loading/error states

**Day 5: Service Worker + Testing**
- Offline detection
- Cache static assets
- Test on real iOS device

### Week 3: Polish & Documentation

**Days 1-2: Cloudflare Access Setup**
- Configure zero-trust policy
- Test auth flow on mobile

**Days 3-4: Production Hardening**
- Create launchd plists (API + Tunnel)
- Test auto-restart on reboot
- Add request logging

**Day 5: Documentation**
- API documentation (auto-generated OpenAPI)
- User setup guide
- Troubleshooting guide

---

## 📊 Effort Estimation (Refined)

| Task | Files | Complexity | Estimated Time |
|-----:|------:|-----------:|---------------:|
| 6.1 FastAPI Backend | 8 | Medium | 6-8 hours |
| 6.2 Cloudflare Tunnel | 2 | Low | 1-2 hours |
| 6.3 PWA Frontend | 5 | Medium | 6-8 hours |
| 6.4 Service Worker | 1 | Low | 1 hour |
| 6.5 Cloudflare Access | 1 | Low | 1 hour |
| 6.6 launchd Autostart | 2 | Low | 1 hour |
| 6.7 Tests | 2 | Medium | 3 hours |
| 6.8 Documentation | 2 | Low | 2 hours |

**Total:** ~21-26 hours (2-3 weeks part-time)

---

## ✅ Implementation Checklist (Refined)

### Phase 6.1: Core API (Week 1)
- [ ] Project structure (`api/` directory)
- [ ] FastAPI app initialization (`api/main.py`)
- [ ] Configuration management (`api/config.py`)
- [ ] Pydantic schemas (`api/schemas.py`)
- [ ] API key authentication (`api/auth.py`)
- [ ] Health endpoint (`/api/health`)
- [ ] Context endpoints (`/api/context/daily`, `/api/context/review/{type}`)
- [ ] Journal endpoints (`/api/journal/quick`, `/api/journal`)
- [ ] Goals endpoint (`/api/goals/status`)
- [ ] Habits endpoint (`/api/habits`)
- [ ] Review endpoints (`/api/reviews/{type}`)
- [ ] CORS configuration
- [ ] Error handling & standardized responses
- [ ] Unit tests (`tests/test_api.py`)

### Phase 6.2: Cloudflare Tunnel (Week 1)
- [ ] Install cloudflared
- [ ] Create named tunnel
- [ ] Test quick tunnel
- [ ] Create tunnel config file
- [ ] Configure Cloudflare Access policy
- [ ] Test from mobile device

### Phase 6.3: PWA Frontend (Week 2)
- [ ] HTML structure (`web/index.html`)
- [ ] PWA manifest (`web/manifest.json`)
- [ ] App icons (192x192, 512x512)
- [ ] Mobile-first CSS (`web/css/app.css`)
- [ ] JavaScript API client (`web/js/app.js`)
- [ ] Home screen with 6 action buttons
- [ ] Daily Context view (copy/share)
- [ ] Quick Journal form
- [ ] Goal Status list view
- [ ] Habits list view
- [ ] Review Context view (type selector)
- [ ] Loading states
- [ ] Error handling
- [ ] Offline detection

### Phase 6.4: Service Worker & Polish (Week 2)
- [ ] Service Worker (`web/sw.js`)
- [ ] Static asset caching
- [ ] Offline fallback page
- [ ] "Add to Home Screen" prompt/instructions

### Phase 6.5: Production (Week 3)
- [ ] API server launchd plist
- [ ] Tunnel launchd plist
- [ ] Test auto-restart on reboot
- [ ] Request logging
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User setup guide
- [ ] Troubleshooting guide

### Phase 6.6: Optional Enhancements
- [ ] iOS Shortcuts documentation
- [ ] Dark mode support
- [ ] Haptic feedback on actions

---

## 🔮 Future Considerations (Phase 7+)

1. **PWA v1.1 - Dashboard Mode**
   - Activity feed / recent actions
   - Goal progress visualization
   - Habit streak display
   - Quick stats

2. **Native iOS App (SwiftUI)**
   - Widgets
   - Push notifications
   - Siri Intents
   - Apple Watch companion

3. **Android Support**
   - PWA works out of box (better support than iOS)
   - Tasker/Automate integration
   - Native app (Kotlin) if needed

4. **Offline Mode**
   - SQLite local cache
   - Sync queue
   - Conflict resolution

5. **Direct AI Integration**
   - Gemini API calls from backend
   - Bypass web UI for automation
   - On-device LLM (future)

---

## 📝 Notes

### Environment Variables Needed

```bash
# Existing (from Phase 1-5)
NOTION_TOKEN=secret_xxx
PILLARS_DB_ID=xxx
LT_GOALS_DB_ID=xxx
HABITS_DB_ID=xxx
PERIODIC_GOALS_DB_ID=xxx
ACTIONS_DB_ID=xxx
JOURNAL_DB_ID=xxx
REVIEWS_DB_ID=xxx

# New for Phase 6
PERSONALAXIS_API_KEY=<generate-32-char-key>
```

### API Key Generation

```bash
# Generate a secure API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Testing Checklist (Real Device)

1. Open PWA URL in Safari
2. Verify all buttons work
3. Test "Add to Home Screen"
4. Kill and reopen app
5. Test offline behavior
6. Test with slow connection
