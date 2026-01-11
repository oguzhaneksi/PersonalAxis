import os
import sys
from pprint import pprint

# Add the project root to sys.path to import orchestration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestration.notion_client import NotionClient

def test_client():
    print("Initializing Notion Client...")
    try:
        client = NotionClient()
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return

    print("\n1. Testing fetch_all_pillars...")
    pillars = client.fetch_all_pillars()
    print(f"Found {len(pillars)} active pillars.")
    for p in pillars:
        name = p["properties"]["Ad"]["title"][0]["plain_text"]
        print(f" - {name}")

    print("\n2. Testing fetch_active_goals (Haftalık)...")
    goals = client.fetch_active_goals(period_type="Haftalık")
    print(f"Found {len(goals)} active weekly goals.")
    for g in goals:
        name = g["properties"]["Ad"]["title"][0]["plain_text"]
        print(f" - {name}")

    print("\n3. Testing fetch_active_habits...")
    habits = client.fetch_active_habits()
    print(f"Found {len(habits)} active habits.")
    for h in habits:
        name = h["properties"]["Ad"]["title"][0]["plain_text"]
        print(f" - {name}")

    print("\n4. Testing fetch_recent_journals...")
    journals = client.fetch_recent_journals(days=30)
    print(f"Found {len(journals)} recent journal entries.")
    for j in journals:
        # Tarih Kodu is the title
        title = j["properties"]["Tarih Kodu"]["title"][0]["plain_text"]
        print(f" - {title}")

    print("\n5. Testing fetch_tasks...")
    tasks = client.fetch_tasks()
    print(f"Found {len(tasks)} active tasks for today.")
    for t in tasks:
        name = t["properties"]["Ad"]["title"][0]["plain_text"]
        print(f" - {name}")

if __name__ == "__main__":
    test_client()
