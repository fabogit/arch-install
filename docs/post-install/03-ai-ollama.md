# Local AI & Ollama Acceleration (AMD iGPU / CPU)

This guide documents the setup of Ollama on Arch Linux with hardware acceleration on AMD APUs (e.g., AMD Ryzen 7 7840U with integrated Radeon 780M graphics) using Vulkan backend overrides, and fallback CPU configurations.

---

## 1. Installation

Install Ollama from official repositories:
```bash
sudo pacman -S ollama
```

---

## 2. AMD Radeon 780M (Vulkan iGPU) Acceleration

On AMD APUs sharing UMA system memory, Ollama requires specific environment flags to properly recognize and bind the integrated Vulkan compute device.

### 2.1 Systemd Service Override
Create the systemd drop-in override directory and file:
```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo nano /etc/systemd/system/ollama.service.d/override.conf
```

Insert the following configuration:
```ini
[Service]
# Force Ollama to use the Vulkan acceleration backend
Environment="OLLAMA_VULKAN=1"

# Map exclusively the first Vulkan device (Radeon 780M)
Environment="OLLAMA_VULKAN_DEVICE=0"

# Enable integrated GPU support (forces mapping on UMA shared memory)
Environment="OLLAMA_INTEGRATED_GPU=1"

# Disable experimental Vulkan Flash Attention to prevent shader freezes on RDNA3 iGPUs
Environment="OLLAMA_FLASH_ATTENTION=0"

# Bind Ollama API to localhost (or 0.0.0.0 for LAN access)
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"
```

### 2.2 Apply and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ollama.service
```

### 2.3 Verify Hardware Acceleration
Check journal logs to confirm Vulkan runner initialization:
```bash
journalctl -u ollama.service -b -n 50
```

---

## 3. Alternative: CPU-Only Fallback

If running on a system without a compatible GPU or when troubleshooting driver faults:

Create `/etc/systemd/system/ollama.service.d/override.conf`:
```ini
[Service]
Environment="OLLAMA_VULKAN=0"
Environment="OLLAMA_VULKAN_DEVICE="
Environment="OLLAMA_RUNNER=cpu"
Environment="OLLAMA_HOST=127.0.0.1:11434"
```

Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama.service
```
