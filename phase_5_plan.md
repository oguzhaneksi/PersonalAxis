# Phase 5 Implementation Plan: Automation & Workflows

Phase 4 tamamlandı ve AI entegrasyonu (JARVIS + Strategic Reviewer) çalışıyor. Şimdi sistemi **tamamen otonom** hale getirecek otomasyon adımlarına geçiyoruz.

## 📋 Overview

Phase 5 üç ana kategoride gelişim sağlayacak:
1. **Periodic Automation**: Cron/launchd ile otomatik context üretimi
2. **SMART Validation**: Hedef kalite kontrolü
3. **Advanced CLI**: Quick-actions ve validation komutları

---

## 🎯 Task Breakdown

### Task 5.1: Periodic Automation (launchd)

macOS'ta `launchd` kullanarak otomatik çalışan scriptler oluşturacağız:

| Schedule | Command | Trigger |
|----------|---------|---------|
| Sabah 08:00 | `daily-context` | Yeni güne hazırlık |
| Pazar 20:00 | `review-context --type weekly` | Haftalık değerlendirme |
| Ayın son günü | `review-context --type monthly` | Aylık değerlendirme |

**Files to create:**
- `automation/launchd/com.personalaxis.daily.plist`
- `automation/launchd/com.personalaxis.weekly.plist`  
- `automation/launchd/com.personalaxis.monthly.plist`
- `automation/install.sh` (plist installer script)
- `automation/README.md` (setup guide)

### Task 5.2: SMART Goal Validation

Hedeflerin SMART kriterlerine uygunluğunu kontrol eden bir validator:

**SMART Kriterleri:**  
- **S**pecific: Hedef açık mı?
- **M**easurable: Ölçülebilir metrik var mı?
- **A**chievable: Ulaşılabilir mi?
- **R**elevant: Pillar'a bağlı mı?
- **T**ime-bound: Deadline tanımlı mı?

**Files to create/modify:**
- `orchestration/smart_validator.py` (validation logic)
- `orchestration/main.py` (add `validate-goals` command)

**CLI Usage:**
```bash
python -m orchestration.main validate-goals
# Output: Lists goals with SMART score and warnings
```

### Task 5.3: Advanced CLI Commands

Ek CLI komutları ekleyeceğiz:

| Command | Description |
|---------|-------------|
| `quick-journal` | Hızlı tek satır günce girişi |
| `goal-status` | Aktif hedeflerin progress özeti |
| `validate-goals` | SMART validation raporu |

**Files to modify:**
- `orchestration/main.py` (add new commands)
- `orchestration/notion_service.py` (add helper methods if needed)

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
| `automation/launchd/com.personalaxis.daily.plist` | Günlük context otomasyonu |
| `automation/launchd/com.personalaxis.weekly.plist` | Haftalık review otomasyonu |
| `automation/launchd/com.personalaxis.monthly.plist` | Aylık review otomasyonu |
| `automation/install.sh` | Otomasyon kurulum scripti |
| `automation/README.md` | Setup ve kullanım kılavuzu |
| `orchestration/smart_validator.py` | SMART validation modülü |
| `logs/` directory | Otomasyon logları |

### Modified Files

| File | Changes |
|------|---------|
| `orchestration/main.py` | `validate-goals`, `quick-journal`, `goal-status` komutları |
| `orchestration/notion_service.py` | Helper methodlar (gerekirse) |
| `.gitignore` | `logs/` dizini eklenmeli |

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
> Bu testler için gerçek Notion veritabanı erişimi gereklidir.

1. **Otomasyon Kurulum Testi**
   - `automation/install.sh` çalıştır
   - `launchctl list | grep personalaxis` ile agent'ları kontrol et
   - Log dosyalarının oluştuğunu doğrula

2. **SMART Validation Komutu**
   - `python -m orchestration.main validate-goals` çalıştır
   - Notion'daki hedeflerin listesini ve SMART skorlarını gör
   - En az bir hedefin uyarı mesajı aldığını doğrula

3. **Quick Journal Komutu**
   - `python -m orchestration.main quick-journal "Test girişi"` çalıştır
   - Notion'da yeni günce girişinin oluştuğunu doğrula

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
> Lütfen aşağıdaki soruları cevaplayın:

1. **Otomasyon Zamanlaması**: Sabah 08:00 ve Pazar 20:00 uygun mu? Farklı saatler tercih eder misin?

2. **Notification Sistemi**: Otomasyon çalıştığında macOS notification göndermeli mi? (osascript entegrasyonu)

3. **SMART Validator Detayları**: "Achievable" kriteri için hangi metriği kullanmalıyız? (Şu an subjective olduğu için atladım)

4. **Quick Journal Format**: Tek satır mı, yoksa çok satırlı giriş de desteklenmeli mi?

5. **Ek Komutlar**: Başka CLI komutları eklememi ister misin? (örn: `habit-streak`, `pillar-health`)
