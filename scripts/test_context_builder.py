import os
import sys
from pprint import pprint

# Add the project root to sys.path to import orchestration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestration.notion_service import NotionClient
from orchestration.context_builder import ContextBuilder

def test_context_generation():
    print("Initializing Notion Client & Context Builder...")
    client = NotionClient()
    builder = ContextBuilder()

    print("\nFetching data from Notion...")
    pillars = client.fetch_all_pillars()
    goals = client.fetch_active_goals()
    habits = client.fetch_active_habits()
    journals = client.fetch_recent_journals(days=30)
    tasks = client.fetch_tasks()

    print(f"Data Stats:")
    print(f"- Pillars: {len(pillars)}")
    print(f"- Goals: {len(goals)}")
    print(f"- Habits: {len(habits)}")
    print(f"- Journals: {len(journals)}")
    print(f"- Tasks: {len(tasks)}")

    print("\nGenerating Daily Context...")
    daily_context = builder.build_daily_context(
        pillars=pillars,
        goals=goals,
        habits=habits,
        recent_journals=journals,
        tasks=tasks
    )

    print("\n--- GENERATED CONTEXT START ---")
    print(daily_context)
    print("--- GENERATED CONTEXT END ---\n")

    # Save to a temporary file for inspection
    os.makedirs("output", exist_ok=True)
    with open("output/test_context.md", "w", encoding="utf-8") as f:
        f.write(daily_context)
    print("Context saved to output/test_context.md")

if __name__ == "__main__":
    test_context_generation()
