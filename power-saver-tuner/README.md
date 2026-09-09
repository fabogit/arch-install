# Power Saver Tuner

> [!NOTE]
> **Choice of Language (Python Rationale)**:
> The daemon is written in Python to maximize ease of maintenance and on-the-fly customization without external dependencies. Because it is strictly event-driven (sleeping while waiting for DBus events), its CPU footprint is virtually zero (~0.00%) and RAM usage is negligible (~7MB), making Go/Rust compilation optimizations unnecessary.

This directory contains the daemon scripts, Systemd services, and configuration files created and optimized for advanced AMD CPU and GPU power management tuning.

The daemon features **Dynamic Hardware Autotuning (Zero-Config)**: when no `/etc/power-saver-tuner.conf` exists, it queries ACPI CPPC firmware interfaces and `sysfs` to automatically tune clock limits and governor states for the detected silicon. When a configuration file is present, user-defined values override the autotuning defaults.

## 📁 Files & Presets

* `power-saver-tuner.py`: The unified daemon script supporting both static configs and zero-config dynamic autotuning.
* `power-saver-tuner.service`: The standard Systemd service registered in `/etc/systemd/system/`.

### 🖥️ Desktop (Garuda)
Optimized for desktop PCs with discrete AMD Radeon GPUs (Navi 48 / RX 9070):
* `desktop/power-saver-tuner.conf`: Frequency configuration installed in `/etc/`.
* `desktop/power-saver-tuner.service`: Desktop service definition.

### 💻 Laptop (Framework 13 Arch)
Optimized for mobile platforms with an AMD Ryzen 7 7840U APU (Phoenix) and Radeon 780M graphics:
* `laptop/power-saver-tuner.conf`: Laptop-specific configuration capping Balanced at 2.5 GHz and Power Saver at 1.1 GHz.
* `laptop/power-saver-tuner.service`: Laptop service definition.

### 🔲 Mini PC / Zero-Config AMD APU (e.g. Minisforum UM690)
Requires **no configuration file** (`/etc/power-saver-tuner.conf` is omitted). The daemon automatically discovers:
* Base nominal frequency via `/sys/devices/system/cpu/cpu*/acpi_cppc/nominal_freq` (3.30 GHz on Ryzen 9 6900HX).
* Lowest non-linear frequency via `amd_pstate_lowest_nonlinear_freq` (1.10 GHz).
* Governor alignment ensuring `powersave` is active under `amd-pstate-epp` to enable dynamic EPP hints.

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

### 🔲 Mini PC Configuration (Minisforum UM690 - Zero-Config Autotuning)

| Parameter / Metric | 🔋 Power Saver | ⚖️ Balanced | 🚀 Performance |
| :--- | :--- | :--- | :--- |
| **CPU Scaling Driver** | `amd-pstate-epp` | `amd-pstate-epp` | `amd-pstate-epp` |
| **CPU Scaling Governor** | `powersave` (Enables EPP) | `powersave` (Enables EPP) | `performance` (Unrestricted) |
| **CPU EPP Profile** | `power` (Max energy savings) | `balance_performance` | `performance` (Max power) |
| **CPU Max Frequency** | **1.10 GHz** (Lowest non-linear) | **3.30 GHz** (CPPC nominal base) | **4.94 GHz** (Hardware boost) |
| **CPU Min Frequency** | **416 MHz** (Hardware minimum) | **416 MHz** (Hardware minimum) | **416 MHz** (Hardware minimum) |
| **CPU Core Boost** | Disabled | Disabled | Enabled |
| **CPU Power (Est.)** | **~5W - 8W** (Silent idle/background) | **~15W - 25W** (Efficiency sweet-spot) | **45W - 54W+** (Full APU TDP) |
| **CPU Perf. (Est.)** | ~40% (Basic desktop tasks) | ~85% (Snappy daily computing) | 100% (Maximum multi-core boost) |
| **AMDGPU DPM Level** | **low** (Minimum clocks) | **auto** (Driver dynamic scaling) | **auto** (Driver dynamic scaling) |
| **GPU Clock (Est.)** | Locked at minimum state | Dynamic up to **2.40 GHz** | Dynamic up to **2.40 GHz** |

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

### For Mini PC / Generic AMD APU (Zero-Config Autotuning):
```bash
# 1. Restore the daemon script (unified root script)
sudo cp power-saver-tuner.py /usr/local/bin/power-saver-tuner.py
sudo chmod +x /usr/local/bin/power-saver-tuner.py

# 2. Restore the Systemd service file (no .conf required!)
sudo cp power-saver-tuner.service /etc/systemd/system/power-saver-tuner.service

# 3. Enable power-profiles-daemon at boot
sudo systemctl enable power-profiles-daemon.service

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

1. **Initialization & Autotuning**:
   - Parses arguments using `argparse`.
   - Reads configuration from the specified path (default: `/etc/power-saver-tuner.conf`), stripping inline comments and whitespaces.
   - **Zero-Config Fallback**: If no configuration file is found, it automatically activates dynamic autotuning defaults:
     - `power-saver`: CPU frequency set to `auto` (lowest non-linear frequency), boost disabled, GPU level set to `low`.
     - `balanced`: CPU frequency set to `auto` (ACPI CPPC nominal base clock), boost disabled, GPU level set to `auto`.
     - `performance`: CPU frequency unrestricted (`none`), boost enabled, GPU level set to `auto`.
   - Queries `org.freedesktop.UPower.PowerProfiles` via `busctl` to obtain the initial active power profile.
   - If found, applies initial hardware limits. If not, restores hardware defaults.

2. **D-Bus Monitoring & Hot-Reloading**:
   - Spawns `gdbus monitor --system ...` as a subprocess.
   - Parses the stdout stream line-by-line.
   - Extracts changes targeting `ActiveProfile` using a precise regex match: `'ActiveProfile': <'([^']+)'\>`.
   - On change, re-loads `/etc/power-saver-tuner.conf` from disk (enabling **native hot-reloading** without restarting the service) and applies CPU limits core-by-core and GPU limits card-by-card.

3. **Hardware Tuning Logic**:
   - **Governor Alignment**: If the active driver is `amd-pstate-epp`, it sets `scaling_governor=powersave` for `power-saver` and `balanced` profiles. This prevents the hardware from locking EPP registers to `performance`, allowing dynamic CPPC hints to scale up to the capped frequency.
   - **Frequency Resolution**: The parameter `limit_freq_<profile>` accepts:
     - `auto`: Lowest non-linear frequency for `power-saver`; ACPI CPPC nominal base frequency for `balanced`.
     - `base`: Resolves directly to `/sys/devices/system/cpu/cpu*/acpi_cppc/nominal_freq`.
     - `ratio:<float>`: Dynamically sets limit to a ratio of `cpuinfo_max_freq` (e.g. `ratio:0.70`).
     - `min`: Locks to `cpuinfo_min_freq`.
     - `none`: Unrestricted hardware maximum.
     - `<integer>`: Exact frequency in kHz (e.g. `2500000`).

4. **Resilience & Reconnection**:
   - If the `gdbus` monitor process crashes or disconnects (e.g. D-Bus restarts), the daemon cleans up the process, restores defaults, and attempts to spawn a new monitor after a 5-second backoff.

5. **Shutdown Cleanup**:
   - Intercepts `SIGTERM` and `SIGINT` signals.
   - Terminates monitor processes cleanly, waits to prevent zombie process accumulation, restores all hardware settings to defaults, and exits.

---

## 💡 Choice of Language (Python Rationale)

The daemon is written in Python rather than compiled languages like Go or Rust for the following reasons:
* **Event-Driven & CPU Efficient**: The daemon monitors DBus events (`gdbus monitor`) and stays idle in the background 99.99% of the time, consuming ~0.00% CPU.
* **Low Footprint**: It occupies only ~7MB of RAM, making compilation optimizations for memory savings (<1MB in Rust) practically negligible.
* **Zero External Dependencies**: By invoking native system tools (`gdbus`), it relies purely on the Python standard library, avoiding fragile third-party DBus bindings.
* **Easy Maintenance**: Since it is interpreted, it allows for quick configuration edits or code tweaks directly on the target machine without needing toolchains (compilers, build steps).

