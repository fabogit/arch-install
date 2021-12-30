https://wiki.archlinux.org/title/Installation_guide

# 1 SET KEYBOARD LAYOUT

loadkeys \<kbrdlout ex: us,it\>

╰─`loadkeys us`


# 2 CHECK NETWORK

╰─`ip link`

╰─`ping -c 3 archlinux.org`


# 3 CONNECT WIFI

╰─`iwctl`

╰─`device list`

╰─`station <device> scan`

╰─`station <device> get-networks`

╰─`station <device> connect <SSID>`

╰─`device <device> show`

╰─`station <device> show`

╰─`exit`

...

### SET UP FOR INSTALL OVER SSH

set root pwd

╰─`passwd`

...

Check that `PermitRootLogin yes` is present (and uncommented)
in `/etc/ssh/sshd_config`

╰─`nano /etc/ssh/sshd_config`

This setting allows root login with
password authentication on the SSH server.

Finally, start the openssh daemon with 

╰─`systemctl start sshd.service`

which is included by default on the live CD.

Note: Unless required, after installation it is recommended
to remove `PermitRootLogin yes` from `/etc/ssh/sshd_config`

...


get ip

╰─`ip a`

then ssh \# `ssh root@<ip addr>`

## synking clock

╰─`timedatectl set-ntp true`

## rank mirrors

╰─`reflector -c Italy -a 6 --sort rate --save /etc/pacman.d/mirrorlist`

sync

╰─`pacman -Syy`



# 4 DISK SETUP

`Size: 953.87 GiB, 1024209543168 bytes, 2000409264 sectors`

### BFTRS

...

```
NAME                    SIZE        TYPE    MOUNTPOINTS FS      SECTORS
nvme0n1                 953.9G      disk    /dev        GPT     2000409264
├─nvme0n1p1             0.2G        part    /boot       f32     419840
├─nvme0n1p2             921.7G      part    /           btrfs   1932878479
├─nvme0n1p3             32G         part    [SWAP]      swap    367108864

```
...

### LVM

...

```
NAME                    SIZE        TYPE    MOUNTPOINTS FS      SECTORS
nvme0n1                 953.9G      disk    /dev        GPT     2000409264
├─nvme0n1p1             370M        part    /boot       f32     757760
└─nvme0n1p2             953.5G      part                lvm     1999649423
  ├─archVG-root         715.5G      lvm     /           ext4    1500512256
  └─archVG-swap         38G         lvm     [SWAP]      swap    79691776
  
```

...


# UEFI/GPT BTRFS SETUP

https://www.nishantnadkarni.tech/posts/arch_installation/

https://wiki.archlinux.org/title/User:Altercation/Bullet_Proof_Arch_Install#Partition_Drive

# 5 create partitions

╰─`cfdisk /dev/nvme0n1`

...

-> cfdisk GPT

`/dev/EFIpartition`	size: 0.2G	type: `EFI System`

`/dev/root`	size: 900G	type: `Linux FileSystem`

`/dev/swap`	size: 32G	type: `Linux Swap`

write & quit

...

# 6 format partitions

boot fat32

╰─`mkfs.fat -F32 /dev/nvme0n1p1`

root btrfs

╰─`mkfs.btrfs /dev/nvme0n1p2`

swap

╰─`mkswap /dev/nvme0n1p3`

╰─`swapon /dev/nvme0n1p3`

# 7 mount /root

╰─`mount /dev/nvme0n1p2 /mnt`

# 8 create subvolumes

root sbvl

╰─`btrfs su cr /mnt/@`

home sbvl

╰─`btrfs su cr /mnt/@home`

snapshots sbvl

╰─`btrfs su cr /mnt/@snapshots`

# 9 umount mount directory

╰─`umount /mnt`

# 10 mount subvolumes

TEST `mount -t btrfs -o subvol=rootnoatime,commit=60,compress=zstd,space_cache=v2 LABEL=system /mnt`

root btrfs option and mount

╰─`mount -o noatime,commit=60,compress=zstd ,space_cache=v2,subvol=@ /dev/nvme0n1p2 /mnt`

create folders on mount

╰─`mkdir -p /mnt/{boot,home,.snapshots}`

efi partition on boot

╰─`mount /dev/nvme0n1p1 /mnt/boot`

home

╰─`mount -o noatime,commit=60,compress=zstd,space_cache=v2,subvol=@home /dev/nvme0n1p2 /mnt/home`

snapshots

╰─`mount -o noatime,commit=60,compress=zstd,space_cache=v2,subvol=@snapshots /dev/nvme0n1p2 /mnt/.snapshots`

# UEFI/GPT EXT4 LVM

https://wiki.archlinux.org/title/Partitioning#Example_layouts

╰─`fdisk -l`

cfdisk /dev/\<drive ex: nvme0n1\>

╰─`cfdisk /dev/nvme0n1`

...

-> cfdisk GPT

`/dev/EFIpartition`	size: 370M	type: `EFI System`

`/dev/LVMpartition`	size: \<all\>	type: `Linux LVM`

write & quit

...

fdisk -l /dev/\<drive\>

╰─`fdisk -l /dev/nvme0n1`


# 5 FORMAT /EFI PARTITION TO FAT32 FOR BOOTLOADER

mkfs.fat -F32 /dev/\<EFIpartition\>

╰─`mkfs.fat -F32 /dev/nvme0n1p1`

# LVM setup

https://documentation.suse.com/sles/12-SP4/html/SLES-all/cha-lvm.html#fig-lvm-explain

## 6 PHISICAL VOLUME

pvcreate /dev/\<LVMpartition\>

╰─`pvcreate /dev/nvme0n1p2`

╰─`pvs`

## 7 VIRTUAL GROUP

vgcreate \<virtual vol group name ex:archlinux\> /dev/\<partition2\>

╰─`vgcreate archVG /dev/nvme0n1p2`

╰─`vgs`

## 8 LOGICAL VOLUMES

lvcreate -L \<size ex: 20G\> \<on ex: archlinux\> -n \<name ex: root\>

╰─`lvcreate -L 715.5G archVG -n root`	\<665G\>

onlt if want `/root` and `/home` on separated partions

╰─`lvcreate -L 500G archVG -n home` 	\<500G\>

╰─`lvcreate -L 38G archVG -n swap`	\<38gb\>

╰─`lvs`

# 9 FORMAT lvs PARTITIONS

format /dev/\<VGname\>/\<partition\>

╰─`mkfs.ext4 /dev/archVG/root`

╰─ if `/home` has own partiton `mkfs.ext4 /dev/archVG/home`

╰─`mkswap /dev/archVG/swap`

╰─`lvs`

╰─`fdisk -l`

# 10 MOUNT PARTITIONS

mount /dev/\<VGname\>/\<root lv\> /mnt

╰─`mount /dev/archVG/root /mnt`

╰─`df -hT`

╰─`mkdir -p /mnt/boot`

╰─  separated `home` parttion `mkdir -p /mnt/home`

mount /dev/\<EFIpartition\> /mnt/boot

╰─`mount /dev/nvme0n1p1 /mnt/boot` (GRUB)

if /home has its own partition `mount /dev/archVG/home /mnt/home`

╰─`swapon /dev/archVG/swap`

╰─`free -h`

# BTRFS & LVM FINAL CHECK

╰─`df -hT`

╰─`lsblk`

# 11 START INSTALL USING PACSTRAP

╰─`pacstrap /mnt base base-devel linux linux-firmware amd-ucode vim nano git`

-> for BTRFS install `btrfs-progs`

-> ford LVM install `lvm2`

@extra: `linux-lts`

generate file system tabs

╰─`genfstab -U /mnt >> /mnt/etc/fstab`

╰─`more /mnt/etc/fstab`


# 12 ENTER INTO LINUX 

╰─`arch-chroot /mnt`

# 13 TZ & LANG

ln -sf /usr/share/zoneinfo/\<Region\>/\<Place\> /etc/localtime

╰─`ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime`

╰─`hwclock --systohc`

╰─`nano /etc/locale.gen`

### vim controls:

...

- i to enter insert mode,

- ESC for command mode,

- to save&quit ESC, :wq

- to discard&quit ESC, :q!

...

uncomment selected language `en_US.UTF-8`, s&q

╰─`locale-gen`

sys language

╰─`echo "LANG=en_US.UTF-8" > /etc/locale.conf`

keyboard layout

╰─`echo "KEYMAP=us" > /etc/vconsole.conf`

# 14 CREATE HOSTNAME

echo \<hostname\> > /etc/hostname

╰─`echo Arch > /etc/hostname`

edit host entries

╰─`nano /etc/hosts`


add:

127.0.0.1	localhost

::1		localhost

127.0.1.1	\<hostname\>.localdomain	\<hostname\>


```
127.0.0.1   localhost
::1         localhost
127.0.1.1   Arch.localdomain    Arch
```

# 15 SET UP ROOT PASSWORD AND ADD USER

╰─`passwd`

useradd -m -g users -G wheel \<username\>

╰─`useradd -m -g users -G wheel fabo`

╰─`passwd fabo`

## add to sudoers

check `pacman -S sudo`

╰─`EDITOR=nano visudo` or `EDITOR=vim visudo`

uncomment %wheel ALL...

# UPDATE PACkage MANager

NOTE: You must run `pacman-key --init` before first using pacman;

the local keyring can then be populated with the keys of all official Arch Linux

packagers with `pacman-key --populate archlinux`

in `/etc/pacman.conf` put `ParallelDownloads = 10` (or whatever number you want),
add `ILoveCandy` to pacman.conf

to clean pkgs download chace install

╰─`sudo pacman -S pacman-contrib`

run `paccache -r`

`systemctl` `enable` and `start` `paccache.timer`

to clean chache manually

`pacman -Sc`

to install pkgs: `pacman -S packagetoinstall` 

`Ss` to query pkgs dbs. `Si` info on pkgs `Qi` info on local installed pkgs

`Qdt` orphans `Qet` installed and not required as dependencies

`S` sync `y` refresh `u` update

╰─`sudo pacman -Syu`

to uninstall:

`R` remove `sc` dependencies and pkgs depending on it `n` config files

GUI pamac https://wiki.manjaro.org/index.php/Pamac

# YAY

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

# -> FOR LVM

╰─`nano /etc/mkinitcpio.conf`

add `lvm2` at `HOOKS` between `block` and `filesystems`, save & close

recreate kernel image

╰─`mkinitcpio -P`

if lts is installed
( mkinitcpio -p linux-lts )

# -> FOR BTRFS

╰─`nano /etc/mkinitcpio.conf`

add `btrfs` into `MODULES` between `()`, save & close

recreate kernel image

╰─`mkinitcpio -P`

snapper for system snapshots

╰─`pacman -S snapper`

## NETWORK MANAGER ( https://wiki.archlinux.org/title/NetworkManager#Usage )

network bluethoot ssh printer

╰─`pacman -S networkmanager bluez openssh cups`

@extra `bluez-utils network-manager-applet dialog wpa_supplicant wireless_tools netctl`

(aur: `wpa_supplicant_gui`)

#### start/enable services

╰─`systemctl enable sshd`

╰─`systemctl enable NetworkManager.service`

╰─`systemctl enable bluetooth.service`

╰─`systemctl enable cups.service` if error `systemctl enable org.cups.cupsd`

# 16 BOOTMANAGER INSTALL

## GRUB INSTALL

https://wiki.archlinux.org/title/GRUB#UEFI_systems

╰─`pacman -S grub efibootmgr grub-customizer`

-> for BTRFS install `grub-btrfs`

╰─`grub-install /dev/nvme0n1p1 --efi-directory=/boot --bootloader-id=arch-grub --recheck`

╰─`cp /usr/share/locale/en\@quot/LC_MESSAGES/grub.mo /boot/grub/locale/en.mo`

╰─`grub-mkconfig -o /boot/grub/grub.cfg`

optional EXIT & REBOOT

╰─`exit`

╰─`umount -a`

╰─`reboot`

### wifi connect after reboot into cli

╰─`nmcli device wifi list`

╰─`nmcli device wifi connect <SSID_or_BSSID> password <password>`

# 17 INSTALL XORG DISPLAY SERVER

https://wiki.archlinux.org/title/Xorg#Installation

╰─`pacman -S xorg`

@extra `xorg-server xorg-apps`


# 18 INSTALL VIDEO DRIVERS

sudo pacman -S xf86-video-\<DRIVERNAME es:amdgpu, intel\>

╰─`pacman -S xf86-video-amdgpu`

@extra `pulseaudio alsa-utils alsa-plugins pulseaudio-alsa`

# 19 INSTALL KDE
https://wiki.archlinux.org/title/KDE#Installation , https://wiki.archlinux.org/title/Wayland

╰─`pacman -S`

from plasma-meta

`bluedevil breeze-gtk drkonqi kde-gtk-config kdeplasma-addons kgamma5 khotkeys kinfocenter kscreen ksshaskpass kwallet-pam kwallet kwalletmanager knotifications  kwrited oxygen plasma-browser-integration plasma-desktop plasma-disks plasma-firewall plasma-nm plasma-pa plasma-systemmonitor plasma-vault plasma-workspace-wallpapers powerdevil sddm-kcm kio kio-extras systemsettings `

from plasma workspace

`kactivities-stats kactivities-stats kactivitymanagerd kde-cli-tools kholidays kio-extras knotifyconfig kpeople kquickcharts ksystemstats ktexteditor kuserfeedback kwin libkscreen libqalculate milou plasma-integration prison xorg-xmessage xorg-xrdb xorg-xsetroot appmenu-gtk-module plasma-workspace-wallpapers kdepim-addons networkmanager-qt baloo extra-cmake-modules gpsd kdoctools kinit kunitconversion networkmanager-qt plasma-wayland-protocols`

wayland

`kwayland-integration plasma-wayland-session wayland-protocols`

or `plasma-meta` pckg + wayland

@extra `kde-applications plasma-thunderbolt`

## INSTALL USEFUL PACKAGES

╰─`pacman -S`

`linux-headers git curl wget bash-completion konsole lshw usbutils neofetch tmux firefox nm-connection-editor firewalld` and `kde-system-meta kde-graphics-meta dnsmasq ark zip unzip p7zip dolphin kate kwrite kbackup kcalc kfind kmag knotes ktimer ktorrent kipi-plugins dragon gwenview spectacle okular kamoso sweeper kcharselect markdownpart kdialog xdg-utils xdg-user-dirs`

## PIPEWIRE AUDIO DRIVERS

@pipewire https://wiki.archlinux.org/title/PipeWire#Installation

╰─`pacman -S pipewire pipewire-docs pipewire-pulse xdg-desktop-portal xdg-desktop-portal-kde`

@extra `pipewire-alsa pipewire-jack`
 
### PulseAudio clients

Install `pipewire-pulse`. It will replace `pulseaudio` and `pulseaudio-bluetooth`. 
Reboot, re-login or execute `systemctl start --user pipewire-pulse.service` to see the effect.

Normally, no further action is needed, as the user service pipewire-pulse.socket` should be enabled automatically by the package. 
To check if the replacement is working, run the following command and see the output:

╰─`pactl info`

...
 
Server Name: PulseAudio (on PipeWire 0.3.32)
 
...

If PipeWire does not work correctly on system startup, validate that the Systemd/User services `pipewire-pulse.service`, `pipewire.service`, and `pipewire-media-session.service` are up and running. Keep in mind that `pipewire-pulse.service` and `pipewire-pulse.socket` have a `ConditionUser` against running as root.

...

TROUBLESHOUTING

PulseAudio cannot be uninstalled because it is too tied in to KDE
but the systemd socket and service for PulseAudio can be disabled to shut it down

 
`systemctl --user mask pulseaudio.socket --now`
 
`systemctl --user disable pulseaudio.service --now`

and the pipewire socket and service can be enabled instead

`systemctl --user enable pipewire.socket --now`
 
`systemctl --user start pipewire.service`

pipewire is very new and still a beta release
I have no idea what diagnostics and tools are available in pipewire if it does not work, and it is unlikely any tools for PulseAudio will work

...

GUI https://gitlab.freedesktop.org/ryuukyu/helvum


╰─`exit`

╰─`umount -a`

╰─`reboot`

## login into root

## connect wifi from cli after reboot

╰─`nmcli device wifi list`

╰─`nmcli device wifi connect <SSID_or_BSSID> password <password>`
 
 
# -> BTRFS configure snapper
 
umount snapshots dir
 
╰─`sudo umount /.snapshots`

remove snp dir

╰─`sudo rm -r ./.snapshots`
 
recreate snapper config

╰─`sudo snapper -c root create-config /`

remove created folder

╰─`sudo btrfs subvolume delete /.snapshots`

 recreate

╰─`sudo mkdir /.snapshots`

remount

╰─`sudo mount -a`
 
change permission to replace root

╰─`sudo chmod 750 /.snapshots`
 
edit config
 
╰─`sudo nano /etc/snapper/configs/root`

in `ALLOW_USERS` inside "" add username, set `TIMELINE_LIMIT_` to 0, `WEEKLY=3`, `DAILY=7`, `HOURLY=8`. save & close

enable timeline and timeline cleanup
 
╰─`sudo systemctl enable --now snapper-timeline.timer` 

╰─`sudo systemctl enable --now snapper-cleanup.timer` 

install snap-pac-grub and GUI
 
╰─`yay -S snap-pac-grub snapper-gui-git` 

configure hook for grub

╰─`sudo mkdir /etc/pacman.d/hooks`

╰─`sudo nano /etc/pacman.d/hooks/50-bootbackup.hook` 

...
 
[Trigger]
 
Operation = Upgrade
 
Operation = Install
 
Operation = Remove
 
Type = Path
 
Target = boot/*
 
[Action]
 
Depends = rsync
 
Description = Backup /boot...

When = PreTransaction

Exec = /usr/bin/rsync -a --delete /boot /.bootbackup

...

optional install rsync

╰─`sudo pacman -S rsync`
 
edit permission
 
╰─`sudo chmod a+rx /.snapshots`
 
add user

╰─`sudo chown :fabo /.snapshots`

DONE

... 
 
# ENABLE DISPLAY MANAGER TO ENABLE SYSTEM GUI
 
╰─`systemctl enable sddm`

## REBOOT

login as `root` or user
 
## KDE apps
 
╰─`pacman -S` for kde discover install `discover packagekit-qt5 fwupd discover` for flatpack b/end `flatpak`

Dolphin file exploirer plugins and file previews  https://wiki.archlinux.org/title/Dolphin
 
The following packages enable preview thumbnails in dolphin

- ffmpegthumbs: video thumbnails
- kdegraphics-thumbnailers: PDF and PS thumbnails
- qt5-imageformats: thumbnails for additional image formats
- kimageformats: thumbnails for additional image formats
- taglib: audio file thumbnails
- libappimage: AppImage thumbnails
- raw-thumbnailer: Raw image files from a camera

╰─`sudo pacman -S dolphin-plugins ffmpegthumbs kdegraphics-thumbnailers qt5-imageformats kimageformats taglib libappimage raw-thumbnailer`

extras `python-pygments digikam filelight kcolorchooser kontrast skanlite kdeconnect kdenetwork-filesharing print-manager`


# ENJOY
