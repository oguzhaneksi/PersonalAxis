# Phase 7: Enhanced Habit Tracking System

## Problem Statement
The current habit tracking system only stores "Son Tamamlama" (Last Completion Date), making it impossible to:
- Track historical completion patterns
- Calculate completion rates over time
- Analyze habit consistency trends
- Generate meaningful habit analytics for AI coaching

## Proposed Solution: Habit Logs Database

Create a new **"Alışkanlık Kayıtları" (Habit Logs)** database that records each habit completion as a separate entry, enabling full historical tracking.

### New Database Schema

```python
habit_logs_schema = {
    "Tarih Kodu": {"title": {}},        # Format: "2026-01-27-HabitID"
    "Alışkanlık": {"relation": {}},      # Relation to Habits DB (One-way)
    "Tarih": {"date": {}},               # Completion date
    "Tamamlandı": {"checkbox": {}},      # Completed or skipped
    "Günlük Günce": {"relation": {}},    # Optional link to journal
    "Notlar": {"rich_text": {}},         # Optional notes
    # Auto-calculated period fields via Notion Formulas
    "Hafta": {"formula": {"expression": "formatDate(prop(\"Tarih\"), \"YYYY-[W]WW\")"}},
    "Ay": {"formula": {"expression": "formatDate(prop(\"Tarih\"), \"YYYY-MM\")"}},
}
```

### Updated Habits Schema

```python
habits_schema = {
    "Ad": {"title": {}},
    "Sütun": {"relation": {}},
    "Frekans": {"select": {}},           # Günlük, Haftalık, Aylık
    "Hedef Sayısı": {"number": {}},      # Target completions per period
    "Durum": {"select": {}},             # Aktif, Beklemede
    "Tamamlama Oranı": {"number": {}},   # % calculated and updated via API
    "Streak": {"number": {}},             # Current streak updated via API
    "Son Tamamlama": {"date": {}},        # Latest completion date updated via API
}
```

## Implementation Tasks

| Task ID | Description | Effort |
|---------|-------------|--------|
| 7.1.1 | Design and finalize Habit Logs schema | S |
| 7.1.2 | Update `setup_notion_dbs.py` with new schema | S |
| 7.1.3 | Create migration script for existing habits | M |
| 7.2.1 | Add `HabitLogService` to orchestration layer | M |
| 7.2.2 | Update `NotionService` with habit log CRUD operations | M |
| 7.2.3 | Update context builder to include habit statistics | M |
| 7.2.4 | Implement habit stats calculation service | M |
| 7.2.5 | Add background job to refresh habit stats daily | S |
| 7.3.1 | Create `/api/habits/log` endpoint (POST) | S |
| 7.3.2 | Create `/api/habits/{id}/history` endpoint (GET) | S |
| 7.3.3 | Create `/api/habits/stats` endpoint (GET) | M |
| 7.4.1 | Update PWA habits view with completion toggle | M |
| 7.4.2 | Add habit history visualization (streak, calendar) | L |
| 7.4.3 | Integrate habit logging into Quick Journal flow | M |
| 7.5.1 | Update AI prompts with habit analytics context | S |

## Benefits
- **Historical Visibility**: See completion patterns across weeks/months
- **Streak Tracking**: Motivational streak counters
- **Analytics**: Completion rates, best/worst habits, correlation with goals
- **AI Insights**: More context for coaching ("You've missed meditation 3 days in a row")

## Success Metrics
- [ ] 100% habit completions logged with history
- [ ] Streak tracking accurate within 1 day
- [ ] Completion rate visible in PWA
