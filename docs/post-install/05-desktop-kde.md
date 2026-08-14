# KDE Plasma Desktop & System Integration

This guide details KDE Plasma setup, software center integration (Discover, Flatpak, PackageKit), Bluetooth battery metrics, and root theme synchronization.

---

## 1. KDE Plasma Installation

Install core Plasma environment and essential applications:
```bash
sudo pacman -S plasma-meta kde-applications-meta
```

Enable Display Manager:
```bash
sudo systemctl enable sddm.service
```

---

## 2. KDE Discover & Package Backends

To enable full update support and Flatpak integration in Discover:
```bash
sudo pacman -S discover packagekit-qt6 flatpak fwupd archlinux-appstream-data
```

---

## 3. Bluetooth Battery Percentage Reporting

Enable BlueZ experimental features to view battery percentage of connected Bluetooth peripherals in the system tray:

Edit `/etc/bluetooth/main.conf`:
```ini
[General]
Experimental = true
```

Restart bluetooth daemon:
```bash
sudo systemctl restart bluetooth.service
```

---

## 4. Root Theme Synchronization

To ensure root GUI applications (e.g., Partition Manager, KWrite) match user dark/light themes:

```bash
sudo mkdir -p /root/.config
sudo cp -r ~/.config/kdeglobals /root/.config/
```

---

## 5. Network Sharing (Samba & KIO)

Enable local network folder browsing and Windows network integration:
```bash
sudo pacman -S samba kio-fuse kdenetwork-filesharing
sudo systemctl enable --now smb.service
```
