# Walkthrough: Phase 4 AI Integration

We have successfully integrated the AI layer into PersonalAxis. This phase focused on creating the "brains" of the system—the prompts—and enabling the CLI to handle strategic reviews.

## Changes Made

### 1. AI Prompt Library
Created a structured prompt library in the `prompts/` directory:
- **Daily Coach (JARVIS)**: System prompt for a strategic, masculine, and samimi "Aga" persona. JARVIS challenges the user, uses engineering terminology, and applies the P1-P2-P3 framework for analysis.
- **Strategic Reviewer (ChatGPT)**: System prompt for deep analytical reviews of life pillars and goals, with strict constraints against hallucinations and identity labeling.
- **Review Templates**: Specific guidance for Weekly, Monthly, Quarterly, and Yearly reviews.
- **Quality Checklist**: [prompts/checklist.md](./prompts/checklist.md) to ensure consistency and adherence to constraints.
- **Usage Guide**: [prompts/README.md](./prompts/README.md) for quick setup.

### 2. CLI Enhancements
Extended the orchestration layer to support strategic reviews:
- **`save-review` command**: New CLI command to sync ChatGPT review output back to Notion.
- **Goal Synchronization**: Automatically updates goal statuses (Aktif, Tamamlandı, İptal) based on AI assessment.
- **Review Logging**: Creates a detailed entry in the "Değerlendirme Oturumları" database.

### 3. Structural Fixes
- **Renamed `notion_client.py` to `notion_service.py`**: Resolved a circular import conflict with the official Notion library.
- **Updated Imports**: All internal modules and tests now point to the new service name.

---

## Verification Results

### 1. CLI Validation
The CLI commands were verified for correct registration and import stability:
```bash
python3 orchestration/main.py --help
```
Output:
```
Commands:
  daily-context   Generate daily context for...
  habits          Show today's habit...
  review-context  Generate periodic review...
  save-journal    Save a journal entry from...
  save-review     Save a periodic review...
```

### 2. Prompt Quality
- **Gemini (Daily Coach)**: Implements "Günü kapat" trigger for JSON export and avoids identity labeling.
- **ChatGPT (Reviewer)**: Implements "Değerlendirmeyi tamamla" trigger for goal-aware JSON export and adheres to strict objective analysis.
- **Turkish/English**: Follows the agreed convention (English instructions, Turkish dialogue).

---

## How to use Phase 4

### Daily Coaching Flow
1. `python -m orchestration.main daily-context`
2. Upload `output/context.md` to Gemini Gem.
3. Chat -> "Günü kapat" -> Copy JSON.
4. `python -m orchestration.main save-journal` -> Paste JSON.

### Strategic Review Flow
1. `python -m orchestration.main review-context --type weekly --period 2026-W02`
2. Upload context to ChatGPT Custom GPT.
3. Chat -> Follow template -> "Değerlendirmeyi tamamla" -> Copy JSON.
4. `python -m orchestration.main save-review --type weekly --period 2026-W02` -> Paste JSON.

---

## Next Steps: Phase 5 (Automation)
- [x] Set up `launchd` for automatic context generation (Completed).
- [ ] Implement SMART goal validation templates.
- [ ] Build analytics dashboard in Notion.
