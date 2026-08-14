# Arch Linux Installation Guide: UEFI, LVM & EXT4

This guide details the traditional installation of Arch Linux on UEFI systems using **LVM2 (Logical Volume Manager)** on top of **EXT4** partitions.

> [!NOTE]
> For advanced snapshot capabilities, subvolumes, and transparent compression, consider using the [BTRFS & Snapper Guide](01-uefi-btrfs-snapper.md).

---

## 1. Partitioning for LVM

Identify the target drive (e.g., `/dev/nvme0n1`):
```bash
lsblk
cfdisk /dev/nvme0n1
```

Create the following layout:
1. **Partition 1 (EFI System Partition)**: `1G` (Type: `EFI System`)
2. **Partition 2 (LVM Physical Volume)**: Remaining space (Type: `Linux LVM`)

---

## 2. LVM Setup

### 2.1 Create Physical Volume & Volume Group
```bash
pvcreate /dev/nvme0n1p2
vgcreate archVG /dev/nvme0n1p2
```

### 2.2 Create Logical Volumes
```bash
# Root logical volume (e.g. 80GB)
lvcreate -L 80G archVG -n root

# Swap logical volume (e.g. 16GB)
lvcreate -L 16G archVG -n swap

# Home logical volume (using remaining free space)
lvcreate -l 100%FREE archVG -n home
```

### 2.3 Format Logical Volumes & EFI Partition
```bash
# Format EFI partition
mkfs.fat -F 32 /dev/nvme0n1p1

# Format root and home as EXT4
mkfs.ext4 /dev/archVG/root
mkfs.ext4 /dev/archVG/home

# Setup swap
mkswap /dev/archVG/swap
swapon /dev/archVG/swap
```

---

## 3. Mount Partitions & Base Install

```bash
# Mount root
mount /dev/archVG/root /mnt

# Create mount points
mkdir -p /mnt/{boot,home}

# Mount home and EFI boot
mount /dev/archVG/home /mnt/home
mount /dev/nvme0n1p1 /mnt/boot
```

Install base packages with pacstrap:
```bash
pacstrap -K /mnt base base-devel linux linux-firmware amd-ucode lvm2 e2fsprogs nano git sudo networkmanager
```

---

## 4. System Configuration & Chroot

```bash
# Generate fstab
genfstab -U /mnt >> /mnt/etc/fstab

# Enter chroot
arch-chroot /mnt
```

### 4.1 Time, Locale & Network
```bash
ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime
hwclock --systohc

sed -i 's/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
sed -i 's/#it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen
locale-gen

echo "LANG=en_US.UTF-8" > /etc/locale.conf
echo "<HOSTNAME>" > /etc/hostname
systemctl enable NetworkManager.service
```

### 4.2 Configure Initramfs for LVM
Edit `/etc/mkinitcpio.conf` and ensure `lvm2` is added to `HOOKS` before `filesystems`:
```text
HOOKS=(base udev autodetect modconf kms keyboard keymap consolefont block lvm2 filesystems fsck)
```
Regenerate initramfs:
```bash
mkinitcpio -P
```

### 4.3 Users & Bootloader
```bash
passwd
useradd -m -G wheel -s /bin/bash <USERNAME>
passwd <USERNAME>
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/10-wheel

# Install GRUB
pacman -S grub efibootmgr
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

---

## 5. Finish and Reboot

```bash
exit
umount -R /mnt
reboot
```
