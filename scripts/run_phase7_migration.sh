#!/bin/bash

# Phase 7 Migration Quick Start Script
# This script guides you through the migration process

set -e  # Exit on error

echo "=========================================="
echo "Phase 7: Enhanced Habit Tracking Migration"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with your Notion credentials"
    exit 1
fi

# Check if HABIT_LOGS_DB_ID exists in .env
if grep -q "HABIT_LOGS_DB_ID" .env; then
    echo "✓ HABIT_LOGS_DB_ID found in .env"
    HAS_HABIT_LOGS=true
else
    echo "⚠ HABIT_LOGS_DB_ID not found in .env"
    HAS_HABIT_LOGS=false
fi

echo ""
echo "Step 1: Testing migration (dry-run)..."
echo "----------------------------------------"
python3 scripts/migrate_habits_phase7.py --dry-run --migrate-completions

echo ""
echo "Step 2: Review the dry-run output above"
echo "----------------------------------------"
read -p "Does everything look correct? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled. Please review and try again."
    exit 0
fi

echo ""
echo "Step 3: Running actual migration..."
echo "----------------------------------------"

if [ "$HAS_HABIT_LOGS" = false ]; then
    echo "⚠ Creating Habit Logs database first..."
    echo "Please run setup_notion_dbs.py and add HABIT_LOGS_DB_ID to .env"
    echo "Then run this script again."
    exit 1
fi

python3 scripts/migrate_habits_phase7.py --migrate-completions

echo ""
echo "=========================================="
echo "✓ Migration Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Check your Notion Habits database for new fields"
echo "2. Check your Notion Habit Logs database for entries"
echo "3. Proceed to Phase 7.2: Orchestration Layer Updates"
echo ""
