if status is-interactive
  # Commands to run in interactive sessions can go here
end

# Starship prompt
if type -q starship
    starship init fish | source
end

# PNPM
set -gx PNPM_HOME "$HOME/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
    set -gx PATH $PNPM_HOME $PATH
end

# Fast Node Manager (fnm) with Corepack support
if type -q fnm
    fnm env --use-on-cd --corepack-enabled --shell fish | source
end

# Direnv hook
if type -q direnv
    direnv hook fish | source
end
