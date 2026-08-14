# Troubleshooting, Diagnostics & Maintenance

This guide details systematic diagnostic procedures, crash and freeze investigations, Pacman conflict resolutions, and `.pacnew` configuration file management.

---

## 1. Pacman Maintenance & File Conflict Resolution

### 1.1 Managing `.pacnew` Configuration Merges
When upstream packages update system configuration files in `/etc/`, Pacman creates `.pacnew` files to avoid overwriting local changes.

Install `pacman-contrib` and a graphical/CLI diff tool:
```bash
sudo pacman -S pacman-contrib meld
```

Run `pacdiff` to review and merge differences:
```bash
DIFFPROG=meld sudo -E pacdiff
```

#### Merge Decision Matrix:
| Option | Action | Architectural Implication |
| :--- | :--- | :--- |
| **`v` (View)** | Inspect diff | Review differences line-by-line before modifying. |
| **`m` (Merge)** | Open diff tool | Merge upstream changes with local configuration. |
| **`o` (Overwrite)** | Replace original | Replaces local file with upstream `.pacnew` (use when no local edits exist). |
| **`d` (Delete)** | Delete `.pacnew` | Discards upstream changes, keeping local configuration. |
| **`q` (Quit)** | Abort | Leaves files untouched for subsequent inspection. |

> [!CAUTION]
> Never blindly delete `.pacnew` files without checking. Critical packages (e.g., `tpm2-tss`, `shadow`, `sudo`, `mkinitcpio`) often introduce security fixes or syntax updates essential for system boot and authentication.

---

### 1.2 Resolving `failed to commit transaction (conflicting files)`
This error occurs when Pacman attempts to install files that already exist on disk without being tracked in the local package database (e.g., dynamically generated Python bytecode `__pycache__` or manual file copies).

#### Step 1: Check File Ownership
Verify whether the conflicting file is owned by any package:
```bash
pacman -Qo /path/to/conflicting_file
```

#### Step 2: Safe Resolution
- **If unowned (e.g., Python `__pycache__` bytecode or stale build files)**: Safely remove the untracked file or folder:
```bash
sudo rm -rf /usr/share/gcc-*/python/libstdcxx/**/__pycache__
```

- **If required, use targeted selective overwrite** (never use global `--overwrite '*'`):
```bash
sudo pacman -Syu --overwrite '/usr/share/gcc-*/*'
```

> [!WARNING]
> **Anti-Pattern:** Running `pacman -Syu --overwrite '*'` disables package manager safety boundaries across the entire system and can conceal corrupted package installations. `[TECHNICAL DEBT / HIGH RISK]`

---

## 2. System Crash & Freeze Diagnostics

### 2.1 Analyzing System Coredumps (`coredumpctl`)
Systemd automatically captures memory state and backtraces when user-space applications or system daemons crash.

List recent application crashes:
```bash
coredumpctl list
```

Inspect crash metadata and stack trace for a specific process or PID:
```bash
coredumpctl info <PID_OR_EXECUTABLE>
```

Launch GDB directly on the captured core dump to inspect backtraces:
```bash
coredumpctl gdb <PID_OR_EXECUTABLE>
# Inside GDB:
(gdb) bt full
(gdb) quit
```

---

### 2.2 Investigating System Freezes & Kernel Panics
When diagnosing hardware freezes, GPU driver lockups, or unexpected reboots:

#### Check Logs from the Previous Boot
Inspect journal logs from the boot session immediately preceding the crash:
```bash
journalctl -b -1 -p 3 -xb
```

#### Monitor Live Hardware / Driver Errors
Filter system journal for errors from the current boot:
```bash
# Filter by priority (Emergency, Alert, Critical, Error)
journalctl -b 0 -p 3

# Check kernel ring buffer for DRM/GPU and APU messages
dmesg -T --level=err,warn
```
