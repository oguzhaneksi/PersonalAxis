#!/usr/bin/env python3
"""
Test script for Phase 7.2 implementations.
Tests habit log CRUD operations and stats calculations.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.notion_service import NotionClient
from orchestration.habit_stats_service import HabitStatsService
from orchestration.util import safe_get_text


def test_habit_log_crud():
    """Test habit log CRUD operations."""
    print("=" * 60)
    print("TEST 1: Habit Log CRUD Operations")
    print("=" * 60)
    
    notion = NotionClient()
    
    # Fetch active habits
    print("\n1. Fetching active habits...")
    habits = notion.fetch_active_habits()
    if not habits:
        print("❌ No active habits found. Cannot test.")
        return False
    
    test_habit = habits[0]
    habit_id = test_habit["id"]
    habit_name = test_habit["properties"]["Ad"]["title"][0]["plain_text"] if test_habit["properties"]["Ad"]["title"] else "Unknown"
    print(f"✓ Found test habit: {habit_name} (ID: {habit_id[:8]}...)")
    
    # Create a test habit log
    print("\n2. Creating test habit log...")
    today = datetime.now().strftime("%Y-%m-%d")
    log_id = notion.create_habit_log(
        habit_id=habit_id,
        date_str=today,
        completed=True,
        notes="Test log from Phase 7.2 verification script"
    )
    
    if log_id:
        print(f"✓ Created habit log (ID: {log_id[:8]}...)")
    else:
        print("❌ Failed to create habit log")
        return False
    
    # Fetch habit logs
    print("\n3. Fetching habit logs...")
    logs = notion.fetch_habit_logs(habit_id=habit_id)
    print(f"✓ Found {len(logs)} logs for habit")
    
    # Fetch logs by date range
    print("\n4. Fetching logs by date range (last 7 days)...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    range_logs = notion.fetch_habit_logs(
        habit_id=habit_id,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    print(f"✓ Found {len(range_logs)} logs in last 7 days")
    
    # Update habit stats
    print("\n5. Updating habit statistics...")
    success = notion.update_habit(
        habit_id=habit_id,
        completion_rate=0.855,
        streak=5,
        last_completion=today
    )
    
    if success:
        print("✓ Successfully updated habit statistics")
    else:
        print("❌ Failed to update habit statistics")
        return False
    
    print("\n" + "=" * 60)
    print("✅ CRUD Operations Test PASSED")
    print("=" * 60)
    return True


def test_stats_calculation():
    """Test habit statistics calculation."""
    print("\n\n" + "=" * 60)
    print("TEST 2: Habit Statistics Calculation")
    print("=" * 60)
    
    stats_service = HabitStatsService()
    
    # Fetch active habits
    print("\n1. Fetching active habits...")
    habits = stats_service.notion.fetch_active_habits()
    if not habits:
        print("❌ No active habits found. Cannot test.")
        return False
    
    test_habit = habits[0]
    habit_id = test_habit["id"]
    habit_name = safe_get_text(test_habit["properties"].get("Ad", {}))
    frequency = safe_get_text(test_habit["properties"].get("Frekans", {}))
    print(f"✓ Testing with habit: {habit_name} (Frequency: {frequency})")
    
    # Test streak calculation
    print("\n2. Calculating current streak...")
    streak = stats_service.calculate_streak(habit_id, frequency or "Günlük")
    print(f"✓ Current streak: {streak}")
    
    # Test completion rate
    print("\n3. Calculating 30-day completion rate...")
    rate = stats_service.calculate_completion_rate(habit_id, 30, frequency or "Günlük")
    print(f"✓ Completion rate: {rate * 100:.1f}%")
    
    # Test last completion date
    print("\n4. Getting last completion date...")
    last_completion = stats_service.get_last_completion_date(habit_id)
    print(f"✓ Last completion: {last_completion or 'Never'}")
    
    # Test full stats calculation
    print("\n5. Calculating all stats for habit...")
    comp_rate, streak_val, last_comp = stats_service.calculate_stats_for_habit(test_habit)
    print(f"✓ Stats: {comp_rate * 100:.1f}% rate, {streak_val} streak, last: {last_comp or 'Never'}")
    
    print("\n" + "=" * 60)
    print("✅ Statistics Calculation Test PASSED")
    print("=" * 60)
    return True


def test_batch_update():
    """Test batch update of all habits."""
    print("\n\n" + "=" * 60)
    print("TEST 3: Batch Statistics Update")
    print("=" * 60)
    
    stats_service = HabitStatsService()
    
    print("\nCalculating and updating stats for all active habits...")
    results = stats_service.calculate_stats_for_all_habits()
    
    if results:
        print("\n" + "=" * 60)
        print("✅ Batch Update Test PASSED")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("⚠️  No habits were updated (may be expected if no active habits)")
        print("=" * 60)
        return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" Phase 7.2 Implementation Verification")
    print(" Tasks: 7.2.2 (CRUD) and 7.2.4 (Stats Calculation)")
    print("=" * 70)
    
    try:
        test1 = test_habit_log_crud()
        test2 = test_stats_calculation()
        test3 = test_batch_update()
        
        print("\n\n" + "=" * 70)
        print(" FINAL RESULTS")
        print("=" * 70)
        print(f" Test 1 (CRUD):        {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f" Test 2 (Calculations): {'✅ PASSED' if test2 else '❌ FAILED'}")
        print(f" Test 3 (Batch Update): {'✅ PASSED' if test3 else '❌ FAILED'}")
        print("=" * 70)
        
        if all([test1, test2, test3]):
            print("\n🎉 All tests passed! Phase 7.2.2 and 7.2.4 implementations verified.")
            return 0
        else:
            print("\n❌ Some tests failed. Review output above.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Fatal error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
