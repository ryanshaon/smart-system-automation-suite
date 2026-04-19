# Assignment 2 Report - Smart System Automation & Monitoring Suite

Student Username in Logs: `<username>`  
Assignment Source: `Assignment_2_Scripting.pdf`

## 1. Application 1 - Linux-Based Automation System

### Part A - System Monitoring Setup

Implemented in:

- `linux_app/scripts/monitor_system.sh`

Data captured:

- Running processes (`ps aux --sort=-%cpu`)
- Memory usage (`free -h`)
- Disk utilization (`df -h`)
- Network activity (`ip -s link` + `ss -tuna`)

Generated files:

- `linux_app/logs/system_monitor_YYYY-MM-DD.log`
- `linux_app/output/system_snapshot_YYYY-MM-DD_HH-MM-SS.txt`

### Part B - Automated File Management

Implemented in:

- `linux_app/scripts/file_management.sh`
- `linux_app/config/important_directories.conf`
- `linux_app/config/sync_pairs.conf`

Selected important directories and description:

1. `~/Documents` - academic notes, assignments, and references
2. `~/Downloads` - source PDFs, datasets, and files
3. `~/smart-system-automation-suite` - project code and generated outputs

Operations performed:

- Backup directory data
- Compress backups to `.tar.gz`
- Synchronize source directories to mirror locations

Generated files:

- `linux_app/output/backup_manifest_YYYY-MM-DD.csv`
- `linux_app/backups/*.tar.gz`

### Part C - Scheduled Execution

Implemented in:

- `linux_app/scripts/setup_cron.sh`
- `linux_app/crontab/cron_jobs_example.txt`
- `linux_app/logs/schedule_execution.log`

Schedule used:

1. Monitor every 15 minutes
2. File management every 6 hours
3. Maintenance at 2:30 AM daily
4. Report generation at 11:45 PM daily

Evidence of 3-day scheduling logs included for:

- `2026-04-16`
- `2026-04-17`
- `2026-04-18`

### Part D - System Maintenance Automation

Implemented in:

- `linux_app/scripts/maintenance.sh`

Tasks included:

- Package index update
- Package upgrade
- Autoremove and cache cleanup
- Journal cleanup

### Part E - Linux Report Generation

Implemented in:

- `linux_app/scripts/generate_report.sh`

Consolidated report includes:

- System resource usage summary
- Backup operations performed
- Frequency of scheduled execution
- Overall system health status

Output:

- `linux_app/output/linux_consolidated_report_2026-04-18.txt`

## 2. Application 2 - Python-Based Automation System

Main implementation:

- `python_app/automation_suite.py`

### Part F - Directory Management Model

- `DirectoryInfo` dataclass stores path, file count, last accessed time, and last updated time.
- `DirectoryRegistry` maintains multiple tracked directories from `python_app/data/directories.json`.

### Part G - Interactive Menu System

Menu includes:

1. View directory status
2. Add/remove directory in model
3. Organize files
4. Rename/remove/copy/move files and folders
5. Execute automated bundle
6. Generate analytical report
7. View analytics summary

### Part H - File Automation Engine

- `FileAutomationEngine` implements:
  - organize files by extension
  - rename files
  - remove files/folders
  - copy files/folders
  - move files/folders

### Part I - Logging and Time Tracking

- Runtime logs in `python_app/logs/automation.log`
- Action history with timestamps in `python_app/data/operations_history.json`

### Part J - Analytical Reporting

- `OperationTracker.analytics()` computes:
  - total operations
  - most frequently used directories
  - usage trends by date
  - error statistics
- Reports generated in `python_app/reports/analytics_report_*.txt`

### Part K - Robust Error Handling

Handled cases:

- Invalid menu options
- Missing files/directories
- Invalid path input
- Permission and unexpected runtime errors

The menu loop continues without abrupt termination after handled errors.

## 3. How To Run

### Linux application

```bash
cd /home/<username>/smart-system-automation-suite/linux_app
chmod +x scripts/*.sh
./scripts/run_all.sh
./scripts/setup_cron.sh --install
```

### Python application

```bash
cd /home/<username>/smart-system-automation-suite/python_app
python3 automation_suite.py
```

## 4. Submission Checklist Mapping

1. Source code for both applications: included in `linux_app/` and `python_app/`
2. Evidence of scheduled execution: included in `linux_app/logs/` (3-day logs)
3. Output files: included in `linux_app/output/` and `python_app/reports/`
4. Short report: this file (`docs/assignment_report.md`)

## 5. Screenshot Guidance

To satisfy the note requiring username in output screenshots:

1. Run `whoami` before script execution.
2. Capture terminal screenshots showing command + output.
3. Include logs where `[user:<username>]` appears in schedule entries.

