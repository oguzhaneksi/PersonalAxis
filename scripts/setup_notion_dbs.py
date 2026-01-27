import os
import sys
import json
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
PARENT_PAGE_ID = os.getenv("NOTION_PAGE_ID")

if not NOTION_TOKEN or not PARENT_PAGE_ID:
    print("Error: Please set NOTION_TOKEN and NOTION_PAGE_ID in a .env file or environment variables.")
    sys.exit(1)

client = Client(auth=NOTION_TOKEN)

def get_database_id_by_title(parent_id, title):
    """Checks if a database with the given title exists under the parent page."""
    try:
        results = client.blocks.children.list(block_id=parent_id)
        for block in results.get("results", []):
            if block["type"] == "child_database":
                if block["child_database"]["title"] == title:
                    return block["id"]
        return None
    except Exception as e:
        print(f"Error searching for existing database '{title}': {e}")
        return None

def create_database(parent_id, title, properties):
    """Creates a database in Notion or returns existing one."""
    existing_id = get_database_id_by_title(parent_id, title)
    if existing_id:
        print(f"Database '{title}' already exists (ID: {existing_id}). Skipping creation.")
        return existing_id

    print(f"Creating database: {title}...")
    try:
        response = client.databases.create(
            parent={"page_id": parent_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties=properties
        )
        print(f"Successfully created {title} (ID: {response['id']})")
        return response['id']
    except Exception as e:
        print(f"Error creating {title}: {e}")
        sys.exit(1)

def main():
    print("Starting PersonalAxis Notion Setup...")
    
    # 1. Create Sütunlar (Pillars) - Base DB
    pillars_schema = {
        "Ad": {"title": {}},
        "Grup": {
            "select": {
                "options": [
                    {"name": "Self", "color": "blue"},
                    {"name": "Body", "color": "green"},
                    {"name": "Work & Craft", "color": "orange"},
                    {"name": "Relations", "color": "pink"},
                    {"name": "Life Ops", "color": "gray"}
                ]
            }
        },
        "Durum": {
            "select": {
                "options": [
                    {"name": "Aktif", "color": "green"},
                    {"name": "Durduruldu", "color": "red"},
                    {"name": "İnaktif", "color": "gray"}
                ]
            }
        }
    }
    pillars_id = create_database(PARENT_PAGE_ID, "Sütunlar", pillars_schema)

    # 2. Create Uzun Vadeli Hedefler (Long-term Goals)
    lt_goals_schema = {
        "Ad": {"title": {}},
        "Sütun": {"relation": {"database_id": pillars_id, "dual_property": {}}}, # Relation to Pillars
        "Durum": {
            "select": {
                "options": [
                    {"name": "Devam ediyor", "color": "blue"},
                    {"name": "Durduruldu", "color": "red"},
                    {"name": "Bekliyor", "color": "yellow"},
                    {"name": "Tamamlandı", "color": "green"}
                ]
            }
        },
        "Zorluklar": {"rich_text": {}},
        "Öncelik": {
            "select": {
                "options": [
                    {"name": "P0", "color": "red"},
                    {"name": "P1", "color": "orange"},
                    {"name": "P2", "color": "yellow"},
                    {"name": "P3", "color": "gray"}
                ]
            }
        },
        # "Oluşturulma": {"created_time": {}} # Auto-filled
    }
    lt_goals_id = create_database(PARENT_PAGE_ID, "Uzun Vadeli Hedefler", lt_goals_schema)

    # 3. Create Alışkanlıklar & Rutinler (Habits) - Enhanced with Phase 7 fields
    habits_schema = {
        "Ad": {"title": {}},
        "Sütun": {"relation": {"database_id": pillars_id, "dual_property": {}}},
        "Frekans": {
            "select": {
                "options": [
                    {"name": "Günlük", "color": "blue"},
                    {"name": "Haftalık", "color": "purple"},
                    {"name": "Aylık", "color": "orange"}
                ]
            }
        },
        "Hedef Sayısı": {"number": {"format": "number"}},  # Target completions per period
        "Durum": {
            "select": {
                "options": [
                    {"name": "Aktif", "color": "green"},
                    {"name": "Beklemede", "color": "gray"}
                ]
            }
        },
        "Tamamlama Oranı": {"number": {"format": "percent"}},  # Completion rate (updated via API)
        "Streak": {"number": {"format": "number"}},  # Current streak (updated via API)
        "Son Tamamlama": {"date": {}}  # Latest completion date (updated via API)
    }
    habits_id = create_database(PARENT_PAGE_ID, "Alışkanlıklar & Rutinler", habits_schema)

    # 4. Create Periyodik Hedefler (Periodic Goals)
    periodic_goals_schema = {
        "Ad": {"title": {}},
        "Sütun": {"relation": {"database_id": pillars_id, "dual_property": {}}},
        "Uzun Vadeli Hedef": {"relation": {"database_id": lt_goals_id, "dual_property": {}}},
        "Alışkanlıklar & Rutinler": {"relation": {"database_id": habits_id, "dual_property": {}}},
        "Dönem Tipi": {
            "select": {
                "options": [
                    {"name": "Yıllık", "color": "red"},
                    {"name": "Çeyreklik", "color": "orange"},
                    {"name": "Aylık", "color": "yellow"},
                    {"name": "Haftalık", "color": "blue"}
                ]
            }
        },
        "Dönem": {"rich_text": {}},
        "Öncelik": {
            "select": {
                "options": [
                    {"name": "P1", "color": "red"},
                    {"name": "P2", "color": "orange"},
                    {"name": "P3", "color": "yellow"},
                    {"name": "P4", "color": "blue"},
                    {"name": "P5", "color": "gray"}
                ]
            }
        },
        "Hedef": {"number": {"format": "number"}},
        "Tamamlanan": {"number": {"format": "number"}},
        "İlerleme": {"formula": {"expression": "prop(\"Tamamlanan\") / prop(\"Hedef\")"}},
        "Durum": {
            "select": {
                "options": [
                    {"name": "Başlanmadı", "color": "gray"},
                    {"name": "Devam Ediyor", "color": "blue"},
                    {"name": "Tamamlandı", "color": "green"},
                    {"name": "Ertelendi", "color": "red"}
                ]
            }
        },
        "Tamamlanma Tarihi": {"date": {}}
    }
    periodic_goals_id = create_database(PARENT_PAGE_ID, "Periyodik Hedefler", periodic_goals_schema)

    # 5. Create Aksiyon Maddeleri (Actions)
    actions_schema = {
        "Ad": {"title": {}},
        "Öncelik": {
            "select": {
                "options": [
                    {"name": "P1", "color": "red"},
                    {"name": "P2", "color": "orange"},
                    {"name": "P3", "color": "yellow"},
                    {"name": "P4", "color": "blue"},
                    {"name": "P5", "color": "gray"}
                ]
            }
        },
        "Yapma Tarihi": {"date": {}},
        "Durum": {
            "select": {
                "options": [
                    {"name": "Aktif", "color": "blue"},
                    {"name": "Beklemede", "color": "yellow"},
                    {"name": "Durduruldu", "color": "red"},
                    {"name": "Gelecekte", "color": "purple"},
                    {"name": "Tamamlandı", "color": "green"}
                ]
            }
        },
        "Sütun": {"relation": {"database_id": pillars_id, "dual_property": {}}},
        "Periyodik Hedef": {"relation": {"database_id": periodic_goals_id, "dual_property": {}}}
    }
    actions_id = create_database(PARENT_PAGE_ID, "Aksiyon Maddeleri", actions_schema)

    # 6. Create Günlük Günce (Journal)
    journal_schema = {
        "Tarih Kodu": {"title": {}}, 
        "Tarih": {"date": {}},
        "Hafta": {"formula": {"expression": 'formatDate(prop("Tarih"), "YYYY-[W]WW")'}},
        "Ay": {"formula": {"expression": 'formatDate(prop("Tarih"), "YYYY-MM")'}},
        "Çeyrek": {"formula": {"expression": 'formatDate(prop("Tarih"), "YYYY-[Q]Q")'}},
        "Yıl": {"formula": {"expression": 'formatDate(prop("Tarih"), "YYYY")'}},
        "İlgili Hedefler": {"relation": {"database_id": periodic_goals_id, "dual_property": {}}},
        "Sütunlar": {"relation": {"database_id": pillars_id, "dual_property": {}}},
    }
    journal_id = create_database(PARENT_PAGE_ID, "Günlük Günce", journal_schema)

    # 7. Create Alışkanlık Kayıtları (Habit Logs) - Phase 7: Historical Tracking
    habit_logs_schema = {
        "Tarih Kodu": {"title": {}},  # Format: "2026-01-27-HabitID"
        "Alışkanlık": {"relation": {"database_id": habits_id, "single_property": {}}},  # One-way relation to Habits
        "Tarih": {"date": {}},  # Completion date
        "Tamamlandı": {"checkbox": {}},  # Completed or skipped
        "Günlük Günce": {"relation": {"database_id": journal_id, "single_property": {}}},  # Link to journal
        "Notlar": {"rich_text": {}},  # Optional notes
        # Auto-calculated period fields via Notion Formulas
        "Hafta": {"formula": {"expression": 'formatDate(prop("Tarih"), "YYYY-[W]WW")'}},
        "Ay": {"formula": {"expression": 'formatDate(prop("Tarih"), "YYYY-MM")'}},
        "Çeyrek": {"formula": {"expression": 'formatDate(prop("Tarih"), "YYYY-[Q]Q")'}},
        "Yıl": {"formula": {"expression": 'formatDate(prop("Tarih"), "YYYY")'}}
    }
    habit_logs_id = create_database(PARENT_PAGE_ID, "Alışkanlık Kayıtları", habit_logs_schema)

    # 8. Create Değerlendirme Oturumları (Review Sessions)
    reviews_schema = {
        "Dönem": {"title": {}},
        "Değerlendirme Tipi": {
            "select": {
                "options": [
                    {"name": "Haftalık", "color": "blue"},
                    {"name": "Aylık", "color": "purple"},
                    {"name": "Çeyreklik", "color": "orange"},
                    {"name": "Yıllık", "color": "red"}
                ]
            }
        },
        "Gerçekleştirilme Tarihi": {"date": {}},
        "Oluşturulan Hedefler": {"relation": {"database_id": periodic_goals_id, "dual_property": {}}},
        "Tamamlanan Hedefler": {"relation": {"database_id": periodic_goals_id, "dual_property": {}}},
        "Ertelenen Hedefler": {"relation": {"database_id": periodic_goals_id, "dual_property": {}}}
    }
    reviews_id = create_database(PARENT_PAGE_ID, "Değerlendirme Oturumları", reviews_schema)

    print("\n--- Setup Complete ---")
    print("Please populate your .env file with the generated Database IDs if you want to use them in the orchestration layer.")
    print(f"PILLARS_DB_ID={pillars_id}")
    print(f"LT_GOALS_DB_ID={lt_goals_id}")
    print(f"HABITS_DB_ID={habits_id}")
    print(f"HABIT_LOGS_DB_ID={habit_logs_id}")
    print(f"PERIODIC_GOALS_DB_ID={periodic_goals_id}")
    print(f"ACTIONS_DB_ID={actions_id}")
    print(f"JOURNAL_DB_ID={journal_id}")
    print(f"REVIEWS_DB_ID={reviews_id}")

if __name__ == "__main__":
    main()
