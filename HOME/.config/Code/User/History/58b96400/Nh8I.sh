#!/bin/bash

function run {
  if ! pgrep $1 ;
  then
    $@&
  fi
}

# Set keyboard layout
run setxkbmap -layout us,rs -variant ,latinyz -option grp:alt_shift_toggle

# Set keyboard bindings
run test -f ~/.Xmodmap; and xmodmap ~/.Xmodmap

# Start hotkey daemon
run sxhkd -c $HOME/.config/bspwm/sxhkd/sxhkdrc

