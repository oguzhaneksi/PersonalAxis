"""
Migration script for Phase 7: Enhanced Habit Tracking System

This script performs the following operations:
1. Checks if the Habit Logs database exists
2. Updates existing Habits database to add new fields (if not present)
3. Optionally migrates existing "Son Tamamlama" dates to Habit Logs
4. Initializes stats fields (Tamamlama Oranı, Streak) to 0

Usage:
    python scripts/migrate_habits_phase7.py [--dry-run] [--migrate-completions]

Options:
    --dry-run: Show what would be done without making changes
    --migrate-completions: Create habit log entries from existing "Son Tamamlama" dates
"""

import os
import sys
import argparse
from datetime import datetime
from notion_client import Client
from notion_client.errors import APIResponseError
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
HABITS_DB_ID = os.getenv("HABITS_DB_ID")
HABIT_LOGS_DB_ID = os.getenv("HABIT_LOGS_DB_ID")

if not NOTION_TOKEN:
    print("Error: NOTION_TOKEN not found in environment")
    sys.exit(1)

if not HABITS_DB_ID:
    print("Error: HABITS_DB_ID not found in environment")
    sys.exit(1)

client = Client(auth=NOTION_TOKEN)


def check_database_exists(db_id: str, db_name: str) -> bool:
    """Check if a database exists and is accessible."""
    try:
        db = client.databases.retrieve(database_id=db_id)
        print(f"✓ Found {db_name} database: {db['title'][0]['text']['content']}")
        return True
    except Exception as e:
        print(f"✗ Error accessing {db_name} database: {e}")
        return False


def check_habit_logs_db() -> bool:
    """Check if Habit Logs database exists."""
    if not HABIT_LOGS_DB_ID:
        print("\n⚠ HABIT_LOGS_DB_ID not found in .env file")
        print("Please run setup_notion_dbs.py or manually create the Habit Logs database")
        return False
    
    return check_database_exists(HABIT_LOGS_DB_ID, "Habit Logs")


def get_habits_schema() -> dict:
    """Retrieve the current Habits database schema."""
    try:
        db = client.databases.retrieve(database_id=HABITS_DB_ID)
        return db['properties']
    except Exception as e:
        print(f"Error retrieving Habits schema: {e}")
        sys.exit(1)


def update_habits_schema(dry_run: bool = False) -> bool:
    """Add new fields to Habits database if they don't exist."""
    print("\n--- Checking Habits Database Schema ---")
    
    current_schema = get_habits_schema()
    existing_fields = set(current_schema.keys())
    
    required_fields = {
        "Hedef Sayısı": {"number": {"format": "number"}},
        "Tamamlama Oranı": {"number": {"format": "percent"}},
        "Streak": {"number": {"format": "number"}}
    }
    
    missing_fields = {}
    for field_name, field_config in required_fields.items():
        if field_name not in existing_fields:
            missing_fields[field_name] = field_config
            print(f"  ⚠ Missing field: {field_name}")
        else:
            print(f"  ✓ Field exists: {field_name}")
    
    if not missing_fields:
        print("\n✓ All required fields already exist in Habits database")
        return True
    
    if dry_run:
        print(f"\n[DRY RUN] Would add {len(missing_fields)} fields to Habits database")
        return True
    
    print(f"\nAdding {len(missing_fields)} new fields to Habits database...")
    
    try:
        # Update the database schema
        properties_to_add = {**current_schema, **missing_fields}
        client.databases.update(
            database_id=HABITS_DB_ID,
            properties=missing_fields
        )
        print("✓ Successfully updated Habits database schema")
        return True
    except Exception as e:
        print(f"✗ Error updating Habits schema: {e}")
        return False


def fetch_all_habits() -> list:
    """Fetch all habits from the database."""
    try:
        results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            query_params = {"database_id": HABITS_DB_ID}
            if start_cursor:
                query_params["start_cursor"] = start_cursor
            
            response = client.databases.query(**query_params)
            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
        
        print(f"✓ Fetched {len(results)} habits from database")
        return results
    except Exception as e:
        print(f"✗ Error fetching habits: {e}")
        return []


def initialize_habit_stats(habit_id: str, dry_run: bool = False) -> bool:
    """Initialize Tamamlama Oranı and Streak to 0 for a habit."""
    if dry_run:
        return True
    
    try:
        client.pages.update(
            page_id=habit_id,
            properties={
                "Tamamlama Oranı": {"number": 0},
                "Streak": {"number": 0}
            }
        )
        return True
    except Exception as e:
        print(f"  ✗ Error updating habit {habit_id}: {e}")
        return False


def create_habit_log_entry(habit_id: str, habit_name: str, completion_date: str, dry_run: bool = False) -> bool:
    """Create a habit log entry for a completion date."""
    if not HABIT_LOGS_DB_ID:
        return False
    
    # Create a unique Tarih Kodu
    date_code = f"{completion_date}-{habit_id[:8]}"
    
    if dry_run:
        print(f"  [DRY RUN] Would create log entry: {date_code}")
        return True
    
    try:
        client.pages.create(
            parent={"database_id": HABIT_LOGS_DB_ID},
            properties={
                "Tarih Kodu": {"title": [{"text": {"content": date_code}}]},
                "Alışkanlık": {"relation": [{"id": habit_id}]},
                "Tarih": {"date": {"start": completion_date}},
                "Tamamlandı": {"checkbox": True},
                "Notlar": {"rich_text": [{"text": {"content": "Migrated from Son Tamamlama"}}]}
            }
        )
        print(f"  ✓ Created log entry: {date_code}")
        return True
    except Exception as e:
        print(f"  ✗ Error creating log entry: {e}")
        return False


def migrate_habit_completions(dry_run: bool = False) -> None:
    """Migrate existing "Son Tamamlama" dates to Habit Logs."""
    print("\n--- Migrating Habit Completions ---")
    
    if not check_habit_logs_db():
        print("Cannot proceed with migration without Habit Logs database")
        return
    
    habits = fetch_all_habits()
    
    migrated_count = 0
    skipped_count = 0
    
    for habit in habits:
        habit_id = habit['id']
        
        # Get habit name
        habit_name_prop = habit['properties'].get('Ad', {})
        if habit_name_prop.get('title'):
            habit_name = habit_name_prop['title'][0]['text']['content']
        else:
            habit_name = "Unnamed Habit"
        
        # Check for Son Tamamlama date
        last_completion = habit['properties'].get('Son Tamamlama', {})
        
        if last_completion.get('date') and last_completion['date'].get('start'):
            completion_date = last_completion['date']['start']
            print(f"\nMigrating: {habit_name} (Last completion: {completion_date})")
            
            if create_habit_log_entry(habit_id, habit_name, completion_date, dry_run):
                migrated_count += 1
            else:
                skipped_count += 1
        else:
            print(f"\nSkipping: {habit_name} (No completion date)")
            skipped_count += 1
    
    print(f"\n--- Migration Summary ---")
    print(f"  Migrated: {migrated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(habits)}")


def initialize_all_habit_stats(dry_run: bool = False) -> None:
    """Initialize stats fields for all habits."""
    print("\n--- Initializing Habit Stats ---")
    
    habits = fetch_all_habits()
    
    success_count = 0
    error_count = 0
    
    for habit in habits:
        habit_id = habit['id']
        
        # Get habit name
        habit_name_prop = habit['properties'].get('Ad', {})
        if habit_name_prop.get('title'):
            habit_name = habit_name_prop['title'][0]['text']['content']
        else:
            habit_name = "Unnamed Habit"
        
        if dry_run:
            print(f"  [DRY RUN] Would initialize stats for: {habit_name}")
            success_count += 1
        else:
            print(f"  Initializing: {habit_name}")
            if initialize_habit_stats(habit_id, dry_run):
                success_count += 1
            else:
                error_count += 1
    
    print(f"\n--- Initialization Summary ---")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(habits)}")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate habits database to Phase 7 enhanced tracking system"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--migrate-completions",
        action="store_true",
        help="Migrate existing 'Son Tamamlama' dates to Habit Logs"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Phase 7 Habit Tracking Migration")
    print("=" * 60)
    
    if args.dry_run:
        print("\n⚠ DRY RUN MODE - No changes will be made")
    
    # Step 1: Check Habits database
    if not check_database_exists(HABITS_DB_ID, "Habits"):
        print("Cannot proceed without Habits database")
        sys.exit(1)
    
    # Step 2: Update Habits schema
    if not update_habits_schema(args.dry_run):
        print("\nSchema update failed. Cannot proceed.")
        sys.exit(1)
    
    # Step 3: Initialize habit stats
    initialize_all_habit_stats(args.dry_run)
    
    # Step 4: Optionally migrate completions
    if args.migrate_completions:
        migrate_habit_completions(args.dry_run)
    else:
        print("\n--- Skipping Completion Migration ---")
        print("Use --migrate-completions flag to migrate existing 'Son Tamamlama' dates")
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY RUN COMPLETE")
        print("Run without --dry-run to apply changes")
    else:
        print("MIGRATION COMPLETE")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Verify the Habit Logs database in Notion")
    print("2. Add HABIT_LOGS_DB_ID to your .env file if not already present")
    print("3. Test habit logging functionality via the API")
    print("4. Implement Task 7.2: Orchestration Layer Updates")


if __name__ == "__main__":
    main()
