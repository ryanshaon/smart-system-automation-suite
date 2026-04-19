# Linux-Based Automation System

## Files

- `scripts/monitor_system.sh` - Collects process, memory, disk, and network metrics.
- `scripts/file_management.sh` - Creates backups, compresses archives, and synchronizes directories.
- `scripts/maintenance.sh` - Runs periodic cleanup and package maintenance tasks.
- `scripts/generate_report.sh` - Produces consolidated Linux status report.
- `scripts/run_all.sh` - Runs all Linux tasks in sequence.
- `scripts/setup_cron.sh` - Generates/install cron entries.
- `config/important_directories.conf` - Directories selected for backup with descriptions.
- `config/sync_pairs.conf` - Source and destination directory sync mapping.
- `crontab/cron_jobs_example.txt` - Example cron schedule.
- `logs/` - Execution and schedule logs (includes sample 3-day logs).
- `output/` - Generated manifests and consolidated reports.

## Execution Steps (Ubuntu)

```bash
cd /home/<username>/smart-system-automation-suite/linux_app
chmod +x scripts/*.sh
./scripts/run_all.sh
./scripts/setup_cron.sh --install
```

## Important Notes

- The scripts include `whoami` in logs to satisfy username evidence.
- Update `config/important_directories.conf` to match your own Ubuntu directories if required.

