#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
OUTPUT_DIR="$BASE_DIR/output"
BACKUP_DIR="$BASE_DIR/backups"
CONFIG_DIR="$BASE_DIR/config"
SCHEDULE_LOG="$LOG_DIR/schedule_execution.log"

mkdir -p "$LOG_DIR" "$OUTPUT_DIR" "$BACKUP_DIR"

timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

expand_path() {
  local raw_path="$1"
  eval "echo \"$raw_path\""
}

append_schedule_log() {
  local task="$1"
  local status="$2"
  local message="$3"
  printf '[%s] [%s] [%s] [user:%s] %s\n' \
    "$(timestamp)" "$task" "$status" "$(whoami)" "$message" >> "$SCHEDULE_LOG"
}
