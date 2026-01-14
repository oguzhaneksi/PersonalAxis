# Phase 5 Implementation Plan: Automation & Workflows

Phase 4 is completed and the AI integration (JARVIS + Strategic Reviewer) is working. Now we move on to automation steps that will make the system fully autonomous.

## 📋 Overview

Phase 5 will advance in three main areas:
1. Periodic Automation: automatic context generation with cron/launchd
2. SMART Validation: goal quality checks
3. Advanced CLI: quick-actions and validation commands

---

## 🎯 Task Breakdown

### Task 5.1: Periodic Automation (launchd) ✅

On macOS we will create scripts that run automatically using `launchd`. The times are configurable in the installer script:

| Schedule | Command | Trigger |
|----------|---------|---------|
| Morning 08:00 | `daily-context` | Prepare for the new day |
| Sunday 20:00 | `review-context --type weekly` | Weekly review |
| Last day of month | `review-context --type monthly` | Monthly review |

**Files to create:**
- `automation/launchd/com.personalaxis.daily.plist`
- `automation/launchd/com.personalaxis.weekly.plist`
- `automation/launchd/com.personalaxis.monthly.plist`
- `automation/install.sh` (plist installer script)
- `automation/README.md` (setup guide)

### Task 5.2: SMART Goal Validation

A validator that checks goals against SMART criteria:

SMART Criteria:
- Specific: Is the goal clear?
- Measurable: Is there a measurable metric?
- Achievable: Is it achievable?
- Relevant: Is it linked to a pillar?
- Time-bound: Is there a deadline?

**Files to create/modify:**
- `orchestration/smart_validator.py` (validation logic)
- `orchestration/main.py` (add `validate-goals` command)

**CLI Usage:**
```bash
python -m orchestration.main validate-goals
# Output: Lists goals with SMART score and warnings
```

### Task 5.3: Advanced CLI Commands

We will add extra CLI commands:

| Command | Description |
|---------|-------------|
| `quick-journal` | Quick multi-line journal entry (supports stdin) |
| `goal-status` | Summary of active goals' progress |
| `validate-goals` | SMART validation report |

**Files to modify:**
- `orchestration/main.py` (add new commands)
- `orchestration/notion_service.py` (add helper methods if needed)

### Status Update (implementation progress)

- `launchd` automation and `automation/install.sh` are implemented and configured for the schedules described above.
- macOS notifications via `osascript` have been added and CLI commands accept a `--notify` flag.
- `quick-journal` now supports multi-line entries via `stdin` and a simple call form.
- `goal-status` and `quick-journal` commands are implemented in `orchestration/main.py`.
- Automated tests for the new CLI commands have been added at `tests/test_cli.py`.
- The SMART Goal Validation feature is deferred for a later phase (see Task 5.2).

---

## 📝 Detailed Implementation

### 5.1.1 launchd Plist Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.personalaxis.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>-m</string>
        <string>orchestration.main</string>
        <string>daily-context</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/PersonalAxis</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/path/to/PersonalAxis/logs/daily.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/PersonalAxis/logs/daily.error.log</string>
</dict>
</plist>
```

### 5.1.2 Installer Script

```bash
#!/bin/bash
# automation/install.sh
# Installs launchd plists and configures paths

PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

# Update plist paths
sed -i '' "s|/path/to/PersonalAxis|$PROJECT_DIR|g" automation/launchd/*.plist
sed -i '' "s|/path/to/venv/bin/python|$VENV_PYTHON|g" automation/launchd/*.plist

# Copy to LaunchAgents
cp automation/launchd/*.plist ~/Library/LaunchAgents/

# Load agents
launchctl load ~/Library/LaunchAgents/com.personalaxis.*.plist

echo "✓ PersonalAxis automation installed!"
```

### 5.2.1 SMART Validator Logic

```python
# orchestration/smart_validator.py

from typing import TypedDict

class ValidationResult(TypedDict):
    goal_name: str
    smart_score: int  # 0-5
    issues: list[str]

def validate_goal(goal: dict) -> ValidationResult:
    """Validate a goal against SMART criteria."""
    issues = []
    score = 0
    
    # Specific: Has description > 20 chars
    desc = get_property(goal, "Açıklama", "rich_text")
    if len(desc) > 20:
        score += 1
    else:
        issues.append("Hedef açıklaması çok kısa (min 20 karakter)")
    
    # Measurable: Has quantitative metric
    metric = get_property(goal, "Başarı Kriteri", "rich_text")
    if metric and any(char.isdigit() for char in metric):
        score += 1
    else:
        issues.append("Ölçülebilir metrik eksik (sayısal kriter gerekli)")
    
    # Achievable: Progress < 100 and status not Tamamlandı for active
    # (skipped - subjective)
    score += 1
    
    # Relevant: Has pillar relation
    pillar = get_relation(goal, "Sütun")
    if pillar:
        score += 1
    else:
        issues.append("Sütun ilişkisi eksik")
    
    # Time-bound: Has end date
    end_date = get_property(goal, "Bitiş", "date")
    if end_date:
        score += 1
    else:
        issues.append("Bitiş tarihi tanımlı değil")
    
    return {
        "goal_name": get_property(goal, "Ad", "title"),
        "smart_score": score,
        "issues": issues
    }
```

---

## 🔧 File Summary

### New Files

| File | Purpose |
|------|---------|
| `automation/launchd/com.personalaxis.daily.plist` | Daily context automation |
| `automation/launchd/com.personalaxis.weekly.plist` | Weekly review automation |
| `automation/launchd/com.personalaxis.monthly.plist` | Monthly review automation |
| `automation/install.sh` | Automation installer script |
| `automation/README.md` | Setup and usage guide |
| `orchestration/smart_validator.py` | SMART validation module |
| `logs/` directory | Automation logs |

### Modified Files

| File | Changes |
|------|---------|
| `orchestration/main.py` | `validate-goals`, `quick-journal`, `goal-status` commands |
| `orchestration/notion_service.py` | Helper methods (if necessary) |
| `.gitignore` | Add `logs/` directory |

---

## 🧪 Verification Plan

### Automated Tests

1. **SMART Validator Unit Tests**
```bash
python -m pytest tests/test_smart_validator.py -v
```
Test cases:
- Goal with full SMART criteria → score 5
- Goal missing deadline → score 4, issues list contains "Bitiş tarihi"
- Goal with no pillar → score 4, issues list contains "Sütun"

### Manual Tests

> [!IMPORTANT]
> These tests require real Notion database access.

1. **Automation Installation Test**
   - Run `automation/install.sh`
   - Check agents with `launchctl list | grep personalaxis`
   - Verify that log files are created

2. **SMART Validation Command**
   - Run `python -m orchestration.main validate-goals`
   - Confirm you see the list of goals and SMART scores from Notion
   - Verify at least one goal receives a warning

3. **Quick Journal Command**
   - Run `python -m orchestration.main quick-journal "Test entry"`
   - Confirm a new journal entry appears in Notion

---

## 📊 Estimated Effort

| Task | Files | Complexity | Est. Time |
|------|-------|------------|-----------|
| launchd automation | 5 | Low | 1 hour |
| SMART validator | 2 | Medium | 1.5 hours |
| CLI commands | 2 | Low | 1 hour |
| Testing + docs | 2 | Low | 30 min |

**Total**: ~11 files, ~4 hours estimated

---

## User Review Required

> [!NOTE]
> Please answer the following:

1. **Automation schedule**: Is 08:00 in the morning and Sunday 20:00 acceptable? Do you prefer different times?
2. **Notification system**: Should automation send macOS notifications when it runs? (osascript integration)
3. **SMART Validator details**: Which metric should we use for the "Achievable" criterion? (Currently skipped because it's subjective)
4. **Quick Journal format**: Single-line only, or should multi-line entries be supported?
5. **Additional commands**: Any other CLI commands you want added? (e.g., `habit-streak`, `pillar-health`)
