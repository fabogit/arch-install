# System Performance & Maintenance Tuning

This guide documents essential post-installation optimizations, systemd tuning, kernel initramfs configuration, pacman automation hooks, and power/sleep configurations.

---

## 1. Systemd Shutdown & Reboot Timeouts

Avoid long shutdown delays caused by unresponsive background user processes or unmounting timeouts:

Edit `/etc/systemd/system.conf`:
```ini
[Manager]
DefaultTimeoutStopSec=10s
DefaultTimeoutAbortSec=10s
```

Apply immediately:
```bash
sudo systemctl daemon-reexec
```

---

## 2. Initramfs Optimization (`mkinitcpio`)

### 2.1 Enable Zstandard (ZSTD) Compression
Ensure `/etc/mkinitcpio.conf` uses modern `zstd` compression:
```bash
sudo sed -i 's/^#COMPRESSION="zstd"/COMPRESSION="zstd"/' /etc/mkinitcpio.conf
sudo mkinitcpio -P
```

---

## 3. Pacman Maintenance & Hooks

### 3.1 Automatic Cache Cleaning
Enable the systemd timer to automatically retain only the last 2 versions of installed packages and purge uninstalled package caches:
```bash
sudo pacman -S pacman-contrib
sudo systemctl enable --now paccache.timer
```

To clean AUR/yay cache:
```bash
yay -Sc --aur
```

### 3.2 Pre-Transaction `/boot` Backup Hook
Protects the boot partition before any kernel/system upgrade.

Create `/etc/pacman.d/hooks/50-bootbackup.hook`:
```ini
[Trigger]
Operation = Upgrade
Operation = Install
Operation = Remove
Type = Path
Target = boot/*

[Action]
Depends = rsync
Description = Backing up /boot partition to /.bootbackup ...
When = PreTransaction
Exec = /usr/bin/rsync -a --delete /boot /.bootbackup
```

---

## 4. Sleep & Hibernate Configuration

### 4.1 Swapfile Resume Hook
For laptops using a swapfile for hibernation on BTRFS or EXT4:

1. Identify the swap partition UUID:
```bash
findmnt -no UUID -T /swap/swapfile
```

2. Calculate resume offset for BTRFS swapfile:
```bash
btrfs inspect-internal map-swapfile -r /swap/swapfile
```

3. Add `resume` hook in `/etc/mkinitcpio.conf` **after** `udev` and `block`:
```text
HOOKS=(base udev autodetect modconf kms keyboard keymap consolefont block resume filesystems fsck)
```

4. Add resume kernel parameters to `/etc/default/grub`:
```text
GRUB_CMDLINE_LINUX_DEFAULT="... resume=UUID=<ROOT_UUID> resume_offset=<CALCULATED_OFFSET>"
```

5. Update initramfs and GRUB:
```bash
sudo mkinitcpio -P
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

---

## 5. Firmware Updates (`fwupd`)

Check for firmware updates (UEFI BIOS, Touchpad, NVMe SSDs, Framework components):
```bash
sudo pacman -S fwupd
fwupdmgr refresh
fwupdmgr get-updates
fwupdmgr update
```
