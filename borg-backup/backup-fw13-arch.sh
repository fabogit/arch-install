#!/usr/bin/env bash

# Shell safety settings
set -euo pipefail

# Configuration
GARUDA_IP="192.168.1.50"
REMOTE_HOST="arch"
STORAGE_DIR="/run/media/fabo/Storage/arch_backup"
STORAGE_REPO="${STORAGE_DIR}/backup_arch_borg"
BORG_TARGET_REPO="ssh://fabo@${GARUDA_IP}${STORAGE_REPO}"
ARCHIVE_NAME="fw13-arch-$(date +'%Y-%m-%d-%H%M%S')"

echo "Exporting installed package lists from remote Arch..."
ssh "$REMOTE_HOST" "pacman -Qqen" > "$(dirname "$0")/pkglist_native.txt" || true
ssh "$REMOTE_HOST" "pacman -Qqem" > "$(dirname "$0")/pkglist_aur.txt" || true

# Copy package lists into project folder and into Storage/arch_backup directory
mkdir -p "$STORAGE_DIR"
cp "$(dirname "$0")/pkglist_"*.txt "$STORAGE_DIR/" || true

echo "Syncing exclude.txt pattern file to Arch via SCP..."
scp "$(dirname "$0")/exclude.txt" "$REMOTE_HOST":/home/fabo/exclude.txt

# Ensure any leftover lock on local repository or remote cache is cleared
borg break-lock "$STORAGE_REPO" || true
ssh "$REMOTE_HOST" "env BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS=yes borg break-lock '${BORG_TARGET_REPO}'" || true

echo "Starting native high-speed BorgBackup on Arch pushing to Garuda..."
set +e
ssh "$REMOTE_HOST" "env BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS=yes borg create \
    --verbose \
    --filter AME \
    --list \
    --stats \
    --show-rc \
    --compression zstd \
    --exclude-from /home/fabo/exclude.txt \
    '${BORG_TARGET_REPO}::${ARCHIVE_NAME}' \
    /home/fabo"
BORG_EXIT=$?
set -e

if [ $BORG_EXIT -eq 0 ]; then
    echo "BorgBackup completed successfully."
elif [ $BORG_EXIT -eq 1 ]; then
    echo "BorgBackup completed with warnings (some files changed during run)."
else
    echo "BorgBackup failed with critical error: $BORG_EXIT"
    exit $BORG_EXIT
fi

echo "Pruning old archives on local Storage repository..."
borg prune \
    --list \
    --glob-archives "fw13-arch-*" \
    --show-rc \
    --keep-daily 7 \
    --keep-weekly 4 \
    --keep-monthly 12 \
    "$STORAGE_REPO"
