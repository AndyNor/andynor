#!/bin/bash
# local backup of database. no need to backup site or config
#
# Retention: keep every daily backup from roughly the last 30 days (mtime).
# Backups older than 30 days are thinned to one file per calendar month
# (the newest backup in that month, by timestamp in the filename).

set -euo pipefail

BACKUP_DIR="/home/django/django_project/andynor/backup"
DB_PATH="/home/django/django_project/andynor/db.sqlite3"

mkdir -p "$BACKUP_DIR"

tar -zcvf "$BACKUP_DIR/sqlite_$(date +%F_%H:%M:%S).tar.gz" "$DB_PATH"

# For backups older than 30 days: keep only one per YYYY-MM (newest in that month).
prune_old_monthlies() {
	local dir="$1"
	declare -A best_key=()
	declare -A best_file=()

	while IFS= read -r -d '' f; do
		local bn ym sortkey
		bn=$(basename "$f")
		sortkey=""
		if [[ $bn =~ ^sqlite_([0-9]{4}-[0-9]{2}-[0-9]{2})_([0-9]{2}):([0-9]{2}):([0-9]{2})\.tar\.gz$ ]]; then
			ym="${BASH_REMATCH[1]:0:7}"
			sortkey="${BASH_REMATCH[1]}_${BASH_REMATCH[2]}:${BASH_REMATCH[3]}:${BASH_REMATCH[4]}"
		else
			ym=$(LC_ALL=C date -r "$f" +%Y-%m)
			sortkey=$(LC_ALL=C date -r "$f" +%Y-%m-%d_%H:%M:%S)
		fi
		if [[ -z "${best_key[$ym]:-}" ]] || [[ "$sortkey" > "${best_key[$ym]}" ]]; then
			best_key[$ym]="$sortkey"
			best_file[$ym]="$f"
		fi
	done < <(find "$dir" -maxdepth 1 -type f -name 'sqlite_*.tar.gz' -mtime +30 -print0)

	while IFS= read -r -d '' f; do
		local bn ym keep
		bn=$(basename "$f")
		if [[ $bn =~ ^sqlite_([0-9]{4}-[0-9]{2}-[0-9]{2})_ ]]; then
			ym="${BASH_REMATCH[1]:0:7}"
		else
			ym=$(LC_ALL=C date -r "$f" +%Y-%m)
		fi
		keep="${best_file[$ym]:-}"
		if [[ -n "$keep" && "$f" != "$keep" ]]; then
			echo "Removing old backup (monthly retention): $f"
			rm -f -- "$f"
		fi
	done < <(find "$dir" -maxdepth 1 -type f -name 'sqlite_*.tar.gz' -mtime +30 -print0)
}

prune_old_monthlies "$BACKUP_DIR"
