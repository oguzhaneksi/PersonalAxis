import pytest
from orchestration.context_builder import ContextBuilder
from orchestration.util import safe_get_text

def test_safe_get_text():
    # Test title
    prop_title = {"type": "title", "title": [{"plain_text": "Hello"}]}
    assert safe_get_text(prop_title) == "Hello"
    
    # Test select
    prop_select = {"type": "select", "select": {"name": "Aktif"}}
    assert safe_get_text(prop_select) == "Aktif"
    
    # Test number
    prop_number = {"type": "number", "number": 0.5}
    assert safe_get_text(prop_number) == "0.5"

def test_build_daily_context_empty():
    builder = ContextBuilder()
    context = builder.build_daily_context([], [], [], [], [])
    
    assert "# Hayat Bağlamın" in context
    assert "## Aktif Sütunlar" in context
    assert "- Henüz aktif sütun tanımlanmamış." in context
    assert "## Mevcut Hedefler" in context
    assert "- Bu dönem için aktif hedef bulunmuyor." in context

def test_build_daily_context_with_data():
    builder = ContextBuilder()
    
    pillars = [
        {"properties": {"Ad": {"type": "title", "title": [{"plain_text": "Sağlık"}]}, 
                       "Grup": {"type": "select", "select": {"name": "Body"}}}}
    ]
    goals = [
        {"properties": {"Ad": {"type": "title", "title": [{"plain_text": "5kg Ver"}]}, 
                       "Dönem Tipi": {"type": "select", "select": {"name": "Aylık"}},
                       "İlerleme": {"type": "formula", "formula": {"number": 0.2}}}}
    ]
    habits = [
        {"properties": {"Ad": {"type": "title", "title": [{"plain_text": "Kitap Oku"}]}, 
                       "Frekans": {"type": "select", "select": {"name": "Günlük"}},
                       "Son Tamamlama": {"type": "date", "date": {"start": "2026-01-10"}}}}
    ]
    
    # Test with include_habit_stats=False to match the assertion below
    context = builder.build_daily_context(pillars, goals, habits, [], [], include_habit_stats=False)
    
    assert "- **Sağlık** (Body)" in context
    assert "- [Aylık] 5kg Ver (İlerleme: %20)" in context
    assert "- Kitap Oku (Günlük) [Son: 2026-01-10]" in context

def test_build_daily_context_with_stats():
    builder = ContextBuilder()
    habits = [
        {
            "properties": {
                "Ad": {"type": "title", "title": [{"plain_text": "Spor Yap"}]},
                "Frekans": {"type": "select", "select": {"name": "Haftalık"}},
                "Streak": {"type": "number", "number": 10},
                "Tamamlama Oranı": {"type": "number", "number": 0.85},
                "Son Tamamlama": {"type": "date", "date": {"start": "2026-01-25"}}
            }
        }
    ]
    
    context = builder.build_daily_context([], [], habits, [], [])
    
    # Check for enhanced format: Bold name, rate indicator, stats, and streak indicator
    # 0.85 -> 85% -> 💪
    # 10 streak -> 🔥
    assert "Spor Yap" in context
    assert "Haftalık" in context
    assert "Oran: %85" in context
    assert "Seri: 10" in context
    assert "Son: 2026-01-25" in context
    assert "💪" in context
    assert "🔥" in context

def test_build_daily_context_with_journals():
    builder = ContextBuilder()
    journals = [
        {
            "properties": {
                "Tarih Kodu": {"type": "title", "title": [{"plain_text": "2026-01-12"}]},
                "Hafta": {"type": "rich_text", "rich_text": [{"plain_text": "2026-W02"}]},
                "Ay": {"type": "rich_text", "rich_text": [{"plain_text": "2026-01"}]},
                "Çeyrek": {"type": "rich_text", "rich_text": [{"plain_text": "2026-Q1"}]},
                "Yıl": {"type": "rich_text", "rich_text": [{"plain_text": "2026"}]}
            },
            "content": "Today I built a new feature."
        }
    ]
    
    context = builder.build_daily_context([], [], [], journals, [])
    
    assert "### 2026-01-12" in context
    assert "Today I built a new feature." in context
