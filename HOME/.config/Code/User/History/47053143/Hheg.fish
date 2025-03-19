if status is-interactive
    # Commands to run in interactive sessions can go here
    set -g fish_greeting ""
end

# Define an alias for dotfiles
alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
