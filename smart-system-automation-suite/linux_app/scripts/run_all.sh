#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

RUN_LOG="$LOG_DIR/automation_run_$(date '+%Y-%m-%d').log"
run_status="SUCCESS"

run_step() {
  local label="$1"
  local script_path="$2"
  printf '[%s] START %s\n' "$(timestamp)" "$label" >> "$RUN_LOG"
  if "$script_path" >> "$RUN_LOG" 2>&1; then
    printf '[%s] SUCCESS %s\n' "$(timestamp)" "$label" >> "$RUN_LOG"
  else
    printf '[%s] ERROR %s\n' "$(timestamp)" "$label" >> "$RUN_LOG"
    run_status="ERROR"
    append_schedule_log "RUNNER" "ERROR" "Step '$label' failed. See $RUN_LOG"
  fi
}

run_step "SYSTEM MONITORING" "$SCRIPT_DIR/monitor_system.sh"
run_step "FILE MANAGEMENT" "$SCRIPT_DIR/file_management.sh"
run_step "SYSTEM MAINTENANCE" "$SCRIPT_DIR/maintenance.sh"
run_step "REPORT GENERATION" "$SCRIPT_DIR/generate_report.sh"

append_schedule_log "RUNNER" "$run_status" "Master automation run completed. Log stored at $RUN_LOG"
echo "Master run completed with status: $run_status. See $RUN_LOG"
