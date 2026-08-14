# PipeWire Audio Infrastructure Setup

This guide details the modern audio stack configuration for Arch Linux using **PipeWire** and **WirePlumber** session manager.

---

## 1. Installation

Install PipeWire packages and drop-in replacements for PulseAudio and JACK:
```bash
sudo pacman -S pipewire pipewire-pulse pipewire-alsa pipewire-jack wireplumber
```

### 1.1 Bluetooth Audio Codecs
Install high-quality Bluetooth codecs (LDAC, AptX):
```bash
sudo pacman -S libfreeaptx
# AUR package if needed:
yay -S libldac
```

---

## 2. Service Management

PipeWire runs entirely as a systemd user service. Ensure PulseAudio services are disabled and PipeWire is active:

```bash
systemctl --user enable --now pipewire.socket
systemctl --user enable --now pipewire-pulse.socket
systemctl --user enable --now wireplumber.service
```

---

## 3. Verification & Troubleshooting

Check active audio sinks and server status:
```bash
wpctl status
pactl info
```

Set default sink / source:
```bash
wpctl set-default <ID>
```
