# Power Saver Tuner Backup

> [!NOTE]
> **Choice of Language (Python Rationale)**:
> The daemon is written in Python to maximize ease of maintenance and on-the-fly customization without external dependencies. Because it is strictly event-driven (sleeping while waiting for DBus events), its CPU footprint is virtually zero (~0.00%) and RAM usage is negligible (~7MB), making Go/Rust compilation optimizations unnecessary.

This directory contains the backups of all configuration files, daemon scripts, and Systemd services created and optimized for advanced power management tuning.

The files are separated by system:

## 🖥️ Desktop (Garuda)
Files optimized for the desktop PC with a discrete AMD Radeon GPU (Navi 48 / RX 9070):
* `desktop/power-saver-tuner.py`: The main script installed in `/usr/local/bin/`.
* `desktop/power-saver-tuner.conf`: The frequency configuration file installed in `/etc/`.
* `desktop/power-saver-tuner.service`: The Systemd service registered in `/etc/systemd/system/`.

## 💻 Laptop (Framework 13 Arch)
Files optimized for the laptop with an AMD Ryzen 7 7840U APU and integrated Radeon 780M graphics (featuring dynamic profile-specific limits for CPU/GPU on laptops):
* `laptop/power-saver-tuner.py`: The profile-aware main script installed in `/usr/local/bin/`.
* `laptop/power-saver-tuner.conf`: The laptop-specific configuration (capping CPU to 2.5 GHz in Balanced, 1.1 GHz in Power Saver, and GPU to `low`/`auto` DPM levels) installed in `/etc/`.
* `laptop/power-saver-tuner.service`: The Systemd service registered in `/etc/systemd/system/`.

---

## 📊 Profile Behaviors and Configuration Details

Here is the exact breakdown of how the 3 system profiles behave on both machines with our custom tuning applied:

### 🖥️ Desktop Configuration (Garuda)

| Parameter / Metric | 🔋 Power Saver | ⚖️ Balanced | 🚀 Performance |
| :--- | :--- | :--- | :--- |
| **CPU Scaling Driver** | `amd-pstate-epp` | `amd-pstate-epp` | `amd-pstate-epp` |
| **CPU EPP Profile** | `power` (Max energy savings) | `balance_performance` | `performance` (Max power) |
| **CPU Max Frequency** | **1.76 GHz** (Non-linear threshold) | **3.60 GHz** (Base clock limit) | **5.10 GHz** (Unrestricted) |
| **CPU Min Frequency** | **560 MHz** (Hardware minimum) | **560 MHz** (Hardware minimum) | **560 MHz** (Hardware minimum) |
| **CPU Core Boost** | Disabled | Disabled | Enabled |
| **CPU Power (Est.)** | **~5W - 8W** (Light desktop tasks) | **~15W - 25W** (Efficiency sweet-spot) | **65W - 105W+** (TDP package peak) |
| **CPU Perf. (Est.)** | ~45% (Basic office/web) | ~85% (Snappy interface, quiet fans) | 100% (Maximum throughput) |
| **AMDGPU DPM Level** | **low** (Forced to minimum clocks) | **auto** (Driver dynamic scaling) | **auto** (Driver dynamic scaling) |
| **GPU Core Clock** | Locked at **500 MHz** (State 0) | Dynamic up to **2.52 GHz** | Dynamic up to **2.52 GHz** |
| **GPU Memory Clock** | Locked at **96 MHz** (State 0) | Dynamic up to **1.25 GHz** | Dynamic up to **1.25 GHz** |
| **GPU Power (Est.)** | **~15W - 50W** (Down to ~15W when idle, ~48W under 4K/120Hz desktop load) | **~30W - 330W** (Typical load to full 3D) | **~30W - 330W+ (Peak 374W)** (TDP cap peak) |

---

### 💻 Laptop Configuration (Framework 13)

| Parameter / Metric | 🔋 Power Saver | ⚖️ Balanced | 🚀 Performance |
| :--- | :--- | :--- | :--- |
| **CPU Scaling Driver** | `amd-pstate-epp` | `amd-pstate-epp` | `amd-pstate-epp` |
| **CPU EPP Profile** | `power` (Max energy savings) | `balance_performance` | `performance` (Max power) |
| **CPU Max Frequency** | **1.10 GHz** (Non-linear threshold) | **2.50 GHz** (Optimal clock cap) | **5.13 GHz** (Unrestricted) |
| **CPU Min Frequency** | **419 MHz** (Hardware minimum) | **419 MHz** (Hardware minimum) | **419 MHz** (Hardware minimum) |
| **CPU Core Boost** | Disabled | Disabled | Enabled |
| **CPU Power (Est.)** | **~3W - 5W** (Excellent battery life) | **~12W - 15W** (Fast and silent) | **28W - 35W+** (Maximum APU TDP) |
| **CPU Perf. (Est.)** | ~40% (Autonomy focused) | ~85% (Daily productivity) | 100% (Maximum throughput) |
| **AMDGPU DPM Level** | **low** (Forced to minimum clocks) | **auto** (Driver dynamic scaling) | **auto** (Driver dynamic scaling) |
| **GPU Core Clock** | Locked at **800 MHz** (State 0) | Dynamic up to **2.70 GHz** (State 2) | Dynamic up to **2.70 GHz** (State 2) |
| **GPU Memory Clock** | Locked at **1.00 GHz** (State 0) | Dynamic up to **2.80 GHz** (State 1) | Dynamic up to **2.80 GHz** (State 1) |
| **GPU Power (Est.)** | **~2W - 4W** (Minimum power draw) | **~1W - 15W** (Typical to full APU load) | **~1W - 15W** (Typical to full APU load) |

---

## 🛠️ Quick Restore Guide

To restore the files, first open your terminal and navigate to this backup directory:
```bash
cd ~/power-saver-tuner
```

Then, run the appropriate set of commands below depending on which machine you are currently configuring:

### For the Desktop PC (Garuda):
```bash
# 1. Restore the daemon script (unified root script)
sudo cp power-saver-tuner.py /usr/local/bin/power-saver-tuner.py
sudo chmod +x /usr/local/bin/power-saver-tuner.py

# 2. Restore the configuration file
sudo cp desktop/power-saver-tuner.conf /etc/power-saver-tuner.conf

# 3. Restore the Systemd service file
sudo cp desktop/power-saver-tuner.service /etc/systemd/system/power-saver-tuner.service

# 4. Reload Systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable --now power-saver-tuner.service
```

### For the Laptop (Framework 13):
```bash
# 1. Restore the daemon script (unified root script)
sudo cp power-saver-tuner.py /usr/local/bin/power-saver-tuner.py
sudo chmod +x /usr/local/bin/power-saver-tuner.py

# 2. Restore the configuration file
sudo cp laptop/power-saver-tuner.conf /etc/power-saver-tuner.conf

# 3. Restore the Systemd service file
sudo cp laptop/power-saver-tuner.service /etc/systemd/system/power-saver-tuner.service

# 4. Reload Systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable --now power-saver-tuner.service
```

---

## ⚙️ Command-Line Interface (CLI)

The unified script supports command-line parameters for manual testing and direct profile application:
```
usage: power-saver-tuner.py [-h] [--config CONFIG] [--apply APPLY] [--daemon]

Power Saver Tuner for AMD systems

options:
  -h, --help      show this help message and exit
  --config PATH   Path to configuration file (default: /etc/power-saver-tuner.conf)
  --apply PROFILE Apply profile settings once (power-saver, balanced, performance) and exit
  --daemon        Run in daemon mode monitoring DBus (default behavior)
```

Example of manual testing:
```bash
python3 power-saver-tuner.py --config desktop/power-saver-tuner.conf --apply power-saver
```

---

## 🔄 Execution Flow and Architecture

The daemon behaves according to the following control logic:

1. **Initialization**:
   - Parses arguments using `argparse`.
   - Reads configuration from the specified path (default: `/etc/power-saver-tuner.conf`), stripping inline comments and whitespaces.
   - Queries `org.freedesktop.UPower.PowerProfiles` via `busctl` to obtain the initial active power profile.
   - If found, applies initial hardware limits. If not, restores hardware defaults.

2. **D-Bus Monitoring**:
   - Spawns `gdbus monitor --system ...` as a subprocess.
   - Parses the stdout stream line-by-line.
   - Extracts changes targeting `ActiveProfile` using a precise regex match: `'ActiveProfile': <'([^']+)'\>`.
   - On change, re-loads the configuration from disk (enabling hot-reloading) and applies CPU limits core-by-core and GPU limits card-by-card.

3. **Resilience & Reconnection**:
   - If the `gdbus` monitor process crashes or disconnects (e.g. D-Bus restarts), the daemon cleans up the process, restores defaults, and attempts to spawn a new monitor after a 5-second backoff.

4. **Shutdown Cleanup**:
   - Intercepts `SIGTERM` and `SIGINT` signals.
   - Terminates monitor processes cleanly, waits to prevent zombie process accumulation, restores all hardware settings to defaults, and exits.

---

## 💡 Choice of Language (Python Rationale)

The daemon is written in Python rather than compiled languages like Go or Rust for the following reasons:
* **Event-Driven & CPU Efficient**: The daemon monitors DBus events (`gdbus monitor`) and stays idle in the background 99.99% of the time, consuming ~0.00% CPU.
* **Low Footprint**: It occupies only ~7MB of RAM, making compilation optimizations for memory savings (<1MB in Rust) practically negligible.
* **Zero External Dependencies**: By invoking native system tools (`gdbus`), it relies purely on the Python standard library, avoiding fragile third-party DBus bindings.
* **Easy Maintenance**: Since it is interpreted, it allows for quick configuration edits or code tweaks directly on the target machine without needing toolchains (compilers, build steps).

