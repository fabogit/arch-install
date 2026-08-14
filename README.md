# Arch Linux Setup & Infrastructure Repository

Comprehensive installation guides, post-install configurations, system tuning tools, and automation backups for Arch Linux workstations (optimized for Framework 13 AMD Ryzen 7 7840U and Desktop environments).

---

## 📑 Repository Structure & Navigation

### 1. Installation Guides (`docs/install/`)
* [01 - UEFI BTRFS & Snapper Installation](docs/install/01-uefi-btrfs-snapper.md): Complete bare-metal installation guide featuring BTRFS subvolumes, Snapper automatic snapshots, and GRUB snapshot rollback integration.
* [02 - UEFI LVM & EXT4 Installation](docs/install/02-uefi-lvm-ext4.md): Standard installation workflow using Logical Volume Management (LVM2) on EXT4.

### 2. Post-Installation Guides (`docs/post-install/`)
* [01 - System Performance & Tuning](docs/post-install/01-system-tuning.md): Systemd timeout tuning, mkinitcpio ZSTD compression, automatic pacman cache cleaning, `/boot` backup hooks, and sleep/hibernate configuration.
* [02 - Security, PAM & SSH](docs/post-install/02-security-pam.md): Fingerprint reader (`fprintd`) PAM integration, systemd user SSH-agent socket management, and SSH daemon hardening.
* [03 - LLM Infrastructure & Frameworks](docs/post-install/03-llm-infrastructure.md): Hardware-accelerated local LLMs with Ollama on AMD Radeon dGPU (Desktop RX 9070 XT) and APU (Laptop Framework 13 780M), and ecosystem overview (Unsloth, llama.cpp, vLLM).
* [04 - PipeWire Audio Infrastructure](docs/post-install/04-audio-pipewire.md): Low-latency PipeWire and WirePlumber setup with high-resolution Bluetooth codecs.
* [05 - KDE Plasma Desktop](docs/post-install/05-desktop-kde.md): Plasma 6 configuration, Discover PackageKit/Flatpak backends, Bluetooth battery percentage reporting, and root theme sync.
* [06 - Shells & Terminal Environment](docs/post-install/06-shells.md): Zsh, Fish shell (Starship cross-shell prompt), Node/PNPM development toolchains, and typography.
* [07 - Boot Theming (Plymouth & GRUB)](docs/post-install/07-boot-theming.md): Plymouth boot splash screens, custom GRUB visual themes, and startup melody tunes.
* [08 - Troubleshooting & System Diagnostics](docs/post-install/08-troubleshooting-diagnostics.md): Pacman `.pacnew` merging (`pacdiff`), conflicting untracked files resolution, application coredumps (`coredumpctl`), and kernel freeze logs.

### 3. Integrated Sub-Projects & Automation
* [Power Saver Tuner (`power-saver-tuner/`)](power-saver-tuner/README.md): Event-driven Python daemon for dynamic power/frequency scaling on AMD CPUs and Radeon GPUs (profiles for Desktop and Laptop).
* [BorgBackup Automation (`borg-backup/`)](borg-backup/README.md): Ultra-fast native Borg push backup workflow over SSH from Arch Linux to a centralized storage server.

### 4. Configuration Templates & Dotfiles (`configs/`)
* `configs/dotfiles/`: Home dotfiles (`.zshrc`, `.bashrc`, `.gitconfig`), `~/.config` templates (`kdeglobals`, `neofetch`), and shell configurations (`starship.toml`, `config.fish`).
* `configs/llm/`: Ollama environment configuration files and systemd service overrides (Desktop dGPU, Laptop APU iGPU, and CPU fallback).
* `configs/boot/`: Bootloader assets and GRUB visual themes.
* `configs/kde/`: KDE Plasma system monitor pages and system settings backups.
* `configs/icons/`: System icons and graphic assets.

---

## 🛠️ Key Technologies & References

- **Base Distribution**: [Arch Linux](https://archlinux.org/) (Rolling Release)
- **Official Installation Guide**: [ArchWiki: Installation Guide](https://wiki.archlinux.org/title/Installation_guide)
- **Filesystem**: BTRFS with transparent ZSTD compression (`compress=zstd`)
- **Snapshot Engine**: Snapper + `snap-pac` + `grub-btrfs`
- **Audio Stack**: PipeWire + WirePlumber
- **Desktop Environment**: KDE Plasma (Wayland)
