# BorgBackup: Arch (Framework 13) to Storage Server

This directory contains the automation script and configurations to perform an ultra-fast, native backup of a remote user home directory (running Arch Linux, accessible via SSH) onto a local or network Storage repository.

---

## Architecture and Workflow

The backup operates using a **Native Borg Push** model:

1. **Trigger**: The backup script executes on the storage host and connects to Arch via SSH.
2. **Package Export**: Arch exports explicitly installed official (`pacman`) and AUR (`yay`/`paru`) package lists to `pkglist_native.txt` and `pkglist_aur.txt`, which are automatically archived.
3. **Exclusion Sync**: The pattern list `exclude.txt` is synced to the target host via SCP.
4. **Native Backup**: BorgBackup runs directly on Arch, reading its local NVMe SSD at maximum speed. It calculates data chunk hashes, applies `zstd` compression, and pushes deduplicated chunks over SSH to the Storage repository (`ssh://<STORAGE_USER>@<STORAGE_IP><STORAGE_REPO>`).
5. **Pruning**: The storage host executes `borg prune` on the repository according to the retention policy.

---

## Files in the Project

* `backup-fw13-arch.sh`: The main automation script.
* `exclude.txt`: The exclusion pattern list (caches, trash, node_modules, virtual environments, site-packages, pnpm store, IDE WebStorage, and LLM models).
* `pkglist_native.txt`: Explicitly installed official repository packages from Arch Linux (`pacman`).
* `pkglist_aur.txt`: Explicitly installed foreign/AUR packages from Arch Linux (`yay`/`paru`).
* `README.md`: This documentation file.

---

## Usage Guide (How-To)

### 1. Run a Backup Manually
Ensure the remote laptop is powered on and connected to the local network, then execute:

```bash
# Run with default or custom environment variables
STORAGE_IP="<STORAGE_IP>" REMOTE_HOST="<REMOTE_HOSTNAME>" ./backup-fw13-arch.sh
```

### 2. List Existing Backups (Snapshots)
To view the list of archived snapshots stored in the repository:

```bash
borg list /path/to/storage/arch_backup/backup_arch_borg
```

### 3. Mount an Archive to Browse or Restore Individual Files
You can mount a specific archive as a local FUSE filesystem to browse files using your terminal or a file manager:

```bash
# Create the mount point
mkdir -p ~/mnt_restore

# Mount a specific archive (replace archive_name with the actual archive name)
borg mount /path/to/storage/arch_backup/backup_arch_borg::archive_name ~/mnt_restore

# Browse files via terminal or GUI file manager
ls -la ~/mnt_restore

# Once done, unmount the archive
borg umount ~/mnt_restore
```

### 4. Extract/Restore Data from an Archive
To directly restore a specific directory or file from an archive:

```bash
# Navigate to the target folder where you want to restore the files
cd /tmp

# Extract a specific directory from the archive
borg extract /path/to/storage/arch_backup/backup_arch_borg::archive_name home/<USERNAME>/Documents/important_project
```

### 5. Export Installed Package Lists
Package lists are exported automatically during backup, but can also be exported manually:

```bash
# Export official repository packages
ssh <REMOTE_HOST> "pacman -Qqen" > pkglist_native.txt

# Export AUR / foreign packages
ssh <REMOTE_HOST> "pacman -Qqem" > pkglist_aur.txt
```

### 6. Reinstall Packages on a Fresh System
To restore all installed applications on a fresh Arch Linux system:

```bash
# Reinstall all official repository packages
sudo pacman -S --needed - < pkglist_native.txt

# Install AUR packages with yay
yay -S --needed - < pkglist_aur.txt
```
