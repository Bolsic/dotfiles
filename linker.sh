#!/bin/bash
DOTFILES_HOME_DIR=~/dotfiles/HOME
cd "$DOTFILES_HOME_DIR" || exit

for file in *; do
  src="$DOTFILES_HOME_DIR/$file"
  dest="$HOME/.$file"

  mkdir -p "$(dirname "$dest")"
  [ -e "$dest" ] && rm -rf "$dest"   # Remove existing file/dir/symlink
  ln -sf "$src" "$dest"
done
