#! /bin/sh

# Load hekboard bindings
#xmodmap ~/.Xmodmap

# Set the keyboard languages
#setxkbmap -layout us,rs -variant ,latinyz -option grp:alt_shift_toggle

# Start the Simple XHotkey Deamon
#sxhkd & 

# Merge X resources so cursor size is read
#[[ -f ~/.Xresources ]] && xrdb -merge ~/.Xresources

# Start bspwm (this command should be the last line of the file)
~/scripts/monitor-detect.sh &

exec bspwm
