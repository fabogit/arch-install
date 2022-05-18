https://wiki.archlinux.org/title/Installation_guide

# 1 SET KEYBOARD LAYOUT

loadkeys \<kbrdlout ex: us,it\>

```
loadkeys us
```

# 2 CHECK NETWORK

`ip link` or `ip a`

```
ping -c 3 archlinux.org
```


# 3 CONNECT WIFI

`iwctl`

`device list`

`station <device> scan`

`station <device> get-networks`

`station <device> connect <SSID>`

`device <device> show`

`station <device> show`

-`exit`

...

### ENABLE INSTALL OVER SSH

- set root pwd

╰─`passwd`

╰─`nano /etc/ssh/sshd_config` 

Add `PermitRootLogin yes`

...

This setting allows root login with
password authentication on the SSH server.

Note: Unless required, after installation it is recommended
to remove `PermitRootLogin yes` from `/etc/ssh/sshd_config`

...

start the openssh daemon with 

```
systemctl start sshd.service
```

- get ip

╰─`ip a`

then ssh \# `ssh root@<ip addr>`

## synking clock

```
timedatectl set-ntp true
```

## rank mirrors

```
reflector --save /etc/pacman.d/mirrorlist --sort score --number 20
```

- sync mirrors

```
pacman -Syy
```

optionally update archinstall

```
pacman -S archinstall
```

# 4 DISK SETUP

## ERASE DRIVE

on `/dev/<DISK>`
```
sgdisk --zap-all /dev/nvme0n1
```

`Size: 953.87 GiB, 1024209543168 bytes, 2000409264 sectors`

### BFTRS

...

```
NAME                    SIZE        TYPE    MOUNTPOINTS FS      SECTORS
nvme0n1                 953.9G      disk    /dev        GPT     2000409264
├─nvme0n1p1             0.2G        part    /boot       f32     419840
├─nvme0n1p2             32G         part    [SWAP]      swap    367108864
├─nvme0n1p3             921.7G      part    /           btrfs   1932878479

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

https://wiki.archlinux.org/title/Btrfs#GRUB

https://wiki.manjaro.org/index.php/Btrfs

https://www.nishantnadkarni.tech/posts/arch_installation/

https://www.ordinatechnic.com/distribution-specific-guides/arch-linux/an-arch-linux-installation-on-a-btrfs-filesystem-with-snapper-for-system-snapshots-and-rollbacks

https://wiki.archlinux.org/title/User:Altercation/Bullet_Proof_Arch_Install#Partition_Drive


# 5 create partitions

on `/dev/DISK`
```
cfdisk /dev/nvme0n1
``` 

...

=> cfdisk `GPT`

`/dev/EFIpartition`	size: 0.2G	type: `EFI System`

`/dev/swap`	size: 32G	type: `Linux Swap`

`/dev/root`	size: ALL	type: `Linux FileSystem`

write & quit

...

# 6 format partitions

- make efi partition

on `/dev/EFI-PART`
```
mkfs.fat -F32 -n EFI /dev/nvme0n1p1
``` 

- swap partition

on `/dev/SWAP-PART`
```
mkswap -L SWAP /dev/nvme0n1p2
``` 
 
- system btrfs partition

on `/dev/BTRFS-PART`
```
mkfs.btrfs --force --label SYSTEM /dev/nvme0n1p3
``` 

- all in one comand

```
mkfs.fat -F32 -n EFI /dev/nvme0n1p1 &&
mkswap -L SWAP /dev/nvme0n1p2 &&
mkfs.btrfs --force --label SYSTEM /dev/nvme0n1p3
``` 

# 7 set btrfs options as variable

```
o=defaults,x-mount.mkdir
```

```
o_btrfs=$o,commit=60,compress=zstd,space_cache=v2,ssd,noatime
```

# 8 create subvolumes

https://en.opensuse.org/SDB:BTRFS

- subvolumes structure

```
MOUNT POINT       SUBVOLUME NAME    USED FOR      SNAPSHOTS
/                 /@                SYSTEM        ON /.snapshots
/home             /@home            USER HOME     ON /home/.snapshots
/var/cache        /@cache           PKGS CACHE    NO
/var/log          /@log             LOGS          NO 
/var/tmp          /@tmp             TMP           NO
```

### DATABASES 

create separate subvolumes

```
/var/lib/mongodb          /@mongodb       
/var/lib/mysql            /@mysql         
/var/lib/postgres         /@postgres    
```

and disable CoW before setup

```
sudo chattr +C /var/lib/mongodb &&
sudo chattr +C /var/lib/mysql &&
sudo chattr +C /var/lib/postgres
```

leave be `/var/lib/docker` https://forum.garudalinux.org/t/btrfs-docker-and-subvolumes/4601/25

- mount system

```
mount -t btrfs LABEL=SYSTEM /mnt
```

- create subvolumes

=> SYSTEM

```
btrfs subvolume create /mnt/@ &&
btrfs subvolume create /mnt/@home &&
btrfs subvolume create /mnt/@cache &&
btrfs subvolume create /mnt/@log &&
btrfs subvolume create /mnt/@tmp
```

=> DBS

```
btrfs subvolume create /mnt/@mongodb &&
btrfs subvolume create /mnt/@mysql &&
btrfs subvolume create /mnt/@postgres
```

- umount all

```
umount -R /mnt
```

# 9 mount partitions and btrfs @subvolumes

=> SYSTEM

```
mount -t btrfs -o subvol=@,$o_btrfs LABEL=SYSTEM /mnt &&
mount -t btrfs -o subvol=@home,$o_btrfs LABEL=SYSTEM /mnt/home &&
mount -t btrfs -o subvol=@cache,$o_btrfs LABEL=SYSTEM /mnt/var/cache &&
mount -t btrfs -o subvol=@log,$o_btrfs LABEL=SYSTEM /mnt/var/log &&
mount -t btrfs -o subvol=@tmp,$o_btrfs LABEL=SYSTEM /mnt/var/tmp
```

=> DBS

```
mount -t btrfs -o subvol=@mongodb,$o_btrfs LABEL=SYSTEM /mnt/var/lib/mongodb &&
mount -t btrfs -o subvol=@mysql,$o_btrfs LABEL=SYSTEM /mnt/var/lib/mysql &&
mount -t btrfs -o subvol=@postgres,$o_btrfs LABEL=SYSTEM /mnt/var/lib/postgres
```

# 10

- make and mount boot, set swap

```
mkdir /mnt/boot &&
mount LABEL=EFI /mnt/boot &&
swapon -L SWAP
```

# BTRFS & LVM FINAL CHECK

- verify all
```
df -hT
```

```
lsblk -f
```

# 11 START INSTALL USING PACSTRAP

```
pacstrap /mnt base base-devel linux linux-firmware amd-ucode nano
```

=> for BTRFS install add `btrfs-progs`

=> ford LVM install add `lvm2`

@extra: `linux-lts vim git`

vim controls:

...

```
i to enter insert mode,

ESC for command mode,

to save&quit ESC, :wq

to discard&quit ESC, :q!
```
...

- generate file system tabs

```
genfstab -U /mnt >> /mnt/etc/fstab
```

check => `more /mnt/etc/fstab`


# 12 ENTER INTO LINUX 

```
arch-chroot /mnt
```

# 13 TZ & LANG

- set timezone and sync clock

ln -sf /usr/share/zoneinfo/\<Region\>/\<Place\> /etc/localtime

```
ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime &&
hwclock --systohc
```

- select and generate locale

```
nano /etc/locale.gen
```

append `en_US.UTF-8 UTF-8`, s&q
 
-generate locale, set enUS language and keyboard layout

```
locale-gen &&
echo "LANG=en_US.UTF-8" > /etc/locale.conf &&
echo "KEYMAP=us" > /etc/vconsole.conf
```

# 14 CREATE HOSTNAME

echo \<hostname\> > /etc/hostname

```
echo Arch > /etc/hostname
```

- edit host entries

```
nano /etc/hosts
```

add blueprint:
```
127.0.0.1   localhost
::1         localhost
127.0.1.1   <hostname>.localdomain  <hostname>
```

like

```
127.0.0.1   localhost
::1         localhost
127.0.1.1   Arch.localdomain    Arch
```

# 15 SET UP ROOT PASSWORD AND ADD USER

- change root pass

`passwd`

- create user

useradd -m -g users -G wheel \<\$username\>

```
useradd -m -g users -G wheel <$USERNAME>
```

```
passwd <$USERNAME>
```

## add to sudoers

check `pacman -S sudo`

`EDITOR=nano visudo` or `EDITOR=vim visudo`

uncomment `%wheel ALL=(ALL:ALL) ALL`

check `id <$USERNAME>`


# UPDATE PACkage MANager

NOTE: You must run `pacman-key --init` before first using pacman;

the local keyring can then be populated with the keys of all official Arch Linux

packagers with `pacman-key --populate archlinux`

`nano /etc/pacman.conf` put `ParallelDownloads = 10` (or whatever number you want),
add `ILoveCandy` to options

to clean pkgs download chace install

`sudo pacman -S pacman-contrib`

run `paccache -r`

`systemctl enable paccache.timer`

to clean chache manually

`pacman -Sc`

to install pkgs: `pacman -S pkg-name` 

`Ss` to query pkgs dbs. `Si` info on pkgs `Qi` info on local installed pkgs

`Qdt` orphans `Qet` installed and not required as dependencies

`S` sync `y` refresh `u` update

`sudo pacman -Syu`

to uninstall:

`R` remove `sc` dependencies and pkgs depending on it `n` config files

GUI pamac https://wiki.manjaro.org/index.php/Pamac

# mkinitcpio.conf 

- => BTRFS

```
nano /etc/mkinitcpio.conf
```

add `btrfs` into `MODULES` between `()`, save & close

- recreate kernel image

```
mkinitcpio -P
```

- => LVM

```
nano /etc/mkinitcpio.conf
```

add `lvm2` at `HOOKS` between `block` and `filesystems`, save & close

- recreate kernel image

```
mkinitcpio -P
```

if lts is installed
( mkinitcpio -p linux-lts )

## NETWORK MANAGER ( https://wiki.archlinux.org/title/NetworkManager#Usage )

- network bluethoot ssh printer

```
pacman -S networkmanager bluez openssh cups
```

@extra `bluez-utils network-manager-applet dialog wpa_supplicant wireless_tools netctl`

(aur: `wpa_supplicant_gui`)

#### start/enable services

`systemctl enable sshd`

`systemctl enable NetworkManager.service`

`systemctl enable bluetooth.service`

`systemctl enable cups.service`

- all togheter

```
systemctl enable sshd &&
systemctl enable NetworkManager.service &&
systemctl enable bluetooth.service &&
systemctl enable cups.service
```

# 16 BOOTMANAGER INSTALL

## GRUB INSTALL

https://wiki.archlinux.org/title/GRUB#UEFI_systems

```
pacman -S grub efibootmgr grub-customizer
```

```
grub-install /dev/nvme0n1p1 --efi-directory=/boot --bootloader-id=arch-grub --recheck
```

```
cp /usr/share/locale/en\@quot/LC_MESSAGES/grub.mo /boot/grub/locale/en.mo &&
grub-mkconfig -o /boot/grub/grub.cfg
```

optional EXIT & REBOOT

`exit`

`umount -a`

`reboot`

### wifi connect after reboot into cli

```
nmcli device wifi list
```

```
nmcli device wifi connect <SSID_or_BSSID> password <password>
```

# 17 INSTALL XORG DISPLAY SERVER

https://wiki.archlinux.org/title/Xorg#Installation

`pacman -S`

```
xorg
```

@extra `xorg-server xorg-apps`


# 18 INSTALL VIDEO DRIVERS

sudo pacman -S xf86-video-\<DRIVERNAME es:amdgpu, intel\>

`pacman -S`

```
xf86-video-amdgpu
```

@extra `pulseaudio alsa-utils alsa-plugins pulseaudio-alsa`

# 19 INSTALL KDE
https://wiki.archlinux.org/title/KDE#Installation , https://wiki.archlinux.org/title/Wayland

`pacman -S`

from plasma-meta

```
bluedevil breeze-gtk drkonqi kde-gtk-config kdeplasma-addons kgamma5 khotkeys kinfocenter kscreen ksshaskpass kwallet-pam kwallet kwalletmanager knotifications kwrited oxygen plasma-browser-integration plasma-desktop plasma-disks plasma-firewall plasma-nm plasma-pa plasma-systemmonitor plasma-vault plasma-workspace-wallpapers powerdevil sddm-kcm kio kio-extras systemsettings
```

from plasma workspace

```
kactivities-stats kactivities-stats kactivitymanagerd kde-cli-tools kholidays kio-extras knotifyconfig kpeople kquickcharts ksystemstats ktexteditor kuserfeedback kwin libkscreen libqalculate milou plasma-integration prison xorg-xmessage xorg-xrdb xorg-xsetroot appmenu-gtk-module plasma-workspace-wallpapers kdepim-addons baloo extra-cmake-modules kdoctools kinit kunitconversion networkmanager-qt
```

wayland

```
plasma-wayland-protocols kwayland-integration plasma-wayland-session wayland-protocols
```

or `plasma-meta` pckg + wayland

@extra `kde-applications kde-graphics-meta plasma-thunderbolt gpsd lshw`

## INSTALL USEFUL PACKAGES

`pacman -S`

```
linux-headers git curl wget bash-completion konsole usbutils neofetch tmux firefox-developer-edition chromium nm-connection-editor dosfstools exfatprogs  firewalld kdf
```

and

```
kde-system-meta dnsmasq ark zip unzip p7zip dolphin kate kwrite kbackup kcalc kfind kmag knotes ktimer ktorrent dragon gwenview kamera spectacle okular digikam filelight kruler skanlite kontrast sweeper kcharselect markdownpart kdialog xdg-utils xdg-user-dirs kdeconnect sshfs print-manager kalendar vlc
``` 
in AUR repos `krecorder` option `audio-recorder` `kipi-plugins`

image editing `kcolorchooser kolourpaint krita inkscape gimp` video `kdenlive obs-studio` camera `plasma-camera kamoso`

Dolphin file exploirer plugins and file previews  https://wiki.archlinux.org/title/Dolphin
 
The following packages enable preview thumbnails in dolphin

- ffmpegthumbs: video thumbnails
- kdegraphics-thumbnailers: PDF and PS thumbnails
- qt5-imageformats: thumbnails for additional image formats
- kimageformats: thumbnails for additional image formats
- taglib: audio file thumbnails
- libappimage: AppImage thumbnails
- raw-thumbnailer: Raw image files from a camera

```
dolphin-plugins ffmpegthumbs kdegraphics-thumbnailers qt5-imageformats kimageformats taglib libappimage
```

not in repos  `raw-thumbnailer`

## PIPEWIRE AUDIO DRIVERS

@pipewire https://wiki.archlinux.org/title/PipeWire#Installation

`pacman -S`

```
pipewire pipewire-docs pipewire-pulse xdg-desktop-portal xdg-desktop-portal-kde
```

@extra `pipewire-alsa pipewire-jack`
 
### PulseAudio clients

Install `pipewire-pulse`. It will replace `pulseaudio` and `pulseaudio-bluetooth`. 
Reboot, re-login or execute `systemctl start --user pipewire-pulse.service` to see the effect.

Normally, no further action is needed, as the user service pipewire-pulse.socket` should be enabled automatically by the package. 
To check if the replacement is working, run the following command and see the output:

```
pactl info
```

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


- `exit`

- `umount -a`

- `reboot`

## login as user

## connect wifi from cli after reboot

```
nmcli device wifi list
```

```
nmcli device wifi connect <SSID_or_BSSID> password <password>
```
 

# YAY (after reboot as normal user)

https://github.com/Jguer/yay

```
sudo pacman -S git
```

```
git clone https://aur.archlinux.org/yay-git.git &&
cd yay-git/
```

```
makepkg -si
```

```
cd .. && sudo rm -r yay-git
```

#### First Use

Development packages upgrade

Use `yay -Y --gendb` to generate a development package database for *-git packages that were installed without yay. This command should only be run once.

`yay -Syu --devel` will then check for development package updates

Use `yay -Y --devel --save` to make development package updates permanently enabled (`yay` and `yay -Syu` will then always check dev packages)

...
 
# -> BTRFS configure snapper
  
https://wiki.archlinux.org/title/Snapper  
  
https://documentation.suse.com/sles/12-SP4/html/SLES-all/cha-snapper.html#sec-snapper-setup
  
https://www.jwillikers.com/btrfs-snapshot-management-with-snapper
 
check for existing subvolumes `sudo btrfs subvolume list /` (unmount and delete `.snapshots` subvol)

## IGNORE, OUTDATED, KEEP JUST FOR REFERENCE

(install `btrfs-assistant` then use the `SYNC_ACL` part after creating the config using the tool)

install btfs tool

```
yay -S grub-btrfs snap-pac snapper btrfs-assistant btrfsmaintenance
```

extra `snapper-gui-git`

### After installing with btrfs selected as the filesystem:

Open `Btrfs Assistant`

Switch to the “Snapper Settings” tab

Click on the “New Config” button

Name the config `root` and choose `/` as the mountpoint

Click the “Save Config” button

Set the retention limits you want. In particular you probably want to lower the amount of “Number” snapshots that are retained. These are the snapshots that are taken when pacman runs. It takes 2 snapshots in each run so something like 10 is probably a more reasonable number. That will give you 5 pacman runs. The timeline settings are entirely left to your preferences.

Select the checkboxes for `snapper-timeline` and `snapper-cleanup` and click the “Apply” button to the right of the checkboxes.

- Add support for booting off read-only snapshots

Edit `/etc/mkinitcpio.conf` and add `grub-btrfs-overlayfs` to the end of the `HOOKS` section

Rebuild your initrams with `sudo mkinitcpio -P`

Make sure the snapshots are added to the grub menu. There are two easy ways to do this. Only pick one of them:

Enable the `grub-btrfs.path` systemd unit

Install `snap-pac-grub` from AUR

### old, go to: install snap-pac-grub and GUI

- umount snapshots subvolumes

```
sudo umount /.snapshots
```

```
sudo umount /home/.snapshots
```

- remove folders

```
sudo rm -rf /.snapshots
```

```
sudo rm -rf /home/.snapshots
```

- create snapper config

`snapper -c <config-name> create-config /<snapped-dir>`

```
sudo snapper -c root create-config /
```

```
sudo snapper -c home create-config /home
```

- delete snapper autogenerated subvolume and implement user created subvol, use subvol id from `sudo btrfs subvolume list /`

```
sudo btrfs subvolume delete --subvolid IDNUMBER /.snapshots
```

for @home/.snapshots

```
sudo btrfs subvolume delete --subvolid IDNUMBER /home/.snapshots
```

- recreate dir

```
sudo mkdir /.snapshots
```

```
sudo mkdir /home/.snapshots
```

- and remount subvolume to directory (`sudo mount -o subvol=SNAPSUBVOLUME /dev/SYSTEMPART /.snapshots`)

```
sudo mount -o subvol=@snapshots /dev/nvme0n1p3 /.snapshots
```

```
sudo mount -o subvol=@snapshots-home /dev/nvme0n1p3 /home/.snapshots
```

- remount fstab

```
sudo mount -a
```

- give folder 750 permission (750 allow current user)

`sudo chmod 750 /.snapshots`

=> OR BETTER USE ACL

- check `ls -la /` if not already, set root as the owner

```
sudo chown root /.snapshots
```

```
sudo chown root /home/.snapshots
```

- edit config, use `ALLOW_USERS="USERNAME"` & `SYNC_ACL="yes"`

```
sudo nano /etc/snapper/configs/root
```

```
sudo nano /etc/snapper/configs/home
```

- Make the directory accessible (also `chown :wheel /.snapshots`)

if `SYNC_ACL="yes"` use:

```
sudo setfacl -m u:fabo:rx /.snapshots
```

```
sudo setfacl -m u:fabo:rx /home/.snapshots
```

-create snapshots

```
sudo snapper -c home create --description "First /@home"
```

```
sudo snapper -c root create --description "First /@"
```

- enable timeline and timeline cleanup

```
sudo systemctl enable --now snapper-timeline.timer
```

```
sudo systemctl enable --now snapper-cleanup.timer
```

```
sudo systemctl enable --now grub-btrfs.path
```

to show all snapshots `snapper list -a`, per config `snapper -c home list`


## install snap-pac-grub and GUI
 
```
yay -S snap-pac-grub
```

- configure hook for grub

```
sudo mkdir /etc/pacman.d/hooks
```
  
```
sudo nano /etc/pacman.d/hooks/50-bootbackup.hook
```
...

```
  
[Trigger]
 
Operation = Upgrade
 
Operation = Install
 
Operation = Remove
 
Type = Path
 
Target = boot/*
 
[Action]
 
Depends = rsync
 
Description = Backing up ==> /boot ...

When = PreTransaction

Exec = /usr/bin/rsync -a --delete /boot /.bootbackup

```
...

- optional install rsync

```
sudo pacman -S rsync
```
  
- edit permission, not necessary if using `SYNC_ACL="yes"`

```
sudo chmod a+rx /.snapshots
```
- allow users, not necessary if using `SYNC_ACL="yes"`

```
sudo chown <$USERNAME>:users /.snapshots
```
or `sudo chown :users /.snapshots`
...
  
DONE

## btrfs utils

- show snpshots
  
`snapper -c root list`  
  
- create snapshot
  
`snapper -c root create -c timeline -d AfterInstall`
  
- snpts property
  
`sudo btrfs property list -ts /.snapshots/<sn#: es 1,2,3..>/snapshot/` 
  
- set read only to false
  
`sudo btrfs property set -ts /.snapshots/<sn#: es 1,2,3..>/snapshot/ ro false` 

... 
 
# ENABLE DISPLAY MANAGER TO ENABLE SYSTEM GUI
 
```
sudo systemctl enable sddm
```
## REBOOT

login as `root` or user
 
## KDE discover
  
- for kde discover install
 
```
sudo pacman -S discover packagekit-qt5 fwupd
```

for flatpack b/end `flatpak`

extras `python-pygments`
  
for network folder sharing `samba kio-fuse kdenetwork-filesharing` https://wiki.archlinux.org/title/Samba#KDE

https://wiki.archlinux.org/title/NetworkManager#Sharing_internet_connection_over_Wi-Fi
  
https://wiki.archlinux.org/title/Android_tethering
  
https://wiki.archlinux.org/title/Software_access_point 

## if modified remove `PermitRootLogin yes` from `/etc/ssh/sshd_config`

# ENJOY

# UEFI/GPT EXT4 LVM

https://wiki.archlinux.org/title/Partitioning#Example_layouts

```
fdisk -l
```

cfdisk /dev/\<drive ex: nvme0n1\>

```
cfdisk /dev/nvme0n1
```

...

=> cfdisk `GPT`

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

