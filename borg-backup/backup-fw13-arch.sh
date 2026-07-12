#!/usr/bin/env bash

# Shell safety settings:
# -e: Exit immediately if any command fails (returns non-zero status).
# -u: Treat unset variables as an error and exit immediately.
# -o pipefail: Ensure that pipeline commands return the exit status of the last command to fail.
set -euo pipefail

# ==============================================================================
# Configuration Section
# ==============================================================================

# Path to the local Borg repository on the external Storage disk.
export BORG_REPO="/run/media/fabo/Storage/backup_arch_borg"

# Local directory where the remote Arch home filesystem will be mounted.
MOUNT_POINT="/home/fabo/mnt_arch"

# Remote source specification using the SSH alias 'arch' defined in ~/.ssh/config.
REMOTE_SOURCE="arch:/home/fabo"

# Unique archive name combining host description and the current date/time.
ARCHIVE_NAME="fw13-arch-$(date +'%Y-%m-%d-%H%M%S')"

# ==============================================================================
# Mounting Remote Filesystem via SSHFS
# ==============================================================================

# Create the local mount directory if it doesn't already exist.
mkdir -p "$MOUNT_POINT"

# Check if the directory is already mounted. If so, attempt to unmount it first
# to avoid overlay mount errors or locked states.
if mountpoint -q "$MOUNT_POINT"; then
    echo "Warning: $MOUNT_POINT is already mounted. Attempting to unmount..."
    fusermount -u "$MOUNT_POINT" || true
fi

echo "Mounting remote Arch home via SSHFS..."
# Mount remote path with options for resiliency:
# - follow_symlinks: Resolves symlinks on the remote host side.
# - reconnect: Automatically tries to reconnect if the connection drops.
# - ServerAliveInterval / ServerAliveCountMax: Sends keepalive packets every 15s,
#   dropping the connection cleanly after 3 missed responses (45s total).
sshfs "$REMOTE_SOURCE" "$MOUNT_POINT" -o follow_symlinks,reconnect,ServerAliveInterval=15,ServerAliveCountMax=3

# Trap function to ensure cleanup on exit.
# Regardless of success, warning, or failure, the mountpoint will be cleanly
# unmounted when the shell script exits.
cleanup() {
    echo "Cleaning up: unmounting SSHFS..."
    if mountpoint -q "$MOUNT_POINT"; then
        fusermount -u "$MOUNT_POINT" || true
    fi
}
# Register the cleanup function to be called on script termination (EXIT signal).
trap cleanup EXIT

# ==============================================================================
# Executing BorgBackup
# ==============================================================================

echo "Starting BorgBackup to $BORG_REPO..."

# Temporarily disable 'exit-on-error' (set +e) because Borg create returns:
# - 0: Success.
# - 1: Warning (e.g. files changed during backup run).
# - 2: Error.
# We want to catch exit code 1 and treat it as non-fatal so we can still prune.
set +e
borg create \
    --verbose \
    --filter AME \
    --list \
    --stats \
    --show-rc \
    --exclude-from "$(dirname "$0")/exclude.txt" \
    "::$ARCHIVE_NAME" \
    "$MOUNT_POINT"
BORG_EXIT=$?
# Re-enable 'exit-on-error' safety setting.
set -e

# Evaluate Borg's exit status.
if [ $BORG_EXIT -eq 0 ]; then
    echo "BorgBackup completed successfully."
elif [ $BORG_EXIT -eq 1 ]; then
    # Exit code 1 is a warning, common for active home folders (e.g., active log files).
    echo "BorgBackup completed with warnings (some files changed during run)."
else
    # Exit code 2 is a critical error (e.g. network failure, repository corruption).
    echo "BorgBackup failed with critical error: $BORG_EXIT"
    exit $BORG_EXIT
fi

# ==============================================================================
# Pruning Old Archives (Rotation Policy)
# ==============================================================================

echo "Pruning old archives..."
# Keep a defined window of backups to optimize storage space:
# --keep-daily 7:   Keep one backup per day for the last 7 days.
# --keep-weekly 4:  Keep one backup per week for the last 4 weeks.
# --keep-monthly 12: Keep one backup per month for the last 12 months.
borg prune \
    --list \
    --prefix "fw13-arch-" \
    --show-rc \
    --keep-daily 7 \
    --keep-weekly 4 \
    --keep-monthly 12 \
    "::"
