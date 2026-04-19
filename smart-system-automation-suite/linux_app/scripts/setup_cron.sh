#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CRON_TEMPLATE="$BASE_DIR/crontab/smart_suite_crontab.txt"

cat > "$CRON_TEMPLATE" <<EOF
# SMART_SUITE: Smart System Automation & Monitoring Suite
# Monitor every 15 minutes
*/15 * * * * $BASE_DIR/scripts/monitor_system.sh >> $LOG_DIR/cron_monitor.log 2>&1
# File management every 6 hours
0 */6 * * * $BASE_DIR/scripts/file_management.sh >> $LOG_DIR/cron_file_management.log 2>&1
# Daily maintenance at 2:30 AM
30 2 * * * $BASE_DIR/scripts/maintenance.sh >> $LOG_DIR/cron_maintenance.log 2>&1
# Daily report generation at 11:45 PM
45 23 * * * $BASE_DIR/scripts/generate_report.sh >> $LOG_DIR/cron_report.log 2>&1
EOF

echo "Cron template generated at: $CRON_TEMPLATE"

if [[ "${1:-}" == "--install" ]]; then
  existing="$(mktemp)"
  combined="$(mktemp)"

  crontab -l 2>/dev/null | grep -v 'SMART_SUITE' > "$existing" || true
  cat "$existing" "$CRON_TEMPLATE" > "$combined"
  crontab "$combined"

  rm -f "$existing" "$combined"
  echo "Cron entries installed successfully."
fi
