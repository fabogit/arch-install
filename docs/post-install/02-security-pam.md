# Security, PAM & Authentication Setup

This guide details the configuration of biometric authentication (Fingerprint reader), systemd user-level SSH agent sockets, and SSH daemon security hardening.

---

## 1. Fingerprint Authentication (`fprintd`)

### 1.1 Install `fprintd`
```bash
sudo pacman -S fprintd
```

### 1.2 Enroll Fingerprint
Enroll your index finger for the current user:
```bash
fprintd-enroll "$USER"
```
Verify enrolled fingerprint:
```bash
fprintd-verify "$USER"
```

### 1.3 Configure PAM for Fingerprint Auth

#### Sudo Authentication (`/etc/pam.d/sudo`)
Add `pam_fprintd.so` as sufficient at the top of `/etc/pam.d/sudo`:
```text
#%PAM-1.0
auth        sufficient  pam_fprintd.so
auth        include     system-auth
account     include     system-auth
session     include     system-auth
```

#### System Login Authentication (`/etc/pam.d/system-auth`)
Insert `pam_fprintd.so` before standard unix authentication:
```text
auth        sufficient  pam_fprintd.so
auth        required    pam_env.so
auth        sufficient  pam_unix.so try_first_pass nullok
auth        required    pam_deny.so
```

---

## 2. SSH Agent Setup via Systemd User Socket

Run a single persistent `ssh-agent` per user session managed cleanly by systemd.

### 2.1 Enable User Systemd Socket
```bash
systemctl --user enable --now ssh-agent.socket
```

### 2.2 Export `SSH_AUTH_SOCK` to GUI Applications
Create `~/.config/environment.d/ssh-agent.conf`:
```ini
SSH_AUTH_SOCK="${XDG_RUNTIME_DIR}/ssh-agent.socket"
```

### 2.3 Shell Integration

#### For Zsh (`~/.zshrc`):
```bash
export SSH_AUTH_SOCK="${XDG_RUNTIME_DIR}/ssh-agent.socket"
```

#### For Fish (`~/.config/fish/conf.d/ssh_agent.fish`):
```fish
if test -z "$SSH_AUTH_SOCK"
    set -gx SSH_AUTH_SOCK "$XDG_RUNTIME_DIR/ssh-agent.socket"
end
```

---

## 3. SSH Daemon Hardening

Ensure SSH server is securely configured in `/etc/ssh/sshd_config.d/10-security.conf`:
```text
PermitRootLogin no
PasswordAuthentication yes
X11Forwarding no
MaxAuthTries 3
```

Restart SSH daemon:
```bash
sudo systemctl restart sshd.service
```
