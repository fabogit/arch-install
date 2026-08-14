# Boot Theming: Plymouth & GRUB Customization

This guide details configuring **Plymouth** flicker-free boot splash screens and **GRUB** visual themes and startup melodies.

---

## 1. Plymouth Boot Splash

### 1.1 Install Plymouth
Install Plymouth from official repositories or AUR:
```bash
sudo pacman -S plymouth
```

### 1.2 Configure `mkinitcpio.conf`
Add the `plymouth` hook immediately **after** `udev` in `/etc/mkinitcpio.conf`:
```text
HOOKS=(base udev plymouth autodetect modconf kms keyboard keymap consolefont block filesystems fsck)
```

### 1.3 Update Kernel Command-Line
Edit `/etc/default/grub` and append to `GRUB_CMDLINE_LINUX_DEFAULT`:
```text
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash vt.global_cursor_default=0 fbcon=nodefer"
```

### 1.4 Select and Apply Theme
List available themes:
```bash
plymouth-set-default-theme -l
```

Set theme and rebuild initramfs:
```bash
sudo plymouth-set-default-theme -R spinner
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

---

## 2. GRUB Custom Themes & Sound Tunes

### 2.1 Install GRUB Theme
Themes are stored in [`configs/boot/grub/grub-themes/`](../../configs/boot/grub/grub-themes).

Copy theme to `/boot/grub/themes/`:
```bash
sudo mkdir -p /boot/grub/themes
sudo cp -r configs/boot/grub/grub-themes/<THEME_NAME> /boot/grub/themes/
```

Edit `/etc/default/grub`:
```ini
GRUB_THEME="/boot/grub/themes/<THEME_NAME>/theme.txt"
GRUB_GFXMODE="1920x1080,auto"
```

### 2.2 HiDPI & 4K Resolution Configuration
For high-resolution panels (such as 4K or Framework 13 2256x1504 displays), configure a fallback cascade in `/etc/default/grub` to avoid black screens while ensuring native sharpness:

```ini
# Fallback cascade: prioritize 4K/HiDPI, fallback to 1080p and auto
GRUB_GFXMODE="3840x2160x32,3840x2160,2256x1504,1920x1080,auto"

# Pass native framebuffer resolution to the Linux KMS console
GRUB_GFXPAYLOAD_LINUX="keep"
```

### 2.3 Optional: GRUB Startup Beep / Melody
To play a sound via PC speaker on bootloader initialization, edit `/etc/default/grub`:
```ini
GRUB_INIT_TUNE="1750 523 1 392 1 523 1 659 1 784 1 1047 1 784 1 415 1 523 1 622 1 831 1 622 1 831 1 1046 1 1244 1 1661 1 1244 1 466 1 587 1 698 1 932 1 1195 1 1397 1 1865 1 1397 1"
```

### 2.4 Regenerate GRUB Configuration
```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

