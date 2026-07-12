# BorgBackup: Arch (Framework 13) to Garuda (Storage)

This repository contains the automation script and configurations to perform a backup of the remote Framework 13 user home directory `/home/fabo` (running Arch Linux, accessible via SSH as `arch`) onto the local Storage disk connected to Garuda (`/run/media/fabo/Storage`).

---

## Architecture and Workflow

The backup operates in a **pull** model initiated from Garuda using SSHFS:

1. **Mounting**: The script creates a local directory `/home/fabo/mnt_arch` and mounts the remote home directory of Framework 13 via SSHFS.
2. **Backup**: BorgBackup scans the locally mounted directory, calculates data chunk hashes, applies `zstd` compression, and saves deduplicated chunks into the local repository `/run/media/fabo/Storage/backup_arch_borg`.
3. **Pruning**: Borg applies rotation rules to keep only a defined number of historical backups.
4. **Cleanup**: On completion (or fatal error), the script unmounts the SSHFS directory cleanly using `fusermount`.

---

## Files in the Project

* `backup-fw13-arch.sh`: The main backup execution script.
* `exclude.txt`: The exclusion pattern list (caches, trash, node_modules, virtual environments, and LLM models).
* `README.md`: This documentation file.

---

## Usage Guide (How-To)

### 1. Run a Backup Manually
Ensure the Framework 13 laptop is powered on and connected to the local network, then execute:

```bash
# Run the backup script
/home/fabo/borg-backup/backup-fw13-arch.sh
```

### 2. List Existing Backups (Snapshots)
To view the list of archived snapshots stored in the Storage repository:

```bash
# List all archives in the repository
borg list /run/media/fabo/Storage/backup_arch_borg
```

### 3. Mount an Archive to Browse or Restore Individual Files
You can mount a specific archive as a local FUSE filesystem to browse files using your terminal or a file manager:

```bash
# Create the mount point
mkdir -p /home/fabo/mnt_restore

# Mount a specific archive (replace archive_name with the actual archive name)
borg mount /run/media/fabo/Storage/backup_arch_borg::archive_name /home/fabo/mnt_restore

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
borg extract /run/media/fabo/Storage/backup_arch_borg::archive_name home/fabo/mnt_arch/Documents/important_project
```

*Note: Paths inside the archive preserve the structure relative to the original mount point (`home/fabo/mnt_arch/...`).*

---

## Retention Policy (Pruning)
The script is configured to automatically clean up old backups according to the following retention policy:
* **7 daily backups** (keep-daily)
* **4 weekly backups** (keep-weekly)
* **12 monthly backups** (keep-monthly)

---

## Troubleshooting

### SSHFS is hung ("Transport endpoint is not connected" or I/O Error)
If the network connection drops during a backup, the remote mountpoint might get stuck.
To resolve:
```bash
# Forcefully unmount the hung SSHFS directory
fusermount -uz /home/fabo/mnt_arch
```

### Repository is locked (Repository is locked)
If Borg is interrupted abruptly, it might leave a safety lock file behind.
To resolve:
```bash
# Break the stale lock of the repository
borg break-lock /run/media/fabo/Storage/backup_arch_borg
```
