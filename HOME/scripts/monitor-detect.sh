#!/usr/bin/env bash

# 1. Variables: adjust these to match your setup
INTERNAL="eDP-1"
EXTERNAL="HDMI-1"

# 2. Check if the HDMI output is connected
if xrandr --query | grep -q "^${EXTERNAL} connected"; then
    # 3a. If HDMI is connected: switch exclusively to HDMI
    echo "HDMI detected: using only ${EXTERNAL}"
    xrandr \
        --output "${EXTERNAL}" --primary --auto \
        --output "${INTERNAL}" --off
else
    # 3b. If HDMI is not connected: use only the internal panel
    echo "HDMI not detected: falling back to ${INTERNAL}"
    xrandr \
        --output "${EXTERNAL}" --off \
        --output "${INTERNAL}" --auto
fi
