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

### Sleep & Hibernate

https://wiki.archlinux.org/title/Power_management/Suspend_and_hibernate

https://austingwalters.com/increasing-battery-life-on-an-arch-linux-laptop-thinkpad-t14s/

https://forums.linuxmint.com/viewtopic.php?t=287015

check swap partition mount dir

╰─`sudo cat /etc/fstab`

es mount: `/dev/mapper/archVG-swap`

add swap into grub conf

╰─`sudo nano /etc/default/grub`

`GRUB_CMDLINE_LINUX_DEFAULT="...resume=/dev/archVolumeGroup/archLogicalVolume"`

update grub

╰─`sudo grub-mkconfig -o /boot/grub/grub.cfg`

add hooks

╰─`sudo nano /etc/mkinitcpio.conf`

-> BTRFS: at `HOOKS` add `resume` after `filesystem` before `fsck` (wiki says after `udev`)

-> LVM: at `HOOKS` add `resume` after `lvm2` (not sure) 

╰─`mkinitcpio -P`

reboot/hybernate

# PAKAGES

### TUXEDO REPO

https://github.com/tuxedocomputers

https://www.reddit.com/r/tuxedocomputers/comments/qngn8r/manjaro_and_tuxedo_control_center/

https://aur.archlinux.org/packages/tuxedo-touchpad-switch/

https://aur.archlinux.org/packages/tuxedo-keyboard/

https://aur.archlinux.org/packages/tuxedo-control-center-bin/

### zsh

╰─`sudo pacman -S zsh zsh-completions zsh-syntax-highlighting zsh-autosuggestions`

https://wiki.archlinux.org/title/Command-line_shell#Changing_your_default_shell

list available shells

╰─`chsh -l`

change default shell to zsh for root
 
╰─`sudo chsh -s /bin/zsh`
 
and for the current user
 
╰─`chsh -s /bin/zsh`

extra: add line to .zshrc `export SHELL=zsh`

### powerlevel10k

https://github.com/romkatv/powerlevel10k

install pwlv10k font

╰─`yay ttf-meslo-nerd-font-powerlevel10k`

Enable font in terminal

`Konsole`: Open Settings → Edit Current Profile → Appearance, click Select Font and select `MesloLGS NF Regular`

`Visual Studio Code`: Open File → Preferences → Settings (PC) or Code → Preferences → Settings (Mac), enter `terminal.integrated.fontFamily` in the search box at the top of Settings tab and set the value below to `MesloLGS NF` see -> https://raw.githubusercontent.com/romkatv/powerlevel10k-media/389133fb8c9a2347929a23702ce3039aacc46c3d/visual-studio-code-font-settings.jpg , https://github.com/romkatv/powerlevel10k/issues/671

in case of trouble: Run ╰─`p10k configure` to generate a new `~/.p10k.zsh`. The old config may work incorrectly with the new font.

Install pwlvl10k

```
yay -S --noconfirm zsh-theme-powerlevel10k-git
echo 'source /usr/share/zsh-theme-powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc
```

open terminal or run `p10k configure` to change/overvrite

### ohmyzsh plugins

https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins-Overview

https://github.com/zsh-users/zsh-syntax-highlighting/blob/master/INSTALL.md

https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md#manual-git-clone
  
zsh plugins=( sudo zsh-autosuggestions zsh-syntax-highlighting dirhistory colored-man-pages colorize )

### Stacer

https://github.com/oguzhaninan/Stacer

### Timeshift

https://github.com/teejee2008/timeshift ( https://www.youtube.com/watch?v=QE0lyWodWdU )

https://documentation.suse.com/sles/12-SP4/html/SLES-all/cha-lvm-snapshots.html

### snapper

https://wiki.archlinux.org/title/snapper

### browsers and mail

╰─`yay google-chrome firefox thunderbird kmail`

### postgresql

https://wiki.archlinux.org/title/PostgreSQL

### mongodb

https://wiki.archlinux.org/title/MongoDB

https://aur.archlinux.org/packages/mongodb-compass/

https://www.reddit.com/r/mongodb/comments/mj1zr0/successfully_achieved_darkmode_for_mongodb_compass/

╰─`yay mongodb-bin mongodb-tools-bin mongodb-compass`

╰─`sudo systemctl mongod status`

╰─`sudo systemctl enable mongodb.service`

╰─`sudo systemctl start mongodb.service`

╰─`mongo`

### vscode

https://wiki.archlinux.org/title/Visual_Studio_Code

╰─`yay visual-studio-code-bin`

config git

╰─`sudo pacman -S gnome-keyring`

and https://stackoverflow.com/questions/34400272/visual-studio-code-is-always-asking-for-git-credentials , https://github.blog/2020-12-15-token-authentication-requirements-for-git-operations/

### github desktop

╰─`yay github-desktop-bin`

https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup

https://man.archlinux.org/man/gitcredentials.7

### insomnia

╰─`yay insomnia-bin`

### python

https://wiki.archlinux.org/title/python#Package_management

https://github.com/pypa/pipenv

https://wiki.archlinux.org/title/Python/Virtual_environment

╰─`sudo pacman -S python-pipenv`

### node & npm

https://wiki.archlinux.org/title/Node.js

╰─`sudo pacman -S nodejs npm`

### Docker

https://wiki.archlinux.org/title/Docker#Installation

for btrfs https://www.reddit.com/r/docker/comments/mba2c7/how_do_i_make_docker_work_nicely_with_btrfs_host/ , https://github.com/egara/arch-btrfs-installation   

╰─`sudo pacman -S docker`

╰─`sudo systemctl enable docker.service`

╰─`sudo systemctl enable containerd.service`

╰─`sudo systemctl start docker.service`

╰─`sudo systemctl start containerd.service`

╰─`sudo docker info`

remove sudo

╰─`sudo groupadd docker`

╰─`sudo usermod -aG docker $USERTOADD`

REBOOT and test

╰─`docker run hello-world`

PORTAINER GUI 

https://github.com/portainer/portainer

https://docs.portainer.io/v/ce-2.9/start/install/server/docker/linux

https://www.portainer.io/casestudy/firstapp

╰─`docker volume create portainer_data`

and

```
docker run -d -p 8000:8000 -p 9000:9000 -p 9443:9443 \
    --name=portainer --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:2.11.0
```
    
╰─`docker ps`

go to https://localhost:9443

╰─`yay portainer-bin`

change portainer app settings `http` to `https` and launcher default port `9000` to `9443`

### fix containerd-shim hangs on reboot/shutdown

https://github.com/containerd/containerd/issues/386 , https://github.com/containerd/containerd/issues/386

Instead of directly editing the systemd service files in `/lib` (which might not be writable depending on the Linux distribution), use `sudo systemctl edit docker` and add:

```
[Unit]
After=containerd.service
Wants=containerd.service
```

(Using `Wants` instead of `Requires` per moby/moby@a985655)

This will create `/etc/systemd/system/docker.service.d/override.conf`, which you’ll also see listed in `systemctl status docker`.

### libreoffice

╰─`sudo pacman -S libreoffice-fresh libreoffice-extension-texmaths libreoffice-extension-writer2latex hunspell hunspell-en_us hyphen hyphen-en libmythes mythes-en`

fonts `ttf-dejavu noto-fonts`

### spotify

https://wiki.archlinux.org/title/Spotify#Installation

╰─`yay spotify`

### kwallet

https://wiki.archlinux.org/title/KDE_Wallet

https://wiki.archlinux.org/title/GNOME/Keyring#Troubleshooting

╰─`sudo pacman -S khelpcenter kwallet kwalletmanager`

### pamac

https://wiki.manjaro.org/index.php/Pamac

https://aur.archlinux.org/packages/pamac-aur/?O=10&PP=10

╰─`yay pamac` also `pamac-tray-appindicator`

### grub themes

https://www.gnome-look.org/p/1603282

https://www.gnome-look.org/p/1528917/

https://www.gnome-look.org/p/1482847/

### splash screen
  
https://www.reddit.com/r/kde/comments/c68o40/i_made_a_gif_i_want_to_use_as_a_splash_screen_how/
  
### sddm themes

https://adhec.github.io/sddm_themes/

### live wallpapers

https://github.com/cheesecakeufo/komorebi

https://github.com/GhostNaN/mpvpaper

### manjaro theme

╰─`yay breath-theme-git`  

plasma

https://wiki.manjaro.org/index.php/Install_Desktop_Environments

https://gitlab.manjaro.org/artwork/themes/breath
  
https://manjaro.org/branch-compare/?q=breath2

grub

https://gitlab.manjaro.org/artwork/branding/grub-theme
  
### window tiling
  
https://swaywm.org/ (wayland)

japokwm (wayland)
  
https://github.com/kwin-scripts/kwin-tiling
  
https://store.kde.org/p/1309653/
  
https://github.com/lingtjien/Grid-Tiling-Kwin
 

# FONTS

https://wiki.archlinux.org/title/Fonts#Font_packages

https://fontlibrary.org/en

### Basic fonts

╰─`yay -S`

`cantarell-fonts ttf-fira-code ttf-merriweather ttf-merriweather-sans ttf-oswald ttf-carlito ttf-quintessential ttf-signika` Google Noto emoji fonts `noto-fonts-emoji`

`gnu-free-fonts noto-fonts ttf-bitstream-vera ttf-croscore ttf-dejavu ttf-droid ttf-ibm-plex ttf-liberation`

Core TTF Fonts from Microsoft

`ttf-ms-fonts`

Microsoft Vista and Office 2007 True Type Fonts

`ttf-vista-fonts`

### metapakages

`all-repository-fonts`
 
TrueType fonts from the Google Fonts project (git version)

`ttf-google-fonts-git`