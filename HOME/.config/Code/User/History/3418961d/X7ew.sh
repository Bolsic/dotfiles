#!/bin/bash

# Prompt for device name
device=$(echo -e "basic\nmici" | dmenu -p "Connect to Bluetooth device:")

# Define device MAC addresses
basic_mac="74:2A:8A:83:55:92"  # Replace with your 'basic' device MAC address
mici_mac="84:D3:52:FD:02:FE"   # Replace with your 'mici' device MAC address

# Connect to the selected device
case "$device" in
    basic)
        bluetoothctl connect "$basic_mac"
        ;;
    mici)
        bluetoothctl connect "$mici_mac"
        ;;
    *)
        notify-send "Bluetooth Connection" "Unknown device: $device"
        ;;
esac
