# Shells & Terminal Environment Setup

This guide details configuration for **Zsh**, **Fish** shell (both using the modern **Starship** cross-shell prompt), and standard **Bash** configurations.

All corresponding dotfile templates are stored in [`configs/dotfiles/`](../../configs/dotfiles).

---

## 1. Zsh Setup with Starship Prompt

### 1.1 Install Zsh and Dependencies
```bash
sudo pacman -S zsh zsh-completions starship git
```

### 1.2 Install Oh My Zsh & Plugins
```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Autosuggestions
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# Syntax Highlighting
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

### 1.3 Apply Configuration
Copy `.zshrc` and `starship.toml`:
```bash
cp configs/dotfiles/home/.zshrc ~/.zshrc
mkdir -p ~/.config
cp configs/dotfiles/shells/starship.toml ~/.config/starship.toml
```

---

## 2. Fish Shell & Starship Prompt

### 2.1 Install Fish and Starship
```bash
sudo pacman -S fish starship
```

### 2.2 Configure Fish & Starship
```bash
mkdir -p ~/.config/fish
cp configs/dotfiles/shells/config.fish ~/.config/fish/config.fish
cp configs/dotfiles/shells/starship.toml ~/.config/starship.toml
```


---

## 3. Bash Shell & Starship Setup

### 3.1 Install Bash Completions & Starship
```bash
sudo pacman -S bash-completion starship
```

### 3.2 Apply Configuration
Copy the provided `.bashrc` from `configs/dotfiles/home/`:
```bash
cp configs/dotfiles/home/.bashrc ~/.bashrc
```

---

## 4. Development Toolchains: `fnm`, `corepack` & `pnpm` Integration

### 4.1 Install `fnm` & `direnv`
```bash
sudo pacman -S direnv
yay -S fnm-bin
```

### 4.2 Shell Configuration

#### For Fish (`~/.config/fish/config.fish`):
```fish
# PNPM Home Directory
set -gx PNPM_HOME "$HOME/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
    set -gx PATH $PNPM_HOME $PATH
end

# Fast Node Manager (fnm) with Corepack support
if type -q fnm
    fnm env --use-on-cd --corepack-enabled --shell fish | source
end

# Direnv environment hook
if type -q direnv
    direnv hook fish | source
end
```

#### For Zsh (`~/.zshrc`):
```bash
# PNPM Home Directory
export PNPM_HOME="$HOME/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac

# Fast Node Manager (fnm) with Corepack support
if command -v fnm &> /dev/null; then
    eval "$(fnm env --use-on-cd --corepack-enabled)"
fi

# Direnv environment hook
if command -v direnv &> /dev/null; then
    eval "$(direnv hook zsh)"
fi
```

#### For Bash (`~/.bashrc`):
```bash
# PNPM Home Directory
export PNPM_HOME="$HOME/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac

# Fast Node Manager (fnm) with Corepack support
if command -v fnm &> /dev/null; then
    eval "$(fnm env --use-on-cd --corepack-enabled)"
fi

# Direnv environment hook
if command -v direnv &> /dev/null; then
    eval "$(direnv hook bash)"
fi

# Starship prompt hook
if command -v starship &> /dev/null; then
    eval "$(starship init bash)"
fi
```


---

## 5. IDE Environment & Terminal Resolution (VS Code & Antigravity)

When launching **VS Code** or **Antigravity IDE** from the desktop launcher, the IDE spawns a login shell to discover the environment (`$PATH`). 

To ensure `node`, `npm`, and `pnpm` are seamlessly resolved by both integrated terminals and language server extensions:

### 5.1 IDE User Settings (`settings.json`)
Add to `~/.config/Code/User/settings.json` or `~/.config/Antigravity/User/settings.json`:

```json
{
  "terminal.integrated.defaultProfile.linux": "fish",
  "terminal.integrated.inheritEnv": true,
  "terminal.integrated.profiles.linux": {
    "fish": {
      "path": "/usr/bin/fish",
      "args": ["-l"]
    },
    "zsh": {
      "path": "/usr/bin/zsh",
      "args": ["-l"]
    },
    "bash": {
      "path": "/usr/bin/bash",
      "args": ["-l"]
    }
  }
}
```

### 5.2 Login Shell Fallback (`~/.bash_profile`)
If `/bin/bash` is still the system default login shell in `/etc/passwd`, ensure `fnm` is loaded in `~/.bash_profile` so the IDE's environment resolver exports it to all GUI worker processes:

```bash
# ~/.bash_profile
export PNPM_HOME="$HOME/.local/share/pnpm"
export PATH="$PNPM_HOME:$PATH"

if command -v fnm &> /dev/null; then
    eval "$(fnm env --use-on-cd --corepack-enabled)"
fi

[[ -f ~/.bashrc ]] && . ~/.bashrc
```

---

## 6. Recommended Typography & Fonts

### 6.1 Terminal & Coding Fonts (Nerd Fonts)
Nerd Fonts are required for Starship symbols, Git branch glyphs, and modern terminal file trees:

```bash
# Recommended coding font packages
sudo pacman -S ttf-firacode-nerd ttf-jetbrains-mono-nerd ttf-cascadia-code-nerd

# Meslo Nerd Font (AUR)
yay -S ttf-meslo-nerd-font-powerlevel10k
```

### 6.2 System, UI & International Fonts
```bash
# High-quality UI, serif, sans, and international fonts
sudo pacman -S noto-fonts noto-fonts-emoji noto-fonts-extra cantarell-fonts ttf-ubuntu-font-family

# Comprehensive Google Fonts library (optional, from AUR)
yay -S ttf-google-fonts-git
```

### 6.3 User Font Directory & Font Cache
To install custom `.ttf` or `.otf` fonts manually:
```bash
mkdir -p ~/.local/share/fonts
cp /path/to/custom/fonts/* ~/.local/share/fonts/

# Rebuild font cache
fc-cache -fv
```

---

## 7. Set Default Shell

Change login shell for the user:
```bash
# For Fish:
chsh -s $(which fish)

# For Zsh:
chsh -s $(which zsh)

# For Bash:
chsh -s $(which bash)
```



