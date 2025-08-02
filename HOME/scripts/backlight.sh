#!/bin/bash

# This script is used to manage the backlight settings of the system.


up() {
	brightnessctl s +10%
}
 
down() {
	brightnessctl s 10%-
}
