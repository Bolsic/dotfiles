#!/bin/bash

# Define the names or indices of your audio sinks
SPEAKERS="alsa_output.pci-0000_06_00.6.analog-stereo"
HEADPHONES="bluez_sink.74_2A_8A_83_55_92.a2dp_sinkmodule-bluez5-device.c"

# Get the current default sink
CURRENT_SINK=$(pactl get-default-sink)

# Toggle between speakers and headphones
if [ "$CURRENT_SINK" = "$SPEAKERS" ]; then
    pactl set-default-sink "$HEADPHONES"
    NEW_SINK="$HEADPHONES"
else
    pactl set-default-sink "$SPEAKERS"
    NEW_SINK="$SPEAKERS"
fi

# Move all current sink inputs to the new sink
pactl list short sink-inputs | while read -r stream; do
    STREAM_ID=$(echo "$stream" | cut -f1)
    pactl move-sink-input "$STREAM_ID" "$NEW_SINK"
done
