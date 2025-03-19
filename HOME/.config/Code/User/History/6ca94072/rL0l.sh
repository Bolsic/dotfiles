#!/bin/bash
DOTFILES_HOME_DIR=~/dotfiles/HOME
cd $DOTFILES_HOME_DIR || exit
for file in *; do
    ln -sf $DOTFILES_HOME_DIR/$file ~/.$file
done
