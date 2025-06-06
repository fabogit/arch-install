if status is-interactive
  # Commands to run in interactive sessions can go here
end

# load starship
starship init fish | source

# pnpm
set -gx PNPM_HOME "/home/fabo/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end
