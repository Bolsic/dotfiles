#!/bin/bash

layout=$(setxkbmap -query | grep variant| awk -F': *' '{print $2}')

case "$layout" in
    ,latinyz)
        setxkbmap -layout us,rs -variant ,yz -option grp:alt_shift_toggle
        ;;
    ,yz)
        setxkbmap -layout us,rs -variant ,latinyz -option grp:alt_shift_toggle
        ;;
    *)
        notify-send "Unknown Keyboard Language Combination is running"
        ;;
esac