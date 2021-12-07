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

# AFTER INSTALL

https://www.reddit.com/r/archlinux/comments/qzlfsu/what_are_some_postinstallation_optimizations_that/

grub config

╰─`sudo nano /etc/default/grub`

...

`GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 mitigations=off"`

...

to improve SSD lifespan and performance in the long term

╰─`sudo systemctl enable fstrim.timer` 

swap file

online:

╰─`sudo echo "vm.swappiness=10" | sudo tee /etc/sysctl.d/10-swappiness.conf`

or:

╰─`sudo nano /etc/sysctl.d/10-swappiness.conf`

add:

...

`vm.swappiness=10`

...

will be applied after reboot


### PACMAN ( https://www.youtube.com/watch?v=HD7jJEh4ZaM&ab_channel=LearnLinuxTV )

NOTE: You must run `pacman-key --init` before first using pacman; the local

keyring can then be populated with the keys of all official Arch Linux

packagers with `pacman-key --populate archlinux`

in `/etc/pacman.conf` put `ParallelDownloads = 10` (or whatever number you want), add `ILoveCandy` to `pacman.conf`

enable multi mirrors

╰─`sudo vim /etc/pacman.conf`

uncomment: `[multilib] Include`

update & upgrade

╰─`sudo pacman -Syu`

query
╰─`sudo pacman -Ss <to search>`

remove

╰─`pacman -Rns <name>`

https://wiki.archlinux.org/title/Pacman/Package_signing#Initializing_the_keyring ?? sudo pacman-key --init


### YAY

https://github.com/Jguer/yay

$ sudo pacman -S git [optional if you have installed it]

$ git clone https://aur.archlinux.org/yay-git.git

$ cd yay-git/

$ makepkg -si

$ cd .. && sudo rm -r yay-git

#### First Use

Development packages upgrade

Use `yay -Y --gendb` to generate a development package database for *-git packages that were installed without yay. This command should only be run once.

`yay -Syu --devel` will then check for development package updates

Use `yay -Y --devel --save` to make development package updates permanently enabled (`yay` and `yay -Syu` will then always check dev packages)

...


### Sleep/Hybern

/etc/default/grub

╰─`sudo nano /etc/mkinitcpio.conf`

at `HOOKS` add `resume` after `lvm2`

╰─`mkinitcpio -P`

https://wiki.archlinux.org/title/Power_management/Suspend_and_hibernate

https://austingwalters.com/increasing-battery-life-on-an-arch-linux-laptop-thinkpad-t14s/


# PAKAGES

`linux-lts linux-lts-headers openssh vim nano git curl wget bash-completion`

https://github.com/scop/bash-completion

network

`nm-connection-editor network-manager-applet wpa_supplicant wireless_tools netctl`

utils

`grub-customizer lshw usbutils neofetch zip unzip p7zip firefox tmux flameshot ktorrent`

printer service

`cups`

fonts https://wiki.archlinux.org/title/fonts#Installation

`all-repository-fonts`

`ttf-ms-fonts ttf-ms-win10`

font Cantarell??

### TUXEDO REPO

https://github.com/tuxedocomputers

https://www.reddit.com/r/tuxedocomputers/comments/qngn8r/manjaro_and_tuxedo_control_center/

https://aur.archlinux.org/packages/tuxedo-touchpad-switch/

https://aur.archlinux.org/packages/tuxedo-keyboard/

https://aur.archlinux.org/packages/tuxedo-control-center-bin/

### powerlevel10k

https://github.com/romkatv/powerlevel10k

install pwlv10k font

╰─`pacman -S ttf-meslo-nerd-font-powerlevel10k`

Enable font in terminal

`Konsole`: Open Settings → Edit Current Profile → Appearance, click Select Font and select `MesloLGS NF Regular`

`Visual Studio Code`: Open File → Preferences → Settings (PC) or Code → Preferences → Settings (Mac), enter `terminal.integrated.fontFamily` in the search box at the top of Settings tab and set the value below to `MesloLGS NF` see -> https://raw.githubusercontent.com/romkatv/powerlevel10k-media/389133fb8c9a2347929a23702ce3039aacc46c3d/visual-studio-code-font-settings.jpg , https://github.com/romkatv/powerlevel10k/issues/671

in case of trouble: Run ╰─`p10k configure` to generate a new `~/.p10k.zsh`. The old config may work incorrectly with the new font.

Install pwlvl10k

╰─`yay -S --noconfirm zsh-theme-powerlevel10k-git
echo 'source /usr/share/zsh-theme-powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc`

run `p10k configure`

### ohmyzsh plugins

https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins-Overview

https://github.com/zsh-users/zsh-syntax-highlighting/blob/master/INSTALL.md
  
zsh plugins=( sudo zsh-autosuggestions zsh-syntax-highlighting dirhistory colored-man-pages colorize )
  
https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md#manual-git-clone

### Stacer

https://github.com/oguzhaninan/Stacer

### Timeshift

https://github.com/teejee2008/timeshift ( https://www.youtube.com/watch?v=QE0lyWodWdU )

https://documentation.suse.com/sles/12-SP4/html/SLES-all/cha-lvm-snapshots.html

### sddm themes

https://adhec.github.io/sddm_themes/

### live wallpapers

https://github.com/cheesecakeufo/komorebi

https://github.com/GhostNaN/mpvpaper

### postgresql

https://wiki.archlinux.org/title/PostgreSQL

### mongodb

https://wiki.archlinux.org/title/MongoDB

https://aur.archlinux.org/packages/mongodb-compass/

### vscode

https://wiki.archlinux.org/title/Visual_Studio_Code

### grub themes

https://www.gnome-look.org/p/1603282

https://www.gnome-look.org/p/1528917/

https://www.gnome-look.org/p/1482847/

### splash screen
  
https://www.reddit.com/r/kde/comments/c68o40/i_made_a_gif_i_want_to_use_as_a_splash_screen_how/
  
### window tiling
  
https://swaywm.org/
  
https://github.com/kwin-scripts/kwin-tiling
  
https://store.kde.org/p/1309653/
  
https://github.com/lingtjien/Grid-Tiling-Kwin

### systemd in System settings

https://store.kde.org/p/1127873/
  
### manjaro theme

╰─`yay breath-theme-git`  

plasma

https://gitlab.manjaro.org/artwork/themes/breath
  
https://manjaro.org/branch-compare/?q=breath2

grub

https://gitlab.manjaro.org/artwork/branding/grub-theme
 

## FONTS

https://wiki.archlinux.org/title/Fonts#Font_packages

https://fontlibrary.org/en

Core TTF Fonts from Microsoft

`ttf-ms-fonts`

Microsoft Vista and Office 2007 True Type Fonts

`ttf-vista-fonts`

fira

`ttf-fira-code`

Humanist sans serif font

`cantarell-fonts`

Google Noto emoji fonts

`noto-fonts-emoji`

## metapakages

`all-repository-fonts`
 
TrueType fonts from the Google Fonts project (git version)

`ttf-google-fonts-git`
