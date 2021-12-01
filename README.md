# arch-install
installation process for arch linux distro 


# links & utils

https://www.arcolinuxd.com/5-the-actual-installation-of-arch-linux-phase-1-uefi/

https://www.youtube.com/watch?v=TbvhcAspBkE&ab_channel=AaronStark

https://gilyes.com/Installing-Arch-Linux-with-LVM/

https://computingforgeeks.com/install-arch-linux-with-lvm-on-uefi-system/

https://archlinuxgui.in/tutorials.html

https://archinstall.readthedocs.io/en/latest/installing/guided.html

https://wiki.archlinux.org/title/Install_Arch_Linux_on_LVM

https://wiki.archlinux.org/title/KDE#Plasma

https://www.youtube.com/watch?v=A6xWiqOpulI&ab_channel=EF-LinuxMadeSimple

https://www.christitus.com/zsh/

https://www.youtube.com/watch?v=0szGhRFKpus&ab_channel=EF-LinuxMadeSimple

https://www.youtube.com/watch?v=exQh0_JKBJQ&ab_channel=LinuxScoop

https://www.youtube.com/watch?v=SVh4osULjP4&ab_channel=DanielLaera

https://www.youtube.com/watch?v=UsKd9Y42Mo0&ab_channel=codeTalk

https://medium.com/macoclock/enhance-your-terminal-with-manjaros-zsh-config-ecada5b2897d

https://github.com/zsh-users/zsh-syntax-highlighting

https://github.com/zsh-users/zsh-autosuggestions

https://www.addictivetips.com/ubuntu-linux-tips/backup-kde-plasma-5-desktop-linux/

https://itsfoss.com/backup-restore-linux-timeshift/

UPDATE PACMAN

NOTE: You must run pacman-key --init before first using pacman; the local

keyring can then be populated with the keys of all official Arch Linux

packagers with pacman-key --populate archlinux

enable multi mirrors

# sudo vim /etc/pacman.conf

uncomment: [multilib] Include

# AFTER INSTALL

https://www.reddit.com/r/archlinux/comments/qzlfsu/what_are_some_postinstallation_optimizations_that/

PACMAN ( https://www.youtube.com/watch?v=HD7jJEh4ZaM&ab_channel=LearnLinuxTV )

in /etc/pacman.conf put ParallelDownloads = 10 (or whatever number you want), add ILoveCandy to pacman.conf

update & upgrade

# sudo pacman -Syyu

remove

# pacman -Rns <name>

https://wiki.archlinux.org/title/Pacman/Package_signing#Initializing_the_keyring ?? sudo pacman-key --init


# PAKAGES

linux-lts

linux-lts-headers

openssh

vim

nano

git

curl

wget

bash-completion ( https://github.com/scop/bash-completion )

nm-connection-editor

network-manager-applet

xorg-apps

wpa_supplicant

wireless_tools

netctl

grub-customizer

lshw

usbutils

neofetch

zip

unzip

p7zip

firefox

tmux

ktorrent

flameshot

cups (printer service)

all-repository-fonts

ttf-ms-fonts

ttf-ms-win10

?pamac ?kwayland ?packagekit-qt5 ?powertop https://wiki.archlinux.org/title/Powertop

font Cantarell??

https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/linux/chromium_packages.md

https://github.com/Jguer/yay

$ sudo pacman -S git [optional if you have installed it]

$ git clone https://aur.archlinux.org/yay-git.git

$ cd yay-git/

$ makepkg -si

$ cd .. && sudo rm -r yay-git

https://github.com/tuxedocomputers

https://www.reddit.com/r/tuxedocomputers/comments/qngn8r/manjaro_and_tuxedo_control_center/

https://aur.archlinux.org/packages/tuxedo-touchpad-switch/

https://aur.archlinux.org/packages/tuxedo-keyboard/

https://aur.archlinux.org/packages/tuxedo-control-center-bin/

https://github.com/romkatv/powerlevel10k

https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins-Overview

https://github.com/ohmyzsh/ohmyzsh

https://github.com/zsh-users/zsh-syntax-highlighting/blob/master/INSTALL.md
  
zsh plugins=( sudo zsh-autosuggestions zsh-syntax-highlighting dirhistory colored-man-pages colorize )
  
https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md#manual-git-clone

https://github.com/oguzhaninan/Stacer

https://github.com/teejee2008/timeshift ( https://www.youtube.com/watch?v=QE0lyWodWdU )

https://documentation.suse.com/sles/12-SP4/html/SLES-all/cha-lvm-snapshots.html

https://adhec.github.io/sddm_themes/

https://github.com/cheesecakeufo/komorebi

https://github.com/GhostNaN/mpvpaper

https://wiki.archlinux.org/title/PostgreSQL

https://wiki.archlinux.org/title/MongoDB

https://aur.archlinux.org/packages/mongodb-compass/

https://wiki.archlinux.org/title/Visual_Studio_Code

pacman -S python-pygments qt5-imageformats breeze-grub packagekit-qt5 fwupd

https://www.gnome-look.org/p/1603282

https://www.gnome-look.org/p/1528917/

https://www.gnome-look.org/p/1482847/
  
https://github.com/kwin-scripts/kwin-tiling
  
https://store.kde.org/p/1309653/
  
https://github.com/lingtjien/Grid-Tiling-Kwin
  
manjaro theme

https://gitlab.manjaro.org/artwork/themes/breath
  
https://manjaro.org/branch-compare/?q=breath2
  
