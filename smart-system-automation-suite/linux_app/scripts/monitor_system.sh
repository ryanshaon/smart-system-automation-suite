#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

DATE_TAG="$(date '+%Y-%m-%d')"
TIMESTAMP_TAG="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/system_monitor_${DATE_TAG}.log"
SNAPSHOT_FILE="$OUTPUT_DIR/system_snapshot_${TIMESTAMP_TAG}.txt"

{
  echo "=== Smart System Monitoring Snapshot ==="
  echo "Timestamp: $(timestamp)"
  echo "User: $(whoami)"
  echo "Hostname: $(hostname)"
  echo "Kernel: $(uname -srmo)"
  echo

  echo "---- Running Processes (Top CPU Consumers) ----"
  if command_exists ps; then
    ps aux --sort=-%cpu | head -n 15 || true
  else
    echo "ps command not available."
  fi
  echo

  echo "---- Memory Usage ----"
  if command_exists free; then
    free -h
  else
    echo "free command not available."
  fi
  echo

  echo "---- Disk Utilization ----"
  if command_exists df; then
    df -h
  else
    echo "df command not available."
  fi
  echo

  echo "---- Network Activity (Interface Stats) ----"
  if command_exists ip; then
    ip -s link
  elif command_exists ifconfig; then
    ifconfig -a
  else
    echo "Neither ip nor ifconfig command is available."
  fi
  echo

  echo "---- Network Connections Snapshot ----"
  if command_exists ss; then
    ss -tuna | head -n 40 || true
  elif command_exists netstat; then
    netstat -tuna | head -n 40 || true
  else
    echo "Neither ss nor netstat command is available."
  fi
} > "$SNAPSHOT_FILE"

cat "$SNAPSHOT_FILE" >> "$LOG_FILE"
echo >> "$LOG_FILE"

append_schedule_log "MONITOR" "SUCCESS" "System monitoring completed. Snapshot stored at $SNAPSHOT_FILE"
echo "Monitoring complete: $SNAPSHOT_FILE"
