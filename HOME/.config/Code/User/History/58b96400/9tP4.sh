#!/bin/bash

function run {
  if ! pgrep $1 ;
  then
    $@&
  fi
}

# Start sxhkd
run sxhkd -c $HOME/.config/bspwm/sxhkd/sxhkdrc &

# Set keyboard layout
run setxkbmap -layout us,rs -variant ,latinyz -option grp:alt_shift_toggle

# Set keyboard bindings
run test -f ~/.Xmodmap; and xmodmap ~/.Xmodmap

# Start hotkey daemon
run sxhkd -c $HOME/.config/bspwm/sxhkd/sxhkdrc

# Run picom
run picom --experimental-backend &

# Start polybar
run polybar example &

