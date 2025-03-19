#! /bin/sh

# Load hekboard bindings
#xmodmap ~/.Xmodmap

# Set the keyboard languages
#setxkbmap -layout us,rs -variant ,latinyz -option grp:alt_shift_toggle

# Start the Simple XHotkey Deamon
#sxhkd & 

# Start bspwm (this command should be the last line of the file)
exec bspwm
