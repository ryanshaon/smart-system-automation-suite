#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

DATE_TAG="$(date '+%Y-%m-%d')"
LOG_FILE="$LOG_DIR/maintenance_${DATE_TAG}.log"
status="SUCCESS"
SUDO=()

log_message() {
  printf '[%s] %s\n' "$(timestamp)" "$1" >> "$LOG_FILE"
}

run_task() {
  local description="$1"
  shift
  log_message "START: $description"
  if "$@" >> "$LOG_FILE" 2>&1; then
    log_message "SUCCESS: $description"
  else
    log_message "ERROR: $description"
    status="ERROR"
  fi
}

log_message "=== System Maintenance Run Started ==="
log_message "User: $(whoami)"

if [[ "$(id -u)" -eq 0 ]]; then
  SUDO=()
elif command_exists sudo && sudo -n true >/dev/null 2>&1; then
  SUDO=(sudo)
else
  log_message "WARNING: Non-root user without passwordless sudo. Privileged operations will be skipped."
  status="WARNING"
fi

if command_exists apt-get; then
  if [[ "${#SUDO[@]}" -eq 0 && "$(id -u)" -ne 0 ]]; then
    log_message "SKIP: apt-get operations require root/sudo privileges."
  else
    run_task "Update package index" "${SUDO[@]}" apt-get update -y
    run_task "Upgrade installed packages" "${SUDO[@]}" apt-get upgrade -y
    run_task "Remove unnecessary packages" "${SUDO[@]}" apt-get autoremove -y
    run_task "Clean package cache" "${SUDO[@]}" apt-get autoclean -y
  fi
else
  log_message "SKIP: apt-get not found on this system."
fi

if command_exists journalctl; then
  if [[ "${#SUDO[@]}" -eq 0 && "$(id -u)" -ne 0 ]]; then
    log_message "SKIP: journal cleanup requires root/sudo privileges."
  else
    run_task "Vacuum system journal (older than 7 days)" "${SUDO[@]}" journalctl --vacuum-time=7d
  fi
fi

log_message "=== System Maintenance Run Finished with status: $status ==="
append_schedule_log "MAINT" "$status" "Maintenance run completed. Log stored at $LOG_FILE"
echo "Maintenance finished with status: $status"
