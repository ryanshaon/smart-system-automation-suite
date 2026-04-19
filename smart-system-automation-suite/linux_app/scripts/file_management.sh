#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

DATE_TAG="$(date '+%Y-%m-%d')"
TIMESTAMP_TAG="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/file_management_${DATE_TAG}.log"
MANIFEST_FILE="$OUTPUT_DIR/backup_manifest_${DATE_TAG}.csv"
IMPORTANCE_FILE="$CONFIG_DIR/important_directories.conf"
SYNC_FILE="$CONFIG_DIR/sync_pairs.conf"

status="SUCCESS"
echo "label,path,description,archive,size,timestamp" > "$MANIFEST_FILE"

log_message() {
  printf '[%s] %s\n' "$(timestamp)" "$1" >> "$LOG_FILE"
}

backup_directory() {
  local label="$1"
  local raw_path="$2"
  local description="$3"
  local source_path
  source_path="$(expand_path "$raw_path")"

  if [[ ! -d "$source_path" ]]; then
    log_message "SKIP Backup: '$source_path' does not exist."
    status="WARNING"
    return
  fi

  local archive_name="${label}_${TIMESTAMP_TAG}.tar.gz"
  local archive_path="$BACKUP_DIR/$archive_name"

  if tar -czf "$archive_path" -C "$(dirname "$source_path")" "$(basename "$source_path")" >> "$LOG_FILE" 2>&1; then
    local archive_size
    archive_size="$(du -h "$archive_path" | awk '{print $1}')"
    printf '%s,%s,%s,%s,%s,%s\n' \
      "$label" "$source_path" "$description" "$archive_path" "$archive_size" "$(timestamp)" >> "$MANIFEST_FILE"
    log_message "SUCCESS Backup created for '$label' at '$archive_path' (size: $archive_size)."
  else
    log_message "ERROR Backup failed for '$source_path'."
    status="ERROR"
  fi
}

sync_pair() {
  local raw_src="$1"
  local raw_dest="$2"
  local src dest
  src="$(expand_path "$raw_src")"
  dest="$(expand_path "$raw_dest")"

  if [[ ! -d "$src" ]]; then
    log_message "SKIP Sync: source '$src' does not exist."
    status="WARNING"
    return
  fi

  mkdir -p "$dest"

  if command_exists rsync; then
    if rsync -a --delete "$src"/ "$dest"/ >> "$LOG_FILE" 2>&1; then
      log_message "SUCCESS Sync completed using rsync from '$src' to '$dest'."
    else
      log_message "ERROR rsync failed from '$src' to '$dest'."
      status="ERROR"
    fi
  else
    if cp -a "$src"/. "$dest"/ >> "$LOG_FILE" 2>&1; then
      log_message "SUCCESS Sync completed using cp fallback from '$src' to '$dest'."
    else
      log_message "ERROR cp fallback failed from '$src' to '$dest'."
      status="ERROR"
    fi
  fi
}

log_message "=== File Management Run Started ==="
log_message "User: $(whoami)"

while IFS='|' read -r label path description; do
  [[ -z "${label:-}" ]] && continue
  [[ "$label" =~ ^# ]] && continue
  backup_directory "$label" "$path" "$description"
done < "$IMPORTANCE_FILE"

while IFS='|' read -r src dest; do
  [[ -z "${src:-}" ]] && continue
  [[ "$src" =~ ^# ]] && continue
  sync_pair "$src" "$dest"
done < "$SYNC_FILE"

log_message "=== File Management Run Finished with status: $status ==="
append_schedule_log "FILES" "$status" "File management finished. Manifest stored at $MANIFEST_FILE"
echo "File management finished with status: $status"
