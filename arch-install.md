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

`/dev/EFIpartition`	size: 0.3G	type: `EFI System`

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

create separate subvolumes || skip and user db containers

```
/var/lib/mongodb          /@mongodb       
/var/lib/mysql            /@mysql         
/var/lib/postgres         /@postgres    
```

remember to disable CoW before installing db

```
sudo chattr +C /var/lib/mongodb &&
sudo chattr +C /var/lib/mysql &&
sudo chattr +C /var/lib/postgres
```

leave be `/var/lib/docker` https://forum.garudalinux.org/t/btrfs-docker-and-subvolumes/4601/25   

https://docs.docker.com/storage/storagedriver/btrfs-driver/

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

- generate file system tabs, `-U` to use UUIS `-L` to use labels

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


=> `updated to use qt ver 5 packages`

```
Replace baloo5 with extra/baloo? [Y/n] 
:: Replace breeze with extra/breeze5? [Y/n] 
:: Replace kuserfeedback5 with extra/kuserfeedback? [Y/n] 
:: Replace oxygen with extra/oxygen5? [Y/n] 
:: Replace plasma-integration with extra/plasma5-integration? [Y/n] 
:: Replace plasma-wayland-session with extra/plasma-workspace? [Y/n] 
```
qt6-multimedia-ffmpeg

KDE6 update:
```
extra/accounts-qml-module          0.7-4             0.7-6               0.04 MiB       0.07 MiB
extra/akonadi                      23.08.5-1         24.02.0-1           2.14 MiB       1.19 MiB
extra/akonadi-calendar             23.08.5-1         24.02.0-1           0.42 MiB       1.07 MiB
extra/akonadi-contacts             23.08.5-1         24.02.0-1           0.83 MiB       1.22 MiB
extra/akonadi-contacts5                              23.08.5-2           1.29 MiB       0.36 MiB
extra/akonadi-import-wizard        23.08.5-1         24.02.0-1           0.06 MiB       0.71 MiB
extra/akonadi-mime                 23.08.5-1         24.02.0-1           0.07 MiB       0.56 MiB
extra/akonadi-notes                23.08.5-1         24.02.0-1          -0.01 MiB       0.14 MiB
extra/akonadi-search               23.08.5-1         24.02.0-1           0.13 MiB       1.00 MiB
extra/appstream-qt                                   1.0.2-1             0.53 MiB       0.12 MiB
extra/archlinux-appstream-data     20240112-1        20240306-1          0.42 MiB      18.93 MiB
extra/ark                          23.08.5-1         24.02.0-1          -0.02 MiB       1.40 MiB
extra/attica                                         6.0.0-1             1.73 MiB       0.73 MiB
extra/baloo                                          6.0.0-3             2.44 MiB       0.64 MiB
extra/baloo-widgets                23.08.5-1         24.02.0-1           0.06 MiB       0.14 MiB
baloo5                             5.115.0-1                            -2.26 MiB               
extra/bitwarden                    2024.2.0-1        2024.2.1-1          4.22 MiB       6.65 MiB
extra/bluedevil                    1:5.27.10-3       1:6.0.1-1           0.09 MiB       0.51 MiB
extra/bluez                        5.72-2            5.73-3             -0.09 MiB       0.54 MiB
extra/bluez-libs                   5.72-2            5.73-3             -0.01 MiB       0.09 MiB
extra/bluez-qt                                       6.0.0-1             2.43 MiB       1.03 MiB
extra/breeze                       5.27.10-1         6.0.1-5             2.60 MiB      50.52 MiB
breeze                             5.27.10-1                           -76.65 MiB               
extra/breeze-gtk                   5.27.10-1         6.0.1.1-1           0.00 MiB       0.20 MiB
extra/breeze-icons                 5.115.0-1         6.0.0-1             0.43 MiB       6.09 MiB
extra/breeze5                                        6.0.1-5             0.50 MiB       0.17 MiB
extra/cairo                        1.18.0-1          1.18.0-2           -0.04 MiB       0.59 MiB
extra/calendarsupport              23.08.5-1         24.02.0-1           0.07 MiB       0.84 MiB
extra/chromium                     122.0.6261.94-1   122.0.6261.111-1    0.00 MiB      98.03 MiB
extra/clinfo                       3.0.21.02.21-1    3.0.23.01.25-1     -0.01 MiB       0.05 MiB
core/cryptsetup                    2.7.0-3           2.7.1-1             0.01 MiB       0.73 MiB
extra/digikam                      8.2.0-2           8.2.0-3            -0.66 MiB      25.77 MiB
extra/discover                     5.27.10.1-1       6.0.1-1             0.97 MiB       1.22 MiB
extra/docker-compose               2.24.6-1          2.24.7-1            0.03 MiB      12.73 MiB
extra/dolphin                      23.08.5-1         24.02.0-2           0.51 MiB       4.51 MiB
extra/dolphin-plugins              23.08.5-1         24.02.0-1           0.27 MiB       0.46 MiB
extra/dragon                       23.08.5-1         24.02.0-1           0.07 MiB       1.71 MiB
extra/drkonqi                      5.27.10-1         6.0.1-1             0.10 MiB       0.62 MiB
extra/electron27                   27.3.4-4          27.3.5-1            0.00 MiB      62.95 MiB
extra/elisa                        23.08.5-1         24.02.0-1           0.41 MiB       2.00 MiB
extra/eventviews                   23.08.5-1         24.02.0-1           0.41 MiB       1.25 MiB
extra/extra-cmake-modules          5.115.0-1         6.0.0-1            -0.21 MiB       0.30 MiB
core/fakeroot                      1.33-2            1.34-1             -0.01 MiB       0.07 MiB
extra/ffmpegthumbs                 23.08.5-1         24.02.0-1           0.00 MiB       0.03 MiB
extra/filelight                    23.08.5-1         24.02.0-1           0.06 MiB       0.76 MiB
extra/firefox-developer-edition    124.0b7-1         124.0b9-1          -0.50 MiB      68.00 MiB
extra/frameworkintegration                           6.0.0-1             0.24 MiB       0.07 MiB
extra/futuresql-qt6                                  0.1.1-2             0.07 MiB       0.02 MiB
extra/ghostscript                  10.02.1-1         10.03.0-1          -0.51 MiB      19.58 MiB
extra/go                           2:1.22.0-1        2:1.22.1-1          0.01 MiB      38.69 MiB
extra/grantleetheme                23.08.5-1         24.02.0-1           0.02 MiB       0.19 MiB
extra/grantleetheme5                                 23.08.5-2           0.16 MiB       0.05 MiB
extra/gst-plugins-base             1.22.10-1         1.24.0-1            0.00 MiB       0.31 MiB
extra/gst-plugins-base-libs        1.22.10-1         1.24.0-1            0.43 MiB       2.24 MiB
extra/gstreamer                    1.22.10-1         1.24.0-1            1.70 MiB       2.24 MiB
extra/gwenview                     23.08.5-1         24.02.0-3           0.34 MiB       6.91 MiB
extra/incidenceeditor              23.08.5-1         24.02.0-1           0.16 MiB       0.77 MiB
extra/kaccounts-integration        23.08.5-1         24.02.0-1           0.03 MiB       0.14 MiB
extra/kactivitymanagerd            5.27.10-1         6.0.1-1             0.07 MiB       0.20 MiB
extra/karchive                                       6.0.0-1             1.06 MiB       0.41 MiB
extra/kate                         23.08.5-1         24.02.0-3           2.73 MiB      10.09 MiB
extra/kauth                                          6.0.0-2             0.71 MiB       0.29 MiB
extra/kbackup                      23.08.5-1         24.02.0-1           0.10 MiB       0.53 MiB
extra/kbookmarks                                     6.0.0-1             1.07 MiB       0.42 MiB
extra/kcalc                        23.08.5-1         24.02.0-1           0.08 MiB       0.67 MiB
extra/kcalendarcore                                  6.0.0-1             3.42 MiB       1.38 MiB
extra/kcalutils                    23.08.5-1         24.02.0-1           0.06 MiB       0.46 MiB
extra/kcharselect                  23.08.5-1         24.02.0-1           0.01 MiB       0.41 MiB
extra/kcmutils                                       6.0.0-2             1.39 MiB       0.48 MiB
extra/kcodecs                                        6.0.0-1             1.00 MiB       0.34 MiB
extra/kcolorpicker                                   0.3.1-4             0.08 MiB       0.03 MiB
extra/kcolorpicker-qt5             0.3.0-3           0.3.1-4             0.00 MiB       0.02 MiB
extra/kcolorscheme                                   6.0.0-1             0.42 MiB       0.20 MiB
extra/kcompletion                                    6.0.0-1             1.07 MiB       0.59 MiB
extra/kconfig                                        6.0.0-1             3.11 MiB       1.22 MiB
extra/kconfigwidgets                                 6.0.0-1             1.97 MiB       0.76 MiB
extra/kcontacts                                      1:6.0.0-1           2.08 MiB       0.79 MiB
extra/kcoreaddons                                    6.0.0-1             3.15 MiB       1.23 MiB
extra/kcrash                                         6.0.0-1             0.23 MiB       0.12 MiB
extra/kcron                        23.08.5-1         24.02.0-1           0.03 MiB       0.99 MiB
extra/kdav                                           1:6.0.0-1           1.02 MiB       0.49 MiB
extra/kdbusaddons                                    6.0.0-1             0.44 MiB       0.20 MiB
extra/kde-cli-tools                5.27.10-1         6.0.1-1            -0.65 MiB       0.86 MiB
extra/kde-gtk-config               5.27.10-1         6.0.1-1             0.01 MiB       0.08 MiB
extra/kde-inotify-survey           23.08.5-1         24.02.0-1           0.00 MiB       0.05 MiB
extra/kde-system-meta              23.08-1           24.02-2             0.00 MiB       0.00 MiB
extra/kdeclarative                                   6.0.0-1             0.82 MiB       0.27 MiB
extra/kdeconnect                   23.08.5-1         24.02.0-2           1.09 MiB       1.27 MiB
extra/kdecoration                  5.27.10-1         6.0.1-1             0.03 MiB       0.08 MiB
extra/kded                                           6.0.0-1             0.11 MiB       0.05 MiB
extra/kdegraphics-mobipocket       23.08.5-1         24.02.0-1           0.00 MiB       0.02 MiB
extra/kdegraphics-thumbnailers     23.08.5-1         24.02.0-1           0.01 MiB       0.04 MiB
extra/kdepim-addons                23.08.5-1         24.02.0-1          14.81 MiB       4.55 MiB
extra/kdepim-runtime               23.08.5-1         24.02.0-1           0.77 MiB       3.21 MiB
extra/kdeplasma-addons             5.27.10-2         6.0.1-1             0.29 MiB       1.16 MiB
extra/kdesu                                          6.0.0-1             0.51 MiB       0.23 MiB
extra/kdf                          23.08.5-1         24.02.0-1           0.00 MiB       0.62 MiB
extra/kdiagram                                       3.0.1-3             6.10 MiB       3.02 MiB
extra/kdialog                      23.08.5-1         24.02.0-1           0.02 MiB       0.15 MiB
extra/kdnssd                                         6.0.0-1             0.62 MiB       0.31 MiB
extra/kdoctools                                      6.0.0-1             2.51 MiB       0.56 MiB
extra/kdsoap-qt6                                     2.2.0-1             1.28 MiB       0.45 MiB
extra/kdsoap-ws-discovery-client                     0.4.0-1             0.90 MiB       0.29 MiB
extra/kfilemetadata                                  6.0.0-2             1.52 MiB       0.42 MiB
extra/kfind                        23.08.5-1         24.02.0-1          -0.12 MiB       0.42 MiB
extra/kgamma                       5.27.10-2         6.0.1-1            -0.08 MiB       0.15 MiB
extra/kglobalaccel                                   6.0.0-1             0.48 MiB       0.21 MiB
extra/kglobalaccel5                5.115.0-1         5.115.0-3          -0.06 MiB       0.25 MiB
extra/kglobalacceld                                  6.0.1-1             0.29 MiB       0.09 MiB
extra/kguiaddons                                     6.0.0-2             0.80 MiB       0.37 MiB
extra/kguiaddons5                  5.115.0-1         5.115.0-2          -0.05 MiB       0.33 MiB
extra/khelpcenter                  23.08.5-1         24.02.0-1          -9.90 MiB       3.60 MiB
extra/kholidays                                      1:6.0.0-1           1.15 MiB       0.41 MiB
extra/ki18n                                          6.0.0-1            17.73 MiB       1.96 MiB
extra/kiconthemes                                    6.0.0-1             1.21 MiB       0.53 MiB
extra/kidentitymanagement          23.08.5-1         24.02.0-1           0.54 MiB       0.48 MiB
extra/kidletime                                      6.0.0-1             0.38 MiB       0.16 MiB
extra/kimageannotator                                0.7.1-2             1.64 MiB       0.39 MiB
extra/kimageannotator-qt5          0.7.0-3           0.7.1-2             0.00 MiB       0.36 MiB
extra/kimap                        23.08.5-1         24.02.0-1           0.13 MiB       0.64 MiB
extra/kinfocenter                  5.27.10-1         6.0.1-1            -0.77 MiB       0.93 MiB
extra/kio                                            6.0.0-2            22.02 MiB       6.30 MiB
extra/kio-admin                    23.08.5-1         24.02.0-1           0.02 MiB       0.07 MiB
extra/kio-extras                   23.08.5-1         24.02.0-1           2.51 MiB       1.90 MiB
extra/kio-fuse                     5.1.0-1           5.1.0-3             0.00 MiB       0.07 MiB
extra/kio5                         5.115.0-1         5.115.0-3          -0.12 MiB       8.08 MiB
extra/kirigami                                       6.0.0-2             4.20 MiB       1.10 MiB
extra/kirigami-addons                                1.0.1-1             2.49 MiB       0.48 MiB
extra/kitemmodels                                    6.0.0-1             1.05 MiB       0.58 MiB
extra/kitemviews                                     6.0.0-1             0.88 MiB       0.47 MiB
extra/kitinerary                   23.08.5-1         24.02.0-1           1.41 MiB       2.40 MiB
extra/kjobwidgets                                    6.0.0-1             0.78 MiB       0.32 MiB
extra/kjournald                    23.08.5-1         24.02.0-1           0.09 MiB       0.16 MiB
extra/kldap                        23.08.5-1         24.02.0-1           0.26 MiB       0.63 MiB
extra/kmag                         23.08.5-1         24.02.0-1           0.02 MiB       0.80 MiB
extra/kmailtransport               23.08.5-1         24.02.0-1           0.09 MiB       0.49 MiB
extra/kmbox                        23.08.5-1         24.02.0-1           0.00 MiB       0.14 MiB
extra/kmenuedit                    5.27.10-1         6.0.1-1            -0.03 MiB       1.05 MiB
extra/kmime                        23.08.5-1         24.02.0-1          -0.01 MiB       0.27 MiB
extra/kmime5                                         23.08.5-2           0.62 MiB       0.23 MiB
core/kmod                          31-1              32-1                0.00 MiB       0.12 MiB
extra/knewstuff                                      6.0.0-3             3.18 MiB       0.93 MiB
extra/knotes                       23.08.5-1         24.02.0-1           0.12 MiB       0.69 MiB
extra/knotifications                                 6.0.0-1             0.65 MiB       0.29 MiB
extra/knotifyconfig                                  6.0.0-1             0.38 MiB       0.18 MiB
extra/kompare                      23.08.5-1         24.02.0-1           0.00 MiB       0.89 MiB
extra/konsole                      23.08.5-1         24.02.0-1           0.64 MiB       1.97 MiB
extra/kontactinterface             23.08.5-1         24.02.0-1           0.06 MiB       0.27 MiB
extra/kontrast                     23.08.5-1         24.02.0-1           0.03 MiB       0.18 MiB
extra/kpackage                                       6.0.0-1             0.91 MiB       0.33 MiB
extra/kparts                                         6.0.0-1             1.14 MiB       0.57 MiB
extra/kpeople                                        6.0.0-1             0.99 MiB       0.43 MiB
extra/kpimtextedit                 23.08.5-1         24.02.0-1          -0.59 MiB       0.45 MiB
extra/kpipewire                    5.27.10-1         6.0.1.1-1           0.13 MiB       0.12 MiB
extra/kpkpass                      23.08.5-1         24.02.0-1           0.05 MiB       0.20 MiB
extra/kpmcore                      23.08.5-1         24.02.0-1           0.10 MiB       0.69 MiB
extra/kpty                                           6.0.0-1             0.40 MiB       0.21 MiB
extra/kquickcharts                                   6.0.0-1             0.60 MiB       0.17 MiB
extra/kruler                       23.08.5-1         24.02.0-1           0.01 MiB       0.29 MiB
extra/krunner                                        6.0.0-1             0.78 MiB       0.40 MiB
extra/ksanecore                    23.08.5-1         24.02.0-1           0.03 MiB       0.09 MiB
extra/ksanecore5                                     24.02.0-1           0.18 MiB       0.06 MiB
extra/kscreen                      5.27.10-1         6.0.1-1             0.06 MiB       0.29 MiB
extra/kscreenlocker                5.27.10-1         6.0.1-1             0.11 MiB       0.23 MiB
extra/kservice                                       6.0.0-1             0.94 MiB       0.41 MiB
extra/ksmtp                        23.08.5-1         24.02.0-1           0.02 MiB       0.20 MiB
extra/ksshaskpass                  5.27.10-1         6.0.1-1             0.01 MiB       0.03 MiB
extra/kstatusnotifieritem                            6.0.0-2             0.56 MiB       0.24 MiB
extra/ksvg                                           6.0.0-1             0.75 MiB       0.33 MiB
extra/ksystemlog                   23.08.5-1         24.02.0-1           0.15 MiB       2.14 MiB
extra/ksystemstats                 5.27.10-1         6.0.1-1             0.16 MiB       0.23 MiB
extra/ktextaddons                  1.5.3-1           1.5.3-4             0.20 MiB       1.22 MiB
extra/ktexteditor                                    6.0.0-2            14.26 MiB       3.54 MiB
extra/ktexttemplate                                  6.0.0-1             2.46 MiB       1.35 MiB
extra/ktextwidgets                                   6.0.0-1             2.09 MiB       0.80 MiB
extra/ktimer                       23.08.5-1         24.02.0-1           0.02 MiB       0.45 MiB
extra/ktnef                        23.08.5-1         24.02.0-1           0.00 MiB       0.33 MiB
extra/ktorrent                     23.08.5-1         24.02.0-1           0.21 MiB       2.68 MiB
extra/kunitconversion                                6.0.0-1            10.97 MiB       1.06 MiB
extra/kuserfeedback                                  6.0.0-2             2.50 MiB       0.51 MiB
kuserfeedback5                     1.3.0-4                              -2.31 MiB               
extra/kwallet                                        6.0.0-3             2.47 MiB       0.60 MiB
extra/kwallet-pam                  5.27.10-1         6.0.1-1             0.00 MiB       0.01 MiB
extra/kwallet5                     5.115.0-1         5.115.0-2          -0.06 MiB       0.56 MiB
extra/kwalletmanager               23.08.5-1         24.02.0-1           0.03 MiB       1.00 MiB
extra/kwayland                                       6.0.1-1             3.37 MiB       1.50 MiB
extra/kwayland-integration         5.27.10-1         6.0.1-1             0.03 MiB       0.04 MiB
extra/kwidgetsaddons                                 6.0.0-1             9.24 MiB       4.73 MiB
extra/kwin                         5.27.10-2         6.0.1-1             2.47 MiB      10.38 MiB
extra/kwindowsystem                                  6.0.0-1             1.76 MiB       0.79 MiB
extra/kxmlgui                                        6.0.0-1             4.24 MiB       1.59 MiB
extra/layer-shell-qt               5.27.10-1         6.0.1-1             0.04 MiB       0.03 MiB
extra/libaccounts-qt               1.16-3            1.16-5              0.04 MiB       0.06 MiB
extra/libakonadi                   23.08.5-1         24.02.0-1           1.33 MiB       4.18 MiB
extra/libakonadi5                                    23.08.5-2           4.64 MiB       1.23 MiB
extra/libdisplay-info                                0.1.1-3             0.33 MiB       0.10 MiB
extra/libfabric                    1.20.0-1          1.20.1-1           -0.18 MiB       1.32 MiB
extra/libgravatar                  23.08.5-1         24.02.0-1           0.00 MiB       0.13 MiB
extra/libid3tag                    0.15.1b-12        0.16.3-2           -0.03 MiB       0.04 MiB
extra/libjxl                       0.10.1-1          0.10.2-1            0.00 MiB       1.77 MiB
extra/libkdcraw                                      24.02.0-1           0.13 MiB       0.04 MiB
extra/libkdcraw5                   23.08.5-1         24.02.0-1           0.00 MiB       0.04 MiB
extra/libkdepim                    23.08.5-1         24.02.0-1           0.16 MiB       0.44 MiB
extra/libkexiv2                    23.08.5-1         24.02.0-1           0.03 MiB       0.14 MiB
extra/libkgapi                     23.08.5-1         24.02.0-1           0.19 MiB       2.14 MiB
extra/libkleo                      23.08.5-1         24.02.0-1           0.31 MiB       1.31 MiB
extra/libkomparediff2              23.08.5-1         24.02.0-1           0.00 MiB       0.11 MiB
extra/libksane                     23.08.5-1         24.02.0-1          -0.03 MiB       0.16 MiB
extra/libkscreen                   5.27.10-1         6.0.1-1             0.06 MiB       0.41 MiB
extra/libksieve                    23.08.5-1         24.02.0-1           0.82 MiB       1.30 MiB
extra/libksysguard                 5.27.10-1         6.0.1-1            -4.44 MiB       0.55 MiB
extra/libktorrent                  23.08.5-1         24.02.0-1           0.17 MiB       0.75 MiB
extra/libmaxminddb                                   1.9.1-1             0.04 MiB       0.02 MiB
extra/libnewt                      0.52.23-2         0.52.24-1           0.00 MiB       0.09 MiB
extra/libpackagekit-glib           1.2.8-2           1.2.8-4             0.00 MiB       0.21 MiB
extra/libplasma                                      6.0.1-1             6.26 MiB       2.93 MiB
extra/libplist                     2.3.0-2           2.4.0-1             0.07 MiB       0.16 MiB
extra/libqaccessibilityclient-qt6                    0.6.0-1             0.32 MiB       0.10 MiB
extra/libreoffice-fresh            24.2.0-2          24.2.1-2          -21.14 MiB     147.36 MiB
core/linux                         6.7.8.arch1-1     6.7.9.arch1-1      -0.04 MiB     130.85 MiB
core/linux-headers                 6.7.8.arch1-1     6.7.9.arch1-1       0.00 MiB      25.33 MiB
extra/llvm-libs                    16.0.6-1          17.0.6-2           -3.04 MiB      31.61 MiB
extra/lsof                         4.99.0-1          4.99.3-1            0.00 MiB       0.14 MiB
extra/mailcommon                   23.08.5-1         24.02.0-1           0.53 MiB       1.67 MiB
extra/mailimporter                 23.08.5-1         24.02.0-1           0.07 MiB       0.55 MiB
extra/marble-common                23.08.5-1         24.02.0-2           0.39 MiB      45.49 MiB
extra/markdownpart                 23.08.5-1         24.02.0-1           0.00 MiB       0.04 MiB
extra/mesa                         1:24.0.2-1        1:24.0.2-2          0.01 MiB      18.44 MiB
extra/messagelib                   23.08.5-1         24.02.0-1           1.34 MiB       9.29 MiB
extra/milou                        5.27.10-1         6.0.1-1            -0.01 MiB       0.08 MiB
extra/modemmanager-qt                                6.0.0-1             1.47 MiB       0.59 MiB
extra/networkmanager-qt                              6.0.0-1             3.87 MiB       1.74 MiB
extra/nodejs                       21.6.2-1          21.7.0-1           -1.07 MiB      11.99 MiB
extra/ocean-sound-theme                              6.0.1-1             1.17 MiB       1.05 MiB
extra/okular                       23.08.5-1         24.02.0-2           0.69 MiB       7.27 MiB
extra/openexr                      3.2.2-1           3.2.3-1             0.03 MiB       1.21 MiB
extra/oxygen                       5.27.10-1         6.0.1-4             0.17 MiB       2.96 MiB
oxygen                             5.27.10-1                           -17.76 MiB               
extra/oxygen-sounds                5.27.10-1         6.0.1-1             0.05 MiB       1.85 MiB
extra/oxygen5                                        6.0.1-4             1.02 MiB       0.29 MiB
extra/packagekit                   1.2.8-2           1.2.8-4             0.00 MiB       0.52 MiB
extra/pacman-contrib               1.10.4-1          1.10.4-3            0.00 MiB       0.05 MiB
extra/pango                        1:1.52.0-1        1:1.52.1-1          0.00 MiB       0.39 MiB
extra/partitionmanager             23.08.5-1         24.02.0-1           0.94 MiB       2.20 MiB
extra/phonon-qt5                   4.12.0-3          4.12.0-4           -0.50 MiB       0.23 MiB
extra/phonon-qt6                                     4.12.0-4            1.65 MiB       0.41 MiB
extra/phonon-qt6-vlc                                 0.12.0-2            0.32 MiB       0.11 MiB
extra/pimcommon                    23.08.5-1         24.02.0-1           0.62 MiB       1.32 MiB
extra/plasma-activities                              6.0.1-1             0.73 MiB       0.30 MiB
extra/plasma-activities-stats                        6.0.1-1             0.61 MiB       0.29 MiB
extra/plasma-browser-integration   5.27.10-1         6.0.1-1             0.06 MiB       0.15 MiB
extra/plasma-desktop               5.27.10-1         6.0.1-1            -0.75 MiB      15.85 MiB
extra/plasma-disks                 5.27.10-1         6.0.1-1             0.11 MiB       0.14 MiB
extra/plasma-firewall              5.27.10-1         6.0.1-1             0.07 MiB       0.47 MiB
extra/plasma-framework5            5.115.0-1         5.115.0-3          -3.65 MiB       1.80 MiB
extra/plasma-integration           5.27.10-1         6.0.1-4            -0.07 MiB       0.14 MiB
plasma-integration                 5.27.10-1                            -0.54 MiB               
extra/plasma-nm                    5.27.10-1         6.0.1-1             0.73 MiB       1.50 MiB
extra/plasma-pa                    5.27.10-1         6.0.1-1             0.08 MiB       0.28 MiB
extra/plasma-systemmonitor         5.27.10-1         6.0.1-1             0.74 MiB       0.39 MiB
extra/plasma-vault                 5.27.10-1         6.0.1-1             0.08 MiB       0.33 MiB
plasma-wayland-session             5.27.10-2                             0.00 MiB               
extra/plasma-workspace             5.27.10-2         6.0.1-1             2.60 MiB      20.43 MiB
extra/plasma-workspace-wallpapers  5.27.10-1         6.0.1-1            15.32 MiB     104.96 MiB
extra/plasma5-integration                            6.0.1-4             0.38 MiB       0.12 MiB
extra/plasma5support                                 6.0.1-1             0.75 MiB       0.31 MiB
extra/polkit-kde-agent             5.27.10-1         6.0.1-1            -0.04 MiB       0.07 MiB
extra/polkit-qt6                                     0.200.0-1           0.35 MiB       0.09 MiB
extra/poppler-qt6                                    24.01.0-1           0.70 MiB       0.21 MiB
extra/powerdevil                   5.27.10-2         6.0.1-1            -0.35 MiB       0.88 MiB
extra/print-manager                23.08.5-1         1:6.0.1-1           0.15 MiB       0.52 MiB
extra/prison                                         6.0.0-1             0.65 MiB       0.23 MiB
core/psmisc                        23.6-1            23.7-1              0.05 MiB       0.25 MiB
extra/pulseaudio-qt                1.4.0-1           1.4.0-3             0.10 MiB       0.29 MiB
extra/purpose                                        6.0.0-1             1.56 MiB       0.35 MiB
extra/purpose5                     5.115.0-1         5.115.0-3          -0.10 MiB       0.32 MiB
extra/python-pygdbmi                                 0.11.0.0-3          0.15 MiB       0.04 MiB
extra/python-sentry_sdk                              1.40.6-1            2.93 MiB       0.46 MiB
extra/qca-qt6                                        2.3.8-2             3.31 MiB       0.84 MiB
extra/qcoro-qt6                                      0.10.0-1            0.65 MiB       0.13 MiB
core/qgpgme-qt6                                      1.23.2-1            1.15 MiB       0.27 MiB
extra/qqc2-breeze-style                              6.0.1-1             2.13 MiB       0.36 MiB
extra/qqc2-desktop-style                             6.0.0-1             1.89 MiB       0.35 MiB
extra/qt5-tools                    5.15.12+kde+r4-1  5.15.12+kde+r4-2   -0.35 MiB       5.29 MiB
extra/qt6-5compat                                    6.6.2-1             1.61 MiB       0.44 MiB
extra/qt6-declarative                                6.6.2-1            81.56 MiB      12.10 MiB
extra/qt6-multimedia                                 6.6.2-1             4.77 MiB       0.92 MiB
extra/qt6-multimedia-ffmpeg                          6.6.2-1             0.47 MiB       0.17 MiB
extra/qt6-networkauth                                6.6.2-1             0.30 MiB       0.08 MiB
extra/qt6-positioning                                6.6.2-1             1.59 MiB       0.36 MiB
extra/qt6-sensors                                    6.6.2-1             1.05 MiB       0.18 MiB
extra/qt6-shadertools                                6.6.2-1             3.88 MiB       1.33 MiB
extra/qt6-speech                                     6.6.2-1             0.50 MiB       0.12 MiB
extra/qt6-tools                                      6.6.2-2            18.27 MiB       5.96 MiB
extra/qt6-virtualkeyboard                            6.6.2-2             5.43 MiB       2.38 MiB
extra/qt6-wayland                                    6.6.2-1             6.90 MiB       1.09 MiB
extra/qt6-webchannel                                 6.6.2-1             0.41 MiB       0.12 MiB
extra/qt6-webengine                                  6.6.2-1           196.43 MiB      64.89 MiB
extra/qt6-websockets                                 6.6.2-1             0.35 MiB       0.10 MiB
extra/qt6-webview                                    6.6.2-1             0.39 MiB       0.08 MiB
extra/qtkeychain-qt6                                 0.14.2-1            0.24 MiB       0.07 MiB
extra/sddm                         0.20.0-4          0.21.0-4            0.75 MiB       3.54 MiB
extra/sddm-kcm                     5.27.10-1         6.0.1-1             0.03 MiB       0.13 MiB
extra/sdl2                         2.30.0-1          2.30.1-1           -0.09 MiB       0.97 MiB
extra/signon-kwallet-extension     23.08.5-1         24.02.0-1           0.00 MiB       0.01 MiB
extra/signon-plugin-oauth2         0.25-1            0.25-3              0.01 MiB       0.08 MiB
extra/signon-ui                    0.17+20171022-3   0.17+20231016-2     0.04 MiB       0.09 MiB
extra/signond                      8.61-1            8.61-3              0.16 MiB       0.36 MiB
extra/skanlite                     23.08.5-1         24.02.0-1           0.00 MiB       2.43 MiB
extra/socat                        1.7.4.4-1         1.8.0.0-1           0.01 MiB       0.20 MiB
extra/solid                                          6.0.0-1             2.61 MiB       0.87 MiB
extra/sonnet                                         6.0.0-1             2.15 MiB       0.67 MiB
extra/spectacle                    23.08.5-1         24.02.0-2           1.25 MiB       1.73 MiB
extra/sweeper                      23.08.5-1         24.02.0-1           0.00 MiB       0.41 MiB
extra/syndication                                    6.0.0-1             1.45 MiB       0.65 MiB
extra/syntax-highlighting                            6.0.0-2            10.27 MiB       1.51 MiB
extra/syntax-highlighting5         5.115.0-1         5.115.0-2          -8.51 MiB       0.51 MiB
extra/systemsettings               5.27.10-1         6.0.1-1            -0.06 MiB       0.36 MiB
extra/threadweaver                                   6.0.0-1             0.86 MiB       0.45 MiB
extra/xdg-desktop-portal-kde       5.27.10-1         6.0.1-1             0.31 MiB       0.37 MiB
extra/xsettingsd                                     1.0.2-1             0.08 MiB       0.03 MiB
```


`pacman -S`

from plasma-meta

```
bluedevil breeze-gtk drkonqi kde-gtk-config kdeplasma-addons kgamma khotkeys kinfocenter kscreen ksshaskpass kwallet-pam kwallet5 kwalletmanager knotifications5 oxygen plasma-browser-integration plasma-desktop plasma-disks plasma-firewall plasma-nm plasma-pa plasma-systemmonitor plasma-vault plasma-workspace-wallpapers powerdevil acpi sddm-kcm kio5 kio-extras systemsettings
```

from plasma workspace

```
kactivities-stats5 kactivitymanagerd kde-cli-tools kholidays5 knotifyconfig5 kpeople5 kquickcharts5 ksystemstats ktexteditor5 kuserfeedback5 kwin libkscreen libqalculate milou plasma-integration prison5 xorg-xmessage xorg-xrdb xorg-xsetroot appmenu-gtk-module plasma-workspace-wallpapers kdepim-addons baloo5 extra-cmake-modules kdoctools5 kinit kunitconversion5 networkmanager-qt5
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
kde-system-meta dnsmasq ark zip unzip p7zip dolphin kate kbackup kcalc kfind kmag knotes ktimer ktorrent dragon elisa gwenview spectacle okular digikam filelight kruler skanlite kontrast sweeper kcharselect markdownpart kdialog xdg-utils xdg-user-dirs kdeconnect sshfs print-manager kalendar kompare vlc
``` 
in AUR repos `krecorder` option `audio-recorder` `kipi-plugins`

image editing `kcolorchooser kolourpaint krita inkscape gimp` video `kdenlive obs-studio` camera `kamera plasma-camera kamoso`

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
sudo pacman -S --needed git base-devel
```

```
git clone https://aur.archlinux.org/yay.git &&
cd yay-git/
```

```
makepkg -si
```

```
cd .. && sudo rm -r yay
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
yay -S snapper grub-btrfs snap-pac snap-pac-grub btrfs-assistant btrfsmaintenance
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

https://forum.garudalinux.org/t/is-there-a-way-to-theme-btrfs-assistant-and-snapper-tools/33376

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

