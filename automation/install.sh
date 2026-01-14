#!/bin/bash
# automation/install.sh
# Installs launchd plists and configures paths

# Get the absolute path of the project root
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)

# Detect virtual environment (prefer .venv, then venv)
if [ -d "$PROJECT_DIR/.venv" ]; then
    VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
elif [ -d "$PROJECT_DIR/venv" ]; then
    VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
else
    echo "Error: Virtual environment not found (.venv or venv). Please create one first."
    exit 1
fi

echo "Installing PersonalAxis automation..."
echo "Project Directory: $PROJECT_DIR"
echo "Python Executable: $VENV_PYTHON"

# Configuration for Schedule
DAILY_HOUR=15
DAILY_MINUTE=07
WEEKLY_DAY=7     # Sunday
WEEKLY_HOUR=20
WEEKLY_MINUTE=0
MONTHLY_DAY=1
MONTHLY_HOUR=8
MONTHLY_MINUTE=0

# Ensure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Update plist paths in-place (macOS sed requires empty extension for -i)
# We use | as a delimiter since paths contain /
sed -i '' "s|/path/to/PersonalAxis|$PROJECT_DIR|g" automation/launchd/*.plist
sed -i '' "s|/path/to/venv/bin/python|$VENV_PYTHON|g" automation/launchd/*.plist

# Update schedule times
sed -i '' "s|__DAILY_HOUR__|$DAILY_HOUR|g" automation/launchd/com.personalaxis.daily.plist
sed -i '' "s|__DAILY_MINUTE__|$DAILY_MINUTE|g" automation/launchd/com.personalaxis.daily.plist

sed -i '' "s|__WEEKLY_DAY__|$WEEKLY_DAY|g" automation/launchd/com.personalaxis.weekly.plist
sed -i '' "s|__WEEKLY_HOUR__|$WEEKLY_HOUR|g" automation/launchd/com.personalaxis.weekly.plist
sed -i '' "s|__WEEKLY_MINUTE__|$WEEKLY_MINUTE|g" automation/launchd/com.personalaxis.weekly.plist

sed -i '' "s|__MONTHLY_DAY__|$MONTHLY_DAY|g" automation/launchd/com.personalaxis.monthly.plist
sed -i '' "s|__MONTHLY_HOUR__|$MONTHLY_HOUR|g" automation/launchd/com.personalaxis.monthly.plist
sed -i '' "s|__MONTHLY_MINUTE__|$MONTHLY_MINUTE|g" automation/launchd/com.personalaxis.monthly.plist

# Copy to LaunchAgents
mkdir -p ~/Library/LaunchAgents
cp automation/launchd/*.plist ~/Library/LaunchAgents/

# Load agents (unload first to avoid 'service already loaded' error)
for plist in ~/Library/LaunchAgents/com.personalaxis.*.plist; do
    launchctl unload "$plist" 2>/dev/null
    launchctl load "$plist"
done

echo "✓ PersonalAxis automation installed and loaded!"
echo ""
echo "Schedules:"
echo "- Daily Context:  ${DAILY_HOUR}:${DAILY_MINUTE} daily           (com.personalaxis.daily)"
echo "- Weekly Review: Day ${WEEKLY_DAY} at ${WEEKLY_HOUR}:${WEEKLY_MINUTE}          (com.personalaxis.weekly)"
echo "- Monthly Review: Day ${MONTHLY_DAY} at ${MONTHLY_HOUR}:${MONTHLY_MINUTE}   (com.personalaxis.monthly)"
echo ""
echo "You can check status using: launchctl list | grep personalaxis"
echo "Logs are located in: $PROJECT_DIR/logs/"
