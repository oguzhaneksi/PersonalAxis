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

# Ensure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Update plist paths in-place (macOS sed requires empty extension for -i)
# We use | as a delimiter since paths contain /
sed -i '' "s|/path/to/PersonalAxis|$PROJECT_DIR|g" automation/launchd/*.plist
sed -i '' "s|/path/to/venv/bin/python|$VENV_PYTHON|g" automation/launchd/*.plist

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
echo "- Daily Context:  08:00 daily           (com.personalaxis.daily)"
echo "- Weekly Review: Sunday 20:00          (com.personalaxis.weekly)"
echo "- Monthly Review: 1st of month 08:00   (com.personalaxis.monthly)"
echo ""
echo "You can check status using: launchctl list | grep personalaxis"
echo "Logs are located in: $PROJECT_DIR/logs/"
