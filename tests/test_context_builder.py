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
    
    context = builder.build_daily_context(pillars, goals, habits, [], [])
    
    assert "- **Sağlık** (Body)" in context
    assert "- [Aylık] 5kg Ver (İlerleme: %20)" in context
    assert "- Kitap Oku (Günlük) [Son: 2026-01-10]" in context

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
