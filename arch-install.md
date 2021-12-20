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

╰─`ip addr`

then ssh \# `ssh root@<ip addr>`

## synking clock

╰─`timedatectl set-ntp true`


# 4 DISK SETUP UEFI/GPT USING LVM

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

## FINAL CHECK

╰─`df -hT`

╰─`lsblk`

# 11 START INSTALL USING PACSTRAP

╰─`pacstrap /mnt base base-devel linux linux-firmware lvm2 amd-ucode vim nano`

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


╰─`nano /etc/mkinitcpio.conf`

add `lvm2` at `HOOKS` between `block` and `filesystems`

╰─`mkinitcpio -P`

if lts is installed
( mkinitcpio -p linux-lts )


# 15 SET UP ROOT PASSWORD AND ADD USER

╰─`passwd`

useradd -m -g users -G wheel \<username\>

╰─`useradd -m -g users -G wheel fabo`

╰─`passwd fabo`

## add to sudoers

check `pacman -S sudo`

╰─`EDITOR=nano visudo` or `EDITOR=vim visudo`

uncomment %wheel ALL...

# 16 BOOTMANAGER INSTALL

## UPDATE PACkage MANager

NOTE: You must run `pacman-key --init` before first using pacman;

the local keyring can then be populated with the keys of all official Arch Linux

packagers with `pacman-key --populate archlinux`

in `/etc/pacman.conf` put `ParallelDownloads = 10` (or whatever number you want),
add `ILoveCandy` to pacman.conf

update & upgrade & mirrirs

╰─`sudo pacman -Syyu`

basic update & upgrade

╰─`sudo pacman -Syu`

## NETWORK MANAGER ( https://wiki.archlinux.org/title/NetworkManager#Usage )

╰─`pacman -S networkmanager bluez openssh`

@extra `bluez-utils network-manager-applet dialog wpa_supplicant wireless_tools netctl`

(aur: `wpa_supplicant_gui`)

#### start/enable services

╰─`systemctl enable sshd`

╰─`systemctl enable NetworkManager.service`

╰─`systemctl enable bluetooth.service`

## GRUB INSTALL

https://wiki.archlinux.org/title/GRUB#UEFI_systems

╰─`pacman -S grub efibootmgr grub-customizer`

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

╰─`pacman -S plasma-meta plasma-wayland-session wayland-protocols`

@extra `kde-applications`

## INSTALL USEFUL PACKAGES

╰─`pacman -S`

`linux-headers git curl wget bash-completion konsole lshw usbutils neofetch tmux firefox nm-connection-editor firewalld` and  `kde-system-meta dnsmasq ark zip unzip p7zip dolphin kate kwrite kbackup kcalc kfind kmag knotes ktimer ktorrent kipi-plugins dragon gwenview spectacle okular kamoso sweeper kcharselect markdownpart kdialog`

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

# ENABLE DISPLAY MANAGER TO ENABLE SYSTEM GUI
 
╰─`systemctl enable sddm`

## REBOOT

login as `root` or user
 
## KDE apps
 
╰─`pacman -S` for kde discover install `packagekit-qt5 fwupd discover` for flatpack b/end `flatpak`

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

extras `python-pygments digikam filelight kcolorchooser kontrast skanlite kdeconnect kdenetwork-filesharing print-manager cups`


# ENJOY
