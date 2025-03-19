#!/bin/bash

# Prompt for device name
device=$(echo -e "basic\nmici\nmali-zvucnik" | dmenu -p "Connect to Bluetooth device:")

# Define device MAC addresses
basic_mac="74:2A:8A:83:55:92"
mici_mac="84:D3:52:FD:02:FE"
mali_zvucnik="16:CD:FF:B0:48:D9"

# Connect to the selected device
case "$device" in
basic)
    bluetoothctl connect "$basic_mac"
    ;;
mici)
    bluetoothctl connect "$mici_mac"
    ;;
mali-zvucnik)
    bluetoothctl connect "$mali_zvucnik"
    ;;
*)
    notify-send "Bluetooth Connection" "Unknown device: $device"
    ;;
esac
