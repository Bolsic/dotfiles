#!/bin/bash
# shellcheck disable=SC2068

function run {
  if ! pgrep -x $1 ;
  then
     $@&
  fi
}

# Start sxhkd
# run sxhkd -c $HOME/.config/sxhkd/sxhkdrc 

# Set keyboard layout
run setxkbmap -layout us,rs -variant ,latinyz -option grp:alt_shift_toggle

# Set keyboard bindings
run xmodmap ~/.Xmodmap

# Start hotkey daemon
run sxhkd -t 1 -c "$HOME/.config/sxhkd/sxhkdrc"

# Run picom
run picom &

# Start polybar
run polybar mybar

# Start wallapper
run feh --bg-max ~/Media/Wallpapers/wallpaper-purple-forest.jpeg

# Flameshot
flameshot &

# Init Keyring
eval "$(gnome-keyring-deamon --start)"
export SSH_AUTH_SOCK
