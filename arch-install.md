 

# 1 keyboard layout

loadkeys \<kbrdlout ex: us,it\>

\# `loadkeys us`


# 2 check ntwk

\# `ip link`

\# `ping -c 3 archlinux.org`


# 3 connect wifi

\# `iwctl`

\# `device list`

\# `station <device> scan`

\# `station <device> get-networks`

\# `station <device> connect <SSID>`

pwd 9287 1680 9720 7776 5516

\# `device <device> show`

\# `station <device> show`

\# `exit`


# SSH install

\# `systemctl start sshd`

set root pwd

\# `passwd`

//

Now check that `PermitRootLogin yes` is present (and uncommented)
in `/etc/ssh/sshd_config`

This setting allows root login with
password authentication on the SSH server.

Finally, start the openssh daemon with sshd.service,
which is included by default on the live CD.

Note: Unless required, after installation it is recommended
to remove PermitRootLogin yes from /etc/ssh/sshd_config

//


get ip

\# `ip addr`

then ssh \# `ssh root@<ip addr>`

#### sync clock

\# `timedatectl set-ntp true`


# 4 DISK partition UEFI/GPT LVM

https://wiki.archlinux.org/title/Partitioning#Example_layouts

\# `fdisk -l`

cfdisk /dev/\<drive ex: nvme0n1\>

\# `cfdisk /dev/nvme0n1`

-> cfdisk GPT

/dev/EFIpartition	size: 370M	type: EFI System

/dev/LVMpartition	size: \<all\>	type: Linux LVM

write, quit

fdisk -l /dev/\<drive\>

\# `fdisk -l /dev/nvme0n1`


# 5 format /efi to fat32 for bootloader

mkfs.fat -F32 /dev/\<EFIpartition\>

\# `mkfs.fat -F32 /dev/nvme0n1p1`



# LVM setup

https://documentation.suse.com/sles/12-SP4/html/SLES-all/cha-lvm.html#fig-lvm-explain

## 6 phisical volume

pvcreate /dev/\<LVMpartition\>

\# `pvcreate /dev/nvme0n1p2`

\# `pvs`


## 7 volume group

vgcreate \<virtual vol group name ex:archlinux\> /dev/\<partition2\>

\# `vgcreate archVG /dev/nvme0n1p2`

\# `vgs`


## 8 logical volumes

lvcreate -L \<size ex: 20G\> \<on ex: archlinux\> -n \<name ex: root\>

\# `lvcreate -L 715.5G archVG -n root`	\<665G\>

\# ( `lvcreate -L 500G archVG -n home` 	\<500G\> )

\# `lvcreate -L 38G archVG -n swap`	\<38gb\>

\# `lvs`


# 9 FORMAT lv

format /dev/\<VGname\>/\<partition\>

\# `mkfs.ext4 /dev/archVG/root`

\# ( `mkfs.ext4 /dev/archVG/home` )

\# `mkswap /dev/archVG/swap`

\# `lvs`

\# `fdisk -l`


# 10 MOUNT root and partitions

mount /dev/\<VGname\>/\<root lv\> /mnt

\# `mount /dev/archVG/root /mnt`

\# `df -hT`

\# `mkdir -p /mnt/boot`

\# ( `mkdir -p /mnt/home` )

mount /dev/\<EFIpartition\> /mnt/boot

\# @GRUB `mount /dev/nvme0n1p1 /mnt/boot`

\# ( `mount /dev/archVG/home /mnt/home` )

\# `swapon /dev/archVG/swap`

\# `free -h`

#### CHECK ALL

\# `df -hT`

\# `lsblk`

# 11 pacstrap for base install

\# `pacstrap /mnt base base-devel linux linux-firmware lvm2 amd-ucode vim nano`

@extra:
linux-lts

generate file system tabs

\# `genfstab -U /mnt >> /mnt/etc/fstab`

\# `more /mnt/etc/fstab`


# 12 root LOG into linux

\# `arch-chroot /mnt`

# 13 set timezone&language

\# ln -sf /usr/share/zoneinfo/\<Region\>/\<Place\> /etc/localtime

\# `ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime`

\# `hwclock --systohc`

\# `nano /etc/locale.gen`

vim:
- i to enter insert mode,

- ESC for command mode,

- to save&quit ESC, :wq

- to discard&quit ESC, :q!

uncomment selected language `en_US.UTF-8`, s&q

\# `locale-gen`

sys language

\# `echo "LANG=en_US.UTF-8" > /etc/locale.conf`

keyboard layout

\# `echo "KEYMAP=us" > /etc/vconsole.conf`

# 14 hostname

echo \<hostname\> > /etc/hostname

\# `echo Arch > /etc/hostname`

edit host entries

\# `nano /etc/hosts`


add:

127.0.0.1	localhost

::1		localhost

127.0.1.1	\<hostname\>.localdomain	\<hostname\>


```
127.0.0.1   localhost
::1         localhost
127.0.1.1   Arch.localdomain    Arch
```


\# `nano /etc/mkinitcpio.conf`

add lvm2 at HOOKS between block and filesystems

\# `mkinitcpio -P`

if lts is installed
( mkinitcpio -p linux-lts )


# 15 set ROOT password and USERS

\# `passwd`

useradd -m -g users -G wheel \<username\>

\# `useradd -m -g users -G wheel fabo`

\# `passwd fabo`

sudoers

\# ( `pacman -S sudo` )

\# `EDITOR=vim visudo`

uncomment %wheel ALL...

# 16 BOOTMANAGER

### UPDATE PACMAN

NOTE: You must run `pacman-key --init` before first using pacman; the local

keyring can then be populated with the keys of all official Arch Linux

packagers with `pacman-key --populate archlinux`

in `/etc/pacman.conf` put `ParallelDownloads = 10` (or whatever number you want),
add `ILoveCandy` to pacman.conf

update & upgrade & mirrirs

\# `sudo pacman -Syyu`

basic update & upgrade

\# `sudo pacman -Syu`

### NETWORK MANAGER ( https://wiki.archlinux.org/title/NetworkManager#Usage )

\# `pacman -S networkmanager bluez openssh`

@extra bluez-utils network-manager-applet dialog wpa_supplicant wireless_tools netctl

(aur: wpa_supplicant_gui)

#### start/enable services

\# `systemctl enable sshd`

\# `systemctl enable NetworkManager.service`

\# `systemctl enable bluetooth.service`

## GRUB

https://wiki.archlinux.org/title/GRUB#UEFI_systems

\# `pacman -S grub efibootmgr grub-customizer`

\# `grub-install /dev/nvme0n1p1 --efi-directory=/boot --bootloader-id=arch-grub --recheck`

\# `cp /usr/share/locale/en\@quot/LC_MESSAGES/grub.mo /boot/grub/locale/en.mo`

\# `grub-mkconfig -o /boot/grub/grub.cfg`

optional EXIT & REBOOT

\# `exit`

\# `umount -a`

\# `reboot`

wifi connect after reboot into cli

\# `nmcli device wifi list`

\# `nmcli device wifi connect <SSID_or_BSSID> password <password>`

# 17 XORG GUI

https://wiki.archlinux.org/title/Xorg#Installation

\# `sudo pacman -S xorg`

@extra

\# `sudo pacman -S xorg-server xorg-apps`


# 18 VIDEO DRIVERS

sudo pacman -S xf86-video-\<DRIVERNAME es:amdgpu\>

\# `sudo pacman -S xf86-video-amdgpu`

\# ( `sudo pacman -S  pulseaudio ) 

@extra `alsa-utils alsa-plugins pulseaudio-alsa`

# 19 KDE
https://wiki.archlinux.org/title/KDE#Installation , https://wiki.archlinux.org/title/Wayland

\# `sudo pacman -S plasma-meta plasma-wayland-session wayland-protocols`

@extra `kde-applications`

# INSTALL USEFUL PACKAGES
`pacman -S`

`linux-headers git curl wget bash-completion konsole lshw usbutils neofetch  tmux firefox nm-connection-editor firewalld` and  `dnsmasq ark zip unzip p7zip dolphin kate kwrite kbackup kcalc kfind kmag knotes ktimer ktorrent kipi-plugins dragon gwenview spectacle okular kamoso sweeper kde-system-meta kcharselect markdownpart kdialog`

## PIPEWIRE AUDIO

@pipewire https://wiki.archlinux.org/title/PipeWire#Installation

\# `pacman -S pipewire pipewire-docs pipewire-pulse xdg-desktop-portal xdg-desktop-portal-kde`

@extra pipewire-alsa pipewire-jack
 
### PulseAudio clients

Install `pipewire-pulse`. It will replace `pulseaudio` and `pulseaudio-bluetooth`. 
Reboot, re-login or execute `systemctl start --user pipewire-pulse.service` to see the effect.

Normally, no further action is needed, as the user service pipewire-pulse.socket` should be enabled automatically by the package. 
To check if the replacement is working, run the following command and see the output:

$ `pactl info`

...
 
Server Name: PulseAudio (on PipeWire 0.3.32)
 
...

If PipeWire does not work correctly on system startup, validate that the Systemd/User services `pipewire-pulse.service`, `pipewire.service`, and `pipewire-media-session.service` are up and running. Keep in mind that `pipewire-pulse.service` and `pipewire-pulse.socket` have a `ConditionUser` against running as root.  

 
 
PulseAudio cannot be uninstalled because it is too tied in to KDE
but the systemd socket and service for PulseAudio can be disabled to shut it down

 
`systemctl --user mask pulseaudio.socket --now`
 
`systemctl --user disable pulseaudio.service --now`

and the pipewire socket and service can be enabled instead

 
`systemctl --user enable pipewire.socket --now`
 
`systemctl --user start pipewire.service`

pipewire is very new and still a beta release
I have no idea what diagnostics and tools are available in pipewire if it does not work, and it is unlikely any tools for PulseAudio will work

GUI https://gitlab.freedesktop.org/ryuukyu/helvum


\# `exit`

\# `umount -a`

\# `reboot`

## login into root

## wifi connect after reboot into cli

\# `nmcli device wifi list`

\# `nmcli device wifi connect <SSID_or_BSSID> password <password>`

# ENABLE WINDOW MANAGER TO LOG IN INTYO DE
\# `systemctl enable sddm`

### reboot

## KDE apps
`pacman -S`

for kde discover install `packagekit-qt5 fwupd discover`

extra for dolphin file exploirer plugins and file previews  https://wiki.archlinux.org/title/Dolphin
`dolphin-plugins kdegraphics-thumbnailers qt5-imageformats kimageformats ffmpegthumbs raw-thumbnailer taglib`

extras `python-pygments digikam filelight kcolorchooser kontrast skanlite kdeconnect kdenetwork-filesharing print-manager`



# ENJOY
