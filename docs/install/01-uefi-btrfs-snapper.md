# Arch Linux Installation Guide: UEFI, BTRFS & Snapper

This guide details the complete bare-metal installation of Arch Linux on UEFI systems using **BTRFS** with optimized subvolumes, automated **Snapper** snapshots, and **GRUB** integration for snapshot rollback.

> [!NOTE]
> This guide is aligned with the official [Arch Linux Installation Guide](https://wiki.archlinux.org/title/Installation_guide) and [BTRFS Wiki documentation](https://wiki.archlinux.org/title/Btrfs).

---

## 1. Pre-Installation

### 1.1 Set Console Keyboard Layout
```bash
loadkeys it
# Or 'loadkeys us' for US English
```

### 1.2 Verify Boot Mode
Verify that the system booted in UEFI mode (command should return `64` or `32`, not an error):
```bash
cat /sys/firmware/efi/fw_platform_size
```

### 1.3 Connect to the Internet
- **Ethernet**: Usually automatic via DHCP. Verify with `ip link` or `ip a`.
- **Wi-Fi**: Use `iwctl`:
```bash
iwctl
# Inside iwctl prompt:
station wlan0 scan
station wlan0 get-networks
station wlan0 connect "<SSID>"
exit
```
Verify connectivity:
```bash
ping -c 3 archlinux.org
```

### 1.4 Optional: Enable SSH for Remote Installation
To execute the installation from another machine on the local network:
```bash
passwd
systemctl start sshd.service
ip a
```
Connect from your remote workstation:
```bash
ssh root@<TARGET_IP_ADDRESS>
```

### 1.5 Sync System Clock
```bash
timedatectl set-ntp true
```

### 1.6 Update Mirrorlist
Rank the 20 fastest HTTPS mirrors in your region:
```bash
reflector --country Italy,Germany,France --protocol https --sort rate --save /etc/pacman.d/mirrorlist
pacman -Sy
```

---

## 2. Disk Partitioning

Identify target drive (e.g., `/dev/nvme0n1` or `/dev/sda`):
```bash
lsblk
```

### 2.1 Partition Table Layout (GPT)
Use `cfdisk` or `fdisk`:
```bash
cfdisk /dev/nvme0n1
```
Create the following layout:
1. **Partition 1 (EFI System Partition)**: `1G` (Type: `EFI System`)
2. **Partition 2 (BTRFS Root Partition)**: Remaining space (Type: `Linux filesystem`)

### 2.2 Format Partitions
```bash
# Format EFI partition as FAT32
mkfs.fat -F 32 /dev/nvme0n1p1

# Format root partition as BTRFS
mkfs.btrfs -f -L "ARCH_ROOT" /dev/nvme0n1p2
```

---

## 3. BTRFS Subvolume Setup

Mount the root BTRFS partition temporarily to create subvolumes:
```bash
mount /dev/nvme0n1p2 /mnt
```

### 3.1 Create Subvolumes
```bash
btrfs subvolume create /mnt/@
btrfs subvolume create /mnt/@home
btrfs subvolume create /mnt/@snapshots
btrfs subvolume create /mnt/@var_log
btrfs subvolume create /mnt/@var_cache
btrfs subvolume create /mnt/@var_tmp
btrfs subvolume create /mnt/@swap
```

Unmount temporary mount:
```bash
umount /mnt
```

### 3.2 Mount Subvolumes with Optimized Options
Recommended BTRFS mount flags: `noatime,compress=zstd,space_cache=v2`.
```bash
BTRFS_OPTS="noatime,compress=zstd,space_cache=v2"

# Mount root subvolume
mount -o ${BTRFS_OPTS},subvol=@ /dev/nvme0n1p2 /mnt

# Create mount directories
mkdir -p /mnt/{boot,home,.snapshots,var/log,var/cache,var/tmp,swap}

# Mount subvolumes
mount -o ${BTRFS_OPTS},subvol=@home /dev/nvme0n1p2 /mnt/home
mount -o ${BTRFS_OPTS},subvol=@snapshots /dev/nvme0n1p2 /mnt/.snapshots
mount -o ${BTRFS_OPTS},subvol=@var_log /dev/nvme0n1p2 /mnt/var/log
mount -o ${BTRFS_OPTS},subvol=@var_cache /dev/nvme0n1p2 /mnt/var/cache
mount -o ${BTRFS_OPTS},subvol=@var_tmp /dev/nvme0n1p2 /mnt/var/tmp
mount -o ${BTRFS_OPTS},subvol=@swap /dev/nvme0n1p2 /mnt/swap

# Mount EFI System Partition
mount /dev/nvme0n1p1 /mnt/boot
```

### 3.3 Optional: BTRFS Swapfile Setup
```bash
btrfs filesystem mkswapfile --size 16G --uuid clear /mnt/swap/swapfile
swapon /mnt/swap/swapfile
```

---

## 4. Install Base System

Use `pacstrap` with `-K` to initialize the pacman keyring inside the new install:
```bash
pacstrap -K /mnt base base-devel linux linux-firmware amd-ucode btrfs-progs nano git sudo networkmanager
# Note: Replace 'amd-ucode' with 'intel-ucode' if on an Intel processor.
```

---

## 5. System Configuration

### 5.1 Generate Fstab
```bash
genfstab -U /mnt >> /mnt/etc/fstab
```
Verify generated entries:
```bash
cat /mnt/etc/fstab
```

### 5.2 Enter Chroot
```bash
arch-chroot /mnt
```

### 5.3 Timezone and Clock
```bash
ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime
hwclock --systohc
```

### 5.4 Localization
Edit `/etc/locale.gen` and uncomment required locales:
```bash
sed -i 's/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
sed -i 's/#it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
```
Set system language in `/etc/locale.conf`:
```bash
echo "LANG=en_US.UTF-8" > /etc/locale.conf
echo "KEYMAP=it" > /etc/vconsole.conf
```

### 5.5 Network Configuration
```bash
echo "<HOSTNAME>" > /etc/hostname

cat <<EOF > /etc/hosts
127.0.0.1   localhost
::1         localhost
127.0.1.1   <HOSTNAME>.localdomain <HOSTNAME>
EOF
```
Enable NetworkManager:
```bash
systemctl enable NetworkManager.service
```

### 5.6 User and Root Account
Set root password:
```bash
passwd
```
Create normal user with sudo privileges:
```bash
useradd -m -G wheel -s /bin/bash <USERNAME>
passwd <USERNAME>
```
Allow members of group `wheel` to use sudo:
```bash
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/10-wheel
chmod 440 /etc/sudoers.d/10-wheel
```

---

## 6. Initramfs & Bootloader (GRUB)

### 6.1 Initramfs (`mkinitcpio`)
Ensure `btrfs` is listed in modules or hooks in `/etc/mkinitcpio.conf` if required, then regenerate:
```bash
mkinitcpio -P
```

### 6.2 Install GRUB for UEFI
Install GRUB and dependencies:
```bash
pacman -S grub efibootmgr dosfstools mtools os-prober
```
Install GRUB to ESP:
```bash
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

---

## 7. Snapper & Snapshot Boot Integration

### 7.1 Install Snapper & Tools
```bash
pacman -S snapper snap-pac inotify-tools
```

### 7.2 Configure Snapper for Root
Unmount `@snapshots` temporarily to let snapper initialize its config:
```bash
umount /.snapshots
rm -r /.snapshots
snapper -c root create-config /
```
Delete default subvolume created by snapper and re-link `@snapshots`:
```bash
btrfs subvolume delete /.snapshots
mkdir /.snapshots
mount -o ${BTRFS_OPTS},subvol=@snapshots /dev/nvme0n1p2 /.snapshots
```

### 7.3 Enable Automatic Snapper Timeline & Cleanup
```bash
systemctl enable snapper-timeline.timer
systemctl enable snapper-cleanup.timer
```

---

## 8. Finalizing and Reboot

Exit chroot, unmount all partitions, and reboot:
```bash
exit
umount -R /mnt
reboot
```
