# BorgBackup: Arch (Framework 13) to Garuda (Storage)

This repository contains the automation script and configurations to perform an ultra-fast, native backup of the remote Framework 13 user home directory `/home/fabo` (running Arch Linux, accessible via SSH as `arch`) onto the local Storage disk connected to Garuda (`/run/media/fabo/Storage/arch_backup`).

---

## Architecture and Workflow

The backup operates using a **Native Borg Push** model initiated from Garuda:

1. **Trigger**: The local script on Garuda connects to Arch via SSH.
2. **Package Export**: Arch exports explicitly installed official (`pacman`) and AUR (`yay`/`paru`) package lists to `pkglist_native.txt` and `pkglist_aur.txt`, which are automatically backed up to `/run/media/fabo/Storage/arch_backup/`.
3. **Exclusion Sync**: Garuda syncs `exclude.txt` to Arch via SCP.
4. **Native Backup**: BorgBackup runs directly on Arch, reading its local NVMe SSD at maximum speed. It calculates data chunk hashes, applies `zstd` compression, and pushes deduplicated chunks over SSH to Garuda's local repository (`ssh://fabo@192.168.1.50/run/media/fabo/Storage/arch_backup/backup_arch_borg`).
5. **Pruning**: Garuda executes `borg prune` on the local repository to maintain the retention policy.

---

## Files in the Project

* `backup-fw13-arch.sh`: The main automation script executed from Garuda.
* `exclude.txt`: The exclusion pattern list (caches, trash, node_modules, virtual environments, site-packages, pnpm store, IDE WebStorage, and LLM models).
* `pkglist_native.txt`: Explicitly installed official repository packages from Arch Linux (`pacman`).
* `pkglist_aur.txt`: Explicitly installed foreign/AUR packages from Arch Linux (`yay`/`paru`).
* `README.md`: This documentation file.

---

## Usage Guide (How-To)

### 1. Run a Backup Manually
Ensure the Framework 13 laptop is powered on and connected to the local network, then execute from Garuda:

```bash
# Run the backup script
/home/fabo/borg-backup/backup-fw13-arch.sh
```

### 2. List Existing Backups (Snapshots)
To view the list of archived snapshots stored in the Storage repository:

```bash
# List all archives in the repository
borg list /run/media/fabo/Storage/arch_backup/backup_arch_borg
```

### 3. Mount an Archive to Browse or Restore Individual Files
You can mount a specific archive as a local FUSE filesystem on Garuda to browse files using your terminal or a file manager:

```bash
# Create the mount point
mkdir -p /home/fabo/mnt_restore

# Mount a specific archive (replace archive_name with the actual archive name)
borg mount /run/media/fabo/Storage/arch_backup/backup_arch_borg::archive_name /home/fabo/mnt_restore

# Browse files via terminal or GUI file manager
ls -la /home/fabo/mnt_restore

# Once done, unmount the archive
borg umount /home/fabo/mnt_restore
```

### 4. Extract/Restore Data from an Archive
To directly restore a specific directory or file from an archive:

```bash
# Navigate to the folder where you want to restore the files
cd /tmp

# Extract a specific directory from the archive
borg extract /run/media/fabo/Storage/arch_backup/backup_arch_borg::archive_name home/fabo/Documents/important_project
```

*Note: Paths inside the archive preserve the structure relative to the user home directory (`home/fabo/...`).*

### 5. Export Installed Package Lists
Package lists are exported automatically during backup, but can also be exported manually:

```bash
# Export official repository packages
ssh arch "pacman -Qqen" > /home/fabo/borg-backup/pkglist_native.txt

# Export AUR / foreign packages
ssh arch "pacman -Qqem" > /home/fabo/borg-backup/pkglist_aur.txt

# Sync lists to external storage
cp /home/fabo/borg-backup/pkglist_*.txt /run/media/fabo/Storage/arch_backup/
```

### 6. Reinstall Packages on a Fresh System
To restore all installed applications on a new or fresh Arch Linux system:

```bash
# Reinstall all official repository packages
sudo pacman -S --needed - < /run/media/fabo/Storage/arch_backup/pkglist_native.txt

# Install AUR helper (yay) if not already present
sudo pacman -S --needed base-devel git
git clone https://aur.archlinux.org/yay.git /tmp/yay
cd /tmp/yay && makepkg -si --noconfirm

# Reinstall all AUR packages
yay -S --needed - < /run/media/fabo/Storage/arch_backup/pkglist_aur.txt
```

---

## Retention Policy (Pruning)
The script automatically cleans up old backups according to the following retention policy:
* **7 daily backups** (keep-daily)
* **4 weekly backups** (keep-weekly)
* **12 monthly backups** (keep-monthly)

---

## Troubleshooting

### Repository is locked (Failed to acquire lock)
If a backup is interrupted abruptly (e.g. Ctrl+C), a stale lock file might remain.
The script automatically runs `break-lock`, but you can also clear it manually:

```bash
# Break local repository lock on Garuda
borg break-lock /run/media/fabo/Storage/arch_backup/backup_arch_borg

# Break remote cache lock on Arch
ssh arch "env BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS=yes borg break-lock ssh://fabo@192.168.1.50/run/media/fabo/Storage/arch_backup/backup_arch_borg"
```
