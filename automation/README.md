# PersonalAxis Automation (macOS)

This directory contains the necessary files to automate the context generation for PersonalAxis using macOS `launchd`.

## Components

- **`launchd/`**: Contains the XML configuration files (plists).
  - `com.personalaxis.daily.plist`: Runs every morning at 08:00 to prepare the daily context.
  - `com.personalaxis.weekly.plist`: Runs every Sunday at 20:00 for the weekly review context.
  - `com.personalaxis.monthly.plist`: Runs on the 1st of every month at 00:05.
- **`install.sh`**: A script that configures the absolute paths, sets up the execution schedule, and loads the agents into `launchd`.

## Configuration

The automation schedule is defined at the top of `automation/install.sh`. You can modify these variables before running the script:

```bash
# Configuration for Schedule
DAILY_HOUR=8
DAILY_MINUTE=0
WEEKLY_DAY=7     # Sunday (1-7)
WEEKLY_HOUR=20
WEEKLY_MINUTE=0
MONTHLY_DAY=1
MONTHLY_HOUR=8
MONTHLY_MINUTE=0
```

## Setup

1. Ensure your virtual environment is created (`.venv` or `venv`).
2. Run the installer:
   ```bash
   ./automation/install.sh
   ```

## Managing Automation

### Check Status
```bash
launchctl list | grep personalaxis
```

### Unload/Disable
```bash
launchctl unload ~/Library/LaunchAgents/com.personalaxis.*.plist
```

### Logs
Logs are saved in the `logs/` directory at the project root:
- `logs/daily.log` / `logs/daily.error.log`
- `logs/weekly.log` / `logs/weekly.error.log`
- `logs/monthly.log` / `logs/monthly.error.log`

## Troubleshooting

If the scripts are not running as expected, check the `.error.log` files for Python traceback or path errors. Ensure the Python environment has all dependencies installed from `requirements.txt`.
