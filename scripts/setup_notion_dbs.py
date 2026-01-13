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

def create_database(parent_id, title, properties):
    """Creates a database in Notion."""
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

    # 3. Create Alışkanlıklar & Rutinler (Habits)
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
        "Durum": {
            "select": {
                "options": [
                    {"name": "Aktif", "color": "green"},
                    {"name": "Beklemede", "color": "gray"}
                ]
            }
        },
        "Son Tamamlama": {"date": {}}
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
        "Hafta": {"rich_text": {}},  # Format: 2026-W02
        "Ay": {"rich_text": {}},      # Format: 2026-01
        "Çeyrek": {"rich_text": {}},  # Format: 2026-Q3
        "Yıl": {"rich_text": {}},     # Format: 2026
        "İlgili Hedefler": {"relation": {"database_id": periodic_goals_id, "dual_property": {}}},
        "Sütunlar": {"relation": {"database_id": pillars_id, "dual_property": {}}},
        # Checkboxes for habits - Dynamic?
        # We can't create dynamic properties easily. We'll add a few placeholders or just rely on description
        # Plan says "Dynamically added based on active habits". The Script can't do this *dynamically* at runtime.
        # It's better to add them manually or have a script update the schema later.
        # For now, we will add a few generic ones or skip.
    }
    journal_id = create_database(PARENT_PAGE_ID, "Günlük Günce", journal_schema)

    # 7. Create Değerlendirme Oturumları (Review Sessions)
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
    print(f"PERIODIC_GOALS_DB_ID={periodic_goals_id}")
    print(f"ACTIONS_DB_ID={actions_id}")
    print(f"JOURNAL_DB_ID={journal_id}")
    print(f"REVIEWS_DB_ID={reviews_id}")

if __name__ == "__main__":
    main()
