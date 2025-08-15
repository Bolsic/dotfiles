# sxhkd Keybindings

Readable reference for the keybindings in `~/.config/sxhkd/sxhkdrc`.

> Tip: after editing bindings, reload sxhkd with `super + Escape` (it sends `pkill -USR1 -x sxhkd`).

## Notation

- **super** = <kbd>Win</kbd>/<kbd>Mod4</kbd>  
- **alt** = <kbd>Alt</kbd>/<kbd>Mod1</kbd>  
- **ctrl** = <kbd>Ctrl</kbd>  
- **shift** = <kbd>Shift</kbd>  
- **[** = `bracketleft` key, **]** = `bracketright` key, **`** = `grave` key  
- A **two-stroke chain** is written like `A ; B` → press `A`, then (within the timeout) press `B`.

---

## Common

| Keys | What it does | Command |
|---|---|---|
| `super + Return` | Open terminal | `alacritty` |
| `super + d` | Program launcher | `dmenu_run` |
| `super + n` | File manager | `nemo` |
| `super + l` | Lock screen (xjack mode) | `xlock -mode xjack` |
| `super + Escape` | Reload sxhkd | `pkill -USR1 -x sxhkd` |
| `super + alt + ctrl + q` | Quit bspwm | `bspc quit` |
| `super + alt + ctrl + r` | Restart bspwm | `bspc wm -r` |
| `super + shift + q` | Close focused window | `bspc node -c` |
| `super + shift + ctrl + q` | **Kill** focused window | `bspc node -k` |
| `super + shift + Delete ; Return` | **Shutdown** (confirm with `Return`) | `sudo shutdown -P now` |
| `super + shift + ctrl + Delete ; Return` | **Reboot** (confirm with `Return`) | `sudo shutdown -r now` |

---

## Window handling (bspwm)

### State & flags
| Keys | What it does | Command |
|---|---|---|
| `super + t` | Tile | `bspc node -t tiled` |
| `super + s` | Float | `bspc node -t floating` |
| `super + f` | Fullscreen | `bspc node -t fullscreen` |
| `super + ctrl + m` | Toggle **marked** | `bspc node -g marked` |
| `super + ctrl + x` | Toggle **locked** | `bspc node -g locked` |
| `super + ctrl + y` | Toggle **sticky** | `bspc node -g sticky` |
| `super + ctrl + z` | Toggle **private** | `bspc node -g private` |

### Focus vs swap (move) by direction
| Keys | Action | Command |
|---|---|---|
| `super + Left` | Focus west | `bspc node -f west` |
| `super + Down` | Focus south | `bspc node -f south` |
| `super + Up` | Focus north | `bspc node -f north` |
| `super + Right` | Focus east | `bspc node -f east` |
| `super + shift + Left` | **Swap** with west | `bspc node -s west` |
| `super + shift + Down` | **Swap** with south | `bspc node -s south` |
| `super + shift + Up` | **Swap** with north | `bspc node -s north` |
| `super + shift + Right` | **Swap** with east | `bspc node -s east` |

### Cycle focus
| Keys | What it does | Command |
|---|---|---|
| `super + c` | Focus next window (local, not hidden) | `bspc node -f next.local.!hidden.window` |
| `super + shift + c` | Focus previous window (local, not hidden) | `bspc node -f prev.local.!hidden.window` |

### Desktops
| Keys | What it does | Command |
|---|---|---|
| `super + [` | Focus previous desktop (on this monitor) | `bspc desktop -f prev.local` |
| `super + ]` | Focus next desktop (on this monitor) | `bspc desktop -f next.local` |
| `super + \`` | Focus **last** node | `bspc node -f last` |
| `super + Tab` | Focus **last** desktop | `bspc desktop -f last` |
| `super + 1…9` | Focus desktop 1…9 | `bspc desktop -f ^1` … `^9` |
| `super + 0` | Focus desktop 10 | `bspc desktop -f ^10` |
| `super + shift + 1…9` | Send focused window to desktop 1…9 **and follow** | `bspc node -d ^1 -f` … |
| `super + shift + 0` | Send focused window to desktop 10 **and follow** | `bspc node -d ^10 -f` |

---

## Preselect (bspwm split placement)

| Keys | What it does | Command |
|---|---|---|
| `super + ctrl + Left` | Preselect split west | `bspc node -p west` |
| `super + ctrl + Down` | Preselect split south | `bspc node -p south` |
| `super + ctrl + Up` | Preselect split north | `bspc node -p north` |
| `super + ctrl + Right` | Preselect split east | `bspc node -p east` |
| `super + ctrl + 1…9` | Preselect **ratio** 0.1…0.9 | `bspc node -o 0.1` … `0.9` |
| `super + ctrl + Space` | Cancel preselection | `bspc node -p cancel` |

---

## Applications & utility

| Keys | What it does | Command |
|---|---|---|
| `super + b` | Open browser (Zen) | `zen-browser` |
| `super + p` | Screenshot GUI | `flameshot gui` |
| `super + v` | VS Code | `code` |
| `super + alt + k` | Change keyboard combo (custom script) | `"$HOME/scripts/change-keyboard-set.sh"` |
| `super + o` | Obsidian | `obsidian` |
| `super + w` | WhatsApp (electron wrapper) | `elecwhat` |
| `super + a` | Audio control | `pavucontrol` |

---

## Media, backlight & Bluetooth

| Keys | What it does | Command |
|---|---|---|
| `super + XF86MonBrightnessUp` | Warm screen (≈5500K) | `redshift -O 5500K` |
| `super + XF86MonBrightnessDown` | Cool screen (≈7500K) | `redshift -O 7500K` |
| `super + XF86AudioMicMute` | Reset color temperature | `redshift -x` |
| `XF86MonBrightnessUp` | Increase brightness by 10% | `brightnessctl s +10%` |
| `XF86MonBrightnessDown` | Decrease brightness (custom script) | `bash -ic '. "$HOME/scripts/backlight.sh" && down'` |
| `XF86AudioRaiseVolume` | Volume +5 | `pulsemixer --change-volume +5` |
| `XF86AudioLowerVolume` | Volume −5 | `pulsemixer --change-volume -5` |
| `XF86AudioMute` | Toggle mute | `pulsemixer --toggle-mute` |
| `super + alt + b` | Bluetooth device selector (custom UI) | `"$HOME/scripts/bluetooth-connect-interface.sh"` |
| `super + alt + ctrl + b` | Disconnect from BT device | `bluetoothctl disconnect` |
| `super + XF86AudioMute` | Toggle audio output (BT ↔ speakers) | `"$HOME/scripts/toggle-audio-output.sh"` |

---

## (Disabled) move/resize examples

> These are commented out in your config. Uncomment to enable.

| Keys | What it would do | Command |
|---|---|---|
| `super + alt + Left/Down/Up/Right` | Expand window by pushing a side | `bspc node -z left -20 0 / bottom 0 20 / top 0 -20 / right 20 0` |
| `super + alt + shift + Left/Down/Up/Right` | Contract window by pulling a side | `bspc node -z right -20 0 / top 0 20 / bottom 0 -20 / left 20 0` |
| `super + Left/Down/Up/Right` | Move floating window | `bspc node -v -20 0 / 0 20 / 0 -20 / 20 0` |

---

## Requirements

Most bindings assume these tools are installed and on your `PATH`:

- `bspwm`, `bspc`, `sxhkd`
- `alacritty`, `dmenu_run`, `nemo`, `xlock`
- `zen-browser`, `flameshot`, `code`, `obsidian`, `pavucontrol`
- `redshift`, `brightnessctl`, `pulsemixer`, `bluetoothctl`
- Custom scripts used here (create or remove as needed):
  - `~/scripts/change-keyboard-set.sh`
  - `~/scripts/backlight.sh`
  - `~/scripts/bluetooth-connect-interface.sh`
  - `~/scripts/toggle-audio-output.sh`

---
