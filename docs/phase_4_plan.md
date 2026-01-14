# Phase 4 Implementation Plan: AI Integration ✅ COMPLETED

This document outlines the detailed plan for implementing AI Integration (Phase 4) of the PersonalAxis project. This phase creates the prompts and configurations for Gemini (daily coaching) and ChatGPT (strategic reviews).

## 📋 Overview

Phase 4 bridges the orchestration layer with AI platforms. Since PersonalAxis is privacy-first (no external API calls), integration is done through:
- **Gemini Gem**: Custom persona for daily coaching sessions
- **ChatGPT Custom GPT**: Strategic reviewer for periodic check-ins

### Design Philosophy
- AI prompts expect `context.md` or `review_context.md` as conversation starters
- AI outputs JSON format for seamless parsing by `save-journal` / `save-review` CLI
- Prompts are in English (system instructions), context in Turkish (user-facing)

---

## 🎯 Task Breakdown

### Task 4.1: Prompt Architecture Setup
- [x] Create `prompts/README.md` with usage instructions
- [x] Define folder structure:
  ```
  prompts/
  ├── README.md
  ├── daily_coach_system.md
  ├── periodic_reviewer_system.md
  └── review_templates/
      ├── weekly_review.md
      ├── monthly_review.md
      ├── quarterly_review.md
      └── yearly_review.md
  ```

### Task 4.2: Daily Coach Prompt (Gemini - JARVIS)
- [x] Create `prompts/daily_coach_system.md`
  - Role definition: JARVIS (Strategic 'Aga' Persona)
  - Context expectations: `context.md` format
  - Conversation modes: Brain dump (Analysis), debug mode, P1-P2-P3 framework
  - Tone: Engineering/Technical + masculine samimi
  - Output contract: JSON schema for `save-journal`

### Task 4.3: Periodic Reviewer Prompt (ChatGPT)
- [x] Create `prompts/periodic_reviewer_system.md`
  - Role definition: Strategic life analyst (Objective focused)
  - Context expectations: `{type}_{period}_context.md` format
  - Review modes: Weekly, Monthly, Quarterly, Yearly
  - Output contract: JSON schema for `save-review`

- [x] Create review templates:
  - `weekly_review.md`: Task completion, micro-adjustments
  - `monthly_review.md`: Habit trends, emotional patterns
  - `quarterly_review.md`: SMART goal validation, pillar balance
  - `yearly_review.md`: Life direction, major achievements

### Task 4.4: CLI Enhancement (Optional)
- [x] Implement `save-review` command in `main.py`
  - Parse JSON from ChatGPT review sessions
  - Create Review Session entry in Notion
  - Update goal statuses as specified

### Task 4.5: Documentation
- [x] Update `orchestration/README.md` with AI setup section
- [x] Create quick-start guide for Gemini Gem setup
- [x] Create quick-start guide for ChatGPT Custom GPT setup

---

## 📝 JSON Output Schemas

### Daily Journal Schema (existing)
```json
{
  "raw_content": "Full session summary in Turkish",
  "emotions_detected": ["Anxiety", "Joy", "Focus"],
  "key_insights": "Main takeaways from conversation",
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

### Periodic Review Schema (new)
```json
{
  "review_summary": "Narrative summary for page body",
  "period_assessment": "Başarılı|Karışık|Zorlayıcı",
  "wins": ["Achievement 1", "Achievement 2"],
  "challenges": ["Challenge 1", "Challenge 2"],
  "lessons_learned": "Key insights from the period",
  "goal_updates": [
    {
      "goal_name": "Goal title",
      "new_status": "Aktif|Tamamlandı|İptal",
      "progress_delta": 25,
      "notes": "Optional notes"
    }
  ],
  "next_period_focus": ["Priority 1", "Priority 2"]
}
```

---

## 🔧 Implementation Order

1. **Step 1: Prompt Structure**
   - Create `prompts/README.md` with overview
   - Set up folder structure
   
2. **Step 2: Daily Coach**
   - Write `daily_coach_system.md`
   - Test with Gemini Gem using sample `context.md`
   
3. **Step 3: Periodic Reviewer**
   - Write `periodic_reviewer_system.md`
   - Create all 4 review templates
   - Test with ChatGPT using sample review context
   
4. **Step 4: CLI Enhancement**
   - Implement `save-review` command
   - Add parsing for review JSON schema
   
5. **Step 5: Documentation**
   - Update README files
   - Create setup guides

---

## 🧪 Verification Strategy

### Manual Testing (Primary)
Since this phase is primarily prompt creation:

1. **Daily Coach Test**
   ```bash
   python -m orchestration.main daily-context
   # Upload output/context.md to Gemini Gem
   # Conduct coaching session
   # Request "Günü kapat" for JSON export
   python -m orchestration.main save-journal --title "2026-01-11"
   # Verify journal and tasks created in Notion
   ```

2. **Periodic Review Test**
   ```bash
   python -m orchestration.main review-context --type weekly --period 2026-W02
   # Upload context to ChatGPT Custom GPT
   # Conduct review session
   # Request JSON export
   # Verify save-review works (if implemented)
   ```

### Prompt Quality Checklist
A dedicated checklist is available at [prompts/checklist.md](./prompts/checklist.md).

Key Verification Points:
- [x] Clear role definition with boundaries (No identity labeling, no diagnosis)
- [x] Perspective challenge for Daily Coach (Mirror/Counter-perspective)
- [x] Context format matches `context_builder.py` output
- [x] JSON schemas match `context_generator.py` parsing
- [x] Turkish/English conventions consistent
- [x] All review periods covered (W/M/Q/Y)

---

## 🚦 Next Steps (Phase 5)

After Phase 4 completion:
1. **Automation**: Set up cron jobs for periodic context generation
2. **SMART Validation**: Add goal quality checks as post-review step
3. **Advanced Workflows**: Integrate habit streaks and analytics

---

## 📊 Estimated Effort

| Task | Files | Complexity | Est. Time |
|------|-------|------------|-----------|
| Prompt Architecture | 2 | Low | 30 min |
| Daily Coach Prompt | 1 | Medium | 1 hour |
| Periodic Reviewer | 5 | Medium | 2 hours |
| CLI Enhancement | 1 | Low | 1 hour |
| Documentation | 2 | Low | 30 min |

**Total**: ~10 files, ~5 hours estimated
