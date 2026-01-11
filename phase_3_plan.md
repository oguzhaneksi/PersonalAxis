# Phase 3 Implementation Plan: Orchestration Layer

This document outlines the detailed plan for implementing the Orchestration Layer (Phase 3) of the PersonalAxis project. This layer acts as the bridge between Notion (Single Source of Truth) and AI interfaces (Gemini/ChatGPT).

## 📋 Overview

The orchestration layer is a Python-based service responsible for fetching data from Notion, formatting it for AI context, and saving AI-generated insights back to Notion.

### Core Components
1. **Notion API Client** (`notion_client.py`): Direct wrapper for Notion SDK.
2. **Context Builder** (`context_builder.py`): Logic for transforming raw Notion data into structured AI context.
3. **Context Generator** (`context_generator.py`): Orchestrates file creation and AI output parsing.
4. **CLI Interface** (`main.py`): Entry point for user commands.

---

## 🎯 Task Breakdown

### Task 3.1: Environment & Dependency Setup
- [x] Update `requirements.txt` with:
  - `notion-client`
  - `python-dotenv`
  - `click` or `argparse` (for CLI)
- [x] Verify `.env` contains:
  - `NOTION_TOKEN`
  - Database IDs for: Pillars, Long-term Goals, Periodic Goals, Daily Journal, Review Sessions, Tasks, Habits.

### Task 3.2: Implement Notion API Client (`notion_client.py`)
Implement the following functions following [MEMORY[general.md]](memory://general.md) rules:
- **Read Operations:**
  - [x] `fetch_all_pillars()`
  - [x] `fetch_active_goals(period_type, period)`
  - [x] `fetch_active_habits()`
  - [x] `fetch_recent_journals(days=7)`
  - [x] `fetch_tasks(date)`
- **Write Operations:**
  - [x] `create_journal_entry(date, content_page, habits_completed)`
  - [x] `create_task(name, priority, date, status, pillar_id, goal_id)`
  - [x] `update_goal_progress(goal_id, progress, status)`
  - [x] `create_review_session(review_type, period, content_page, related_goals)`

### Task 3.3: Build Context Aggregation Service (`context_builder.py`)
- [x] **Daily Context:** Combine pillars, current goals, recent reflections, and today's tasks into a Turkish Markdown format.
- [x] **Review Context:** Aggregate period-specific data (e.g., all journals from "2026-W2") for strategic AI analysis.

### Task 3.4: Create Sync Utilities & CLI (`main.py`)
- Implement CLI commands:
  - [x] `personalaxis daily-context`: Writes `output/context.md`.
  - [x] `personalaxis save-journal`: Robust parsing of JSON-formatted AI summary and updates Notion.
  - [x] `personalaxis weekly-review`: Writes `output/review_context.md`.
  - [x] `personalaxis save-review <type>`: Syncs review results to Notion.
  - [x] `personalaxis habits`: Minimalist habit checklist in terminal.

---

## 🛠️ Robust AI Output Parsing (V2)

To prevent fragile regex-based extraction, the system will expect AI models to provide a final summary in **JSON format**.

### Expected JSON Schema:
```json
{
  "raw_content": "The full summary of the session for the page body",
  "emotions_detected": ["Anxiety", "Joy", "Focus"],
  "key_insights": "The main takeaways from the conversation",
  "action_items": [
    {
      "priority": "P1",
      "status": "Aktif",
      "title": "Task title",
      "date": "2026-01-11"
    }
  ]
}
```

This ensures that even if the AI's conversational tone changes, the data extraction remains consistent.

## 📝 Implementation Order

1. **Step 1: Read-Only Foundation**
   - Implement `notion_client.py` (read functions) + `context_builder.py` (Daily Context).
   - *Goal:* Successfully generate `context.md` from real Notion data.
2. **Step 2: CLI & Integration**
   - Build `main.py` core and `context_generator.py`.
   - *Goal:* Run `personalaxis daily-context` and get a valid file.
3. **Step 3: Write Operations**
   - Implement `notion_client.py` (write functions) + parsing logic for AI summaries.
   - *Goal:* Save a test journal entry to Notion via CLI.
4. **Step 4: Strategic Reviews**
   - Implement review-specific context building and saving logic.

---

## 🧪 Testing Strategy

### Unit Testing
- Mock Notion API responses to test `context_builder.py` transformations.
- Verify `notion_client.py` handles API errors (e.g., `404 Not Found`, `401 Unauthorized`) gracefully.

### Manual Integration Testing
- Use a dedicated `test_orchestration.py` script.
- Verify that Turkish characters are handled correctly in both Notion and local files.
- Ensure relations between databases (e.g., Task -> Pillar) are preserved during creation.

---

## 📦 File Structure

```
/orchestration/
├── __init__.py
├── notion_client.py         # API Wrapper
├── context_builder.py       # Data Transformation
├── context_generator.py     # File Orchestration
├── main.py                  # CLI Entry
└── utils.py                 # Common helpers (parsing, etc.)
```

---

## 🚦 Next Steps

1. Update `requirements.txt`.
2. Implement `notion_client.py` read functions.
3. Verify connectivity with a test script.
