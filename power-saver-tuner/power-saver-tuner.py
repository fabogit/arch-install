#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import signal
import glob
import time
import argparse

# Default paths
CONF_PATH = "/etc/power-saver-tuner.conf"
BOOST_PATH = "/sys/devices/system/cpu/cpufreq/boost"

def log(msg):
    print(f"[power-saver-tuner] {msg}", flush=True)

def load_config(config_path):
    # Set default values for all profiles
    config = {
        "disable_boost_power_saver": "no",
        "disable_boost_balanced": "no",
        "disable_boost_performance": "no",
        
        "limit_freq_power_saver": "auto",
        "limit_freq_balanced": "none",
        "limit_freq_performance": "none",
        
        "gpu_perf_level_power_saver": "none",
        "gpu_perf_level_balanced": "none",
        "gpu_perf_level_performance": "none",
        
        "gpu_sclk_limit_power_saver": "none",
        "gpu_sclk_limit_balanced": "none",
        "gpu_sclk_limit_performance": "none",
        
        "gpu_mclk_limit_power_saver": "none",
        "gpu_mclk_limit_balanced": "none",
        "gpu_mclk_limit_performance": "none",

        "gpu_device_filter": "all"
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                for line in f:
                    # Strip inline comments before processing
                    if "#" in line:
                        line = line.split("#", 1)[0]
                    line = line.strip()
                    if not line:
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip().lower()
                        v = v.strip().strip('"').strip("'")
                        if k in config:
                            config[k] = v
        except Exception as e:
            log(f"Error reading config {config_path}: {e}")
    return config

def write_file(path, value):
    try:
        with open(path, "w") as f:
            f.write(str(value) + "\n")
        return True
    except Exception as e:
        log(f"Error writing {value} to {path}: {e}")
    return False

def get_cpu_dirs():
    return sorted(glob.glob("/sys/devices/system/cpu/cpu[0-9]*/cpufreq"))

def get_lowest_nonlinear_freq(cpu_dir):
    path = os.path.join(cpu_dir, "amd_pstate_lowest_nonlinear_freq")
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except Exception:
        pass
    return None

def get_min_freq(cpu_dir):
    path = os.path.join(cpu_dir, "cpuinfo_min_freq")
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except Exception:
        pass
    return 560000

def get_max_freq(cpu_dir):
    path = os.path.join(cpu_dir, "cpuinfo_max_freq")
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except Exception:
        pass
    return None

def set_cpu_boost(enabled):
    # Keep global boost path enabled at 1 to prevent systemd/power-profiles-daemon 
    # from failing with write errors (EINVAL) when changing profiles.
    if os.path.exists(BOOST_PATH):
        write_file(BOOST_PATH, 1)

    # Disable/enable boost at the individual CPU policy level
    cpu_dirs = get_cpu_dirs()
    count = 0
    for cpu_dir in cpu_dirs:
        policy_boost_path = os.path.join(cpu_dir, "boost")
        if write_file(policy_boost_path, 1 if enabled else 0):
            count += 1
        
    log(f"Boost {'enabled' if enabled else 'disabled'} on {count} CPU policies.")

def apply_profile_settings(profile, config_path):
    config = load_config(config_path)
    log(f"Applying settings for profile: {profile}...")
    conf_profile_name = profile.replace("-", "_")

    # 1. Handle CPU Boost per profile
    boost_key = f"disable_boost_{conf_profile_name}"
    disable_boost_val = config.get(boost_key, "no").lower() in ("yes", "true", "1")
    set_cpu_boost(not disable_boost_val)

    # 2. CPU Frequency Limit (Applied dynamically per core)
    limit_key = f"limit_freq_{conf_profile_name}"
    limit_val = config.get(limit_key, "none")
    
    cpu_dirs = get_cpu_dirs()
    count = 0
    for cpu_dir in cpu_dirs:
        max_freq_path = os.path.join(cpu_dir, "scaling_max_freq")
        target_freq = None
        
        if limit_val == "auto":
            target_freq = get_lowest_nonlinear_freq(cpu_dir)
            if target_freq is None:
                max_f = get_max_freq(cpu_dir)
                if max_f:
                    target_freq = max_f // 2
            if target_freq is None:
                target_freq = 1500000
        elif limit_val == "min":
            target_freq = get_min_freq(cpu_dir)
        elif limit_val == "none":
            target_freq = get_max_freq(cpu_dir)
        else:
            try:
                target_freq = int(limit_val)
            except ValueError:
                log(f"Invalid {limit_key} in config: {limit_val}. Using hardware max.")
                target_freq = get_max_freq(cpu_dir)

        if target_freq is not None:
            if write_file(max_freq_path, target_freq):
                count += 1
                    
    log(f"Configured CPU scaling_max_freq on {count} CPUs (Limit mode: {limit_val}).")

    # 3. GPU Performance Level & State Settings
    gpu_perf_key = f"gpu_perf_level_{conf_profile_name}"
    gpu_perf_val = config.get(gpu_perf_key, "none")
    
    sclk_key = f"gpu_sclk_limit_{conf_profile_name}"
    mclk_key = f"gpu_mclk_limit_{conf_profile_name}"
    sclk_limit = config.get(sclk_key, "none")
    mclk_limit = config.get(mclk_key, "none")
    gpu_filter = config.get("gpu_device_filter", "all").lower()

    card_dirs = [d for d in glob.glob("/sys/class/drm/card*/device") if "-" not in os.path.basename(os.path.dirname(d))]
    for card_dir in card_dirs:
        card_name = os.path.basename(os.path.dirname(card_dir))
        
        # Apply GPU device filtering
        if gpu_filter != "all" and gpu_filter not in card_name:
            log(f"Skipping GPU settings for {card_name} (filtered out by config)")
            continue

        perf_level_path = os.path.join(card_dir, "power_dpm_force_performance_level")
        sclk_path = os.path.join(card_dir, "pp_dpm_sclk")
        mclk_path = os.path.join(card_dir, "pp_dpm_mclk")

        # 3a. Set general DPM performance level if specified
        if gpu_perf_val != "none":
            write_file(perf_level_path, gpu_perf_val)
            log(f"Set GPU performance level to '{gpu_perf_val}' for {card_name}")

        # 3b. Apply clock state overrides if we are in manual mode (requires overdrive enabled)
        if sclk_limit != "none" or mclk_limit != "none":
            write_file(perf_level_path, "manual")
            if sclk_limit != "none":
                write_file(sclk_path, sclk_limit)
                log(f"Limited GPU core clock states to '{sclk_limit}' for {card_name}")
            if mclk_limit != "none":
                write_file(mclk_path, mclk_limit)
                log(f"Limited GPU memory clock states to '{mclk_limit}' for {card_name}")

def restore_all_defaults(config_path):
    log("Restoring all hardware settings to defaults...")
    config = load_config(config_path)
    gpu_filter = config.get("gpu_device_filter", "all").lower()

    # Enable CPU boost globally and individually
    if os.path.exists(BOOST_PATH):
        write_file(BOOST_PATH, 1)
        
    cpu_dirs = get_cpu_dirs()
    for cpu_dir in cpu_dirs:
        max_freq_path = os.path.join(cpu_dir, "scaling_max_freq")
        policy_boost_path = os.path.join(cpu_dir, "boost")
        
        write_file(policy_boost_path, 1)
        max_val = get_max_freq(cpu_dir)
        if max_val is not None:
            write_file(max_freq_path, max_val)

    # Restore GPU settings
    card_dirs = [d for d in glob.glob("/sys/class/drm/card*/device") if "-" not in os.path.basename(os.path.dirname(d))]
    for card_dir in card_dirs:
        card_name = os.path.basename(os.path.dirname(card_dir))
        if gpu_filter != "all" and gpu_filter not in card_name:
            continue
        perf_level_path = os.path.join(card_dir, "power_dpm_force_performance_level")
        write_file(perf_level_path, "auto")

def get_current_profile():
    try:
        res = subprocess.run(
            ["busctl", "get-property", "org.freedesktop.UPower.PowerProfiles",
             "/org/freedesktop/UPower/PowerProfiles", "org.freedesktop.UPower.PowerProfiles", "ActiveProfile"],
            capture_output=True, text=True, check=True
        )
        match = re.search(r'"([^"]+)"', res.stdout)
        if match:
            return match.group(1)
    except Exception as e:
        log(f"Error querying active profile: {e}")
    return None

def run_daemon(config_path):
    log("Starting power-saver-tuner in daemon mode...")
    
    # Initial trigger
    profile = get_current_profile()
    log(f"Current profile on start: {profile}")
    if profile:
        apply_profile_settings(profile, config_path)
    else:
        restore_all_defaults(config_path)

    cmd = [
        "gdbus", "monitor", "--system",
        "--dest", "org.freedesktop.UPower.PowerProfiles",
        "--object-path", "/org/freedesktop/UPower/PowerProfiles"
    ]

    def cleanup(signum, frame):
        log("Stopping and restoring defaults...")
        restore_all_defaults(config_path)
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    # Subprocess execution loop with automatic reconnection
    while True:
        try:
            log("Spawning gdbus monitor process...")
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                if "PropertiesChanged" in line and "ActiveProfile" in line:
                    # Precise regex to match ActiveProfile property
                    match = re.search(r"'ActiveProfile':\s*<'([^']+)'\>", line)
                    if match:
                        new_profile = match.group(1)
                        apply_profile_settings(new_profile, config_path)
            
            stderr_out = proc.stderr.read().strip()
            log(f"gdbus monitor disconnected. Exit code: {proc.poll()}. Error: {stderr_out}")
            proc.terminate()
            proc.wait()
        except Exception as e:
            log(f"Monitor connection error: {e}")

        log("DBus channel lost. Restoring defaults and retrying monitor in 5 seconds...")
        restore_all_defaults(config_path)
        time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Power Saver Tuner for AMD systems")
    parser.add_argument("--config", default=CONF_PATH, help="Path to config file")
    parser.add_argument("--apply", help="Apply profile settings once (power-saver, balanced, performance) and exit")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode monitoring DBus (default)")
    
    args = parser.parse_args()

    if args.apply:
        apply_profile_settings(args.apply, args.config)
        sys.exit(0)

    run_daemon(args.config)

if __name__ == "__main__":
    main()
