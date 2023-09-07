# AFTER INSTALL

https://www.reddit.com/r/archlinux/comments/qzlfsu/what_are_some_postinstallation_optimizations_that/

grub config

❯ `sudo nano /etc/default/grub`

add to `GRUB_CMDLINE_LINUX_DEFAULT="..."`

```
"resume=UUID=<uuid#...> acpi_backlight=vendor xhci_hcd.quirks=1073741824 loglevel=3 mitigations=off"
```

uncomment `GRUB_SAVEDEFAULT=true` set `GRUB_DEFAULT=saved`

❯ `sudo grub-mkconfig -o /boot/grub/grub.cfg`


==> after a grub update redo install and cfg

```
To use the new features provided in this GRUB update, it is recommended
to install it to the MBR or UEFI. Due to potential configuration
incompatibilities, it is advised to run both, installation and generation
of configuration:
$ grub-install ...
$ grub-mkconfig -o /boot/grub/grub.cfg
```

❯ `sudo grub-install /dev/nvme0n1p1 --efi-directory=/boot --bootloader-id=arch-grub --recheck`

❯ `sudo grub-mkconfig -o /boot/grub/grub.cfg`

to improve SSD lifespan and performance in the long term

❯ `sudo systemctl enable fstrim.timer` 

swap file

oneline:

❯ `sudo echo "vm.swappiness=10" | sudo tee /etc/sysctl.d/10-swappiness.conf`

or:

❯ `sudo nano /etc/sysctl.d/10-swappiness.conf`

add:

...

`vm.swappiness=10`

...

will be applied after reboot

### fix cursor theme bug

❯ `sudo nano /usr/share/icons/default/index.theme`
 
change `Adwaita` to `breeze_cursor`

```
[Icon Theme]
Inherits=breeze_cursors
```

### Sleep & Hibernate

https://wiki.archlinux.org/title/Power_management/Suspend_and_hibernate

https://austingwalters.com/increasing-battery-life-on-an-arch-linux-laptop-thinkpad-t14s/

https://forums.linuxmint.com/viewtopic.php?t=287015

check swap partition mount dir

❯ `sudo cat /etc/fstab`

es mount: `/dev/mapper/archVG-swap`

add swap into grub conf

❯ `sudo nano /etc/default/grub`

set path by UUID/LABEL/LVMPATH 

( ie: `resume=UUID=<string>` `resume=LABEL=SWAP` `resume=/dev/archVolumeGroup/archLogicalVolume` )

`GRUB_CMDLINE_LINUX_DEFAULT="...resume=UUID/LABEL/LVMPATH"`

update grub

❯ `sudo grub-mkconfig -o /boot/grub/grub.cfg`

add hooks

❯ `sudo nano /etc/mkinitcpio.conf`

-> BTRFS: at `HOOKS` add `resume` after `filesystem` before `fsck` (wiki says after `udev`)

-> LVM: at `HOOKS` add `resume` after `lvm2` (not sure) 

❯ `sudo mkinitcpio -P`

test reboot/hybernate

### set root theme same as user

❯ `su root`

copy user settings to root config

```
cp -rf /home/fabo/.config/gtk-3.0/ /root/.config/ &&
cp -rf /home/fabo/.config/gtk-4.0/ /root/.config/ &&
cp /home/fabo/.config/kdeglobals /root/.config/
```

### start ssh-agent

https://wiki.archlinux.org/title/SSH_keys#SSH_agents

https://wiki.archlinux.org/title/KDE_Wallet#Using_the_KDE_Wallet_to_store_ssh_key_passphrases

https://support.atlassian.com/bitbucket-cloud/docs/set-up-personal-ssh-keys-on-linux/

https://support.atlassian.com/bitbucket-cloud/docs/managing-multiple-bitbucket-user-ssh-keys-on-one-device/

verify ssh is installed

❯ `ssh -V` 

check if process is running

❯ `ps -auxc | grep ssh-agent`   

if no processes, start it

❯ `eval ssh-agent`

generate key

❯ `ssh-keygen -t rsa -b 4096 -m PEM -f jwtRS256.key`

add key to ssh

❯ `ssh-add ~/.ssh/id_rsa`


list added keys

❯ `ssh-add -l`

=> to autostart the process add to .barshrc / .zshrc

```
if ! pgrep -u "$USER" ssh-agent > /dev/null; then
    ssh-agent -t 1h > "$XDG_RUNTIME_DIR/ssh-agent.env"
fi
if [[ ! -f "$SSH_AUTH_SOCK" ]]; then
    source "$XDG_RUNTIME_DIR/ssh-agent.env" >/dev/null
fi
```

might also install `keychain` if is still not working

### Fix Discover not showing updates

❯ `sudo rm -rf /var/lib/PackageKit/alpm` && `sudo systemctl restart packagekit`

### show bluetooth charge %

https://wiki.archlinux.org/title/bluetooth_headset#Headset_via_Pipewire

❯ `sudo nano /etc/bluetooth/main.conf`

set experimental to `true`

```
# Enables experimental features and interfaces.
# Defaults to false.
Experimental = true
```

also `KernelExperimental = true` if needed

# FIRMWARE UPDATES

❯ `sudo fwupdmgr get-updates`

❯ `sudo fwupdmgr update`

# PAKAGES

## PACMAN CHACE

The `paccache` script, provided within the `pacman-contrib` package, deletes all cached versions of installed and uninstalled packages, except for the most recent three, by default:

❯ `sudo paccache -r`

-> Enable and start `paccache.timer` to discard unused packages weekly.

Tip: You can create a hook to run this automatically after every pacman transaction, see https://bbs.archlinux.org/viewtopic.php?pid=1694743#p1694743 and `pacman-cleanup-hook`AUR.
You can also define how many recent versions you want to keep. To retain only one past version use:

❯ `sudo paccache -rk1`

See `paccache -h` for more options.

## yay aur pkg chache

❯ `yay -Scc`

### TUXEDO REPO https://github.com/tuxedocomputers

❯ `yay tuxedo` or `tuxedo-touchpad-switch`, `tuxedo-keyboard`, `tuxedo-control-center-bin`

https://www.reddit.com/r/tuxedocomputers/comments/qngn8r/manjaro_and_tuxedo_control_center/

https://aur.archlinux.org/packages/tuxedo-touchpad-switch/

https://aur.archlinux.org/packages/tuxedo-keyboard/

https://aur.archlinux.org/packages/tuxedo-control-center-bin/

### zsh

❯ `sudo pacman -S zsh zsh-completions zsh-syntax-highlighting zsh-autosuggestions`

https://wiki.archlinux.org/title/Command-line_shell#Changing_your_default_shell

list available shells

❯ `chsh -l`

change default shell to zsh for root (or leave it default to `/bin/bash`)
 
❯ `sudo chsh -s /bin/zsh`
 
and for the current user
 
❯ `chsh -s /bin/zsh`

extra: add line to .zshrc `export SHELL=zsh`

- zsh autocompletion

You should have a directory where the completions can be saved:

❯ `mkdir ~/.zcompcache`

- deno example

Then output the completions:

❯ `deno completions zsh > ~/.zcompcache/_deno`

And ensure the completions get loaded in your `~/.zshrc`:

❯ `fpath=(~/.zcompcache $fpath)`

❯ `autoload -Uz compinit`

❯ `compinit -u`

If after reloading your shell and completions are still not loading, you may need to remove `~/.zcompdump/` to remove previously generated completions and then `compinit` to generate them again.

### pacman sound hook

https://aur.archlinux.org/packages/pacman-beep-hook

❯ `yay pacman-beep-hook`

### manjaro zsh config

❯ `yay manjaro-zsh-config-git`

### powerlevel10k

https://github.com/romkatv/powerlevel10k

install pwlv10k font

❯ `yay ttf-meslo-nerd-font-powerlevel10k`

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

### bitwarden

❯ `yay bitwarden libappindicator-gtk3`

### browsers and mail

❯ `yay` `thunderbird` `kmail` `google-chrome` `firefox`

### postgresql

https://wiki.archlinux.org/title/PostgreSQL

❯ `sudo pacman -S postgresql`

set postgres password

❯ `sudo passwd postgres`

❯ `sudo chown -R postgres:postgres /var/lib/postgres/` or `sudo chown -R <USER>:users /var/lib/postgres/`

on BTRFS disable CoW (if not present do after initdb)

❯ `sudo chattr +C /var/lib/postgres/data`

change to postgres and initdb

❯ `su postgres`

❯ `initdb -D /var/lib/postgres/data` or `initdb --locale=en_US.UTF-8 -E UTF8 -D /var/lib/postgres/data`

start service as root/sudo

`su` to user/root

❯ `sudo systemctl enable postgresql.service` && `sudo systemctl start postgresql.service`

try `sudo psql -U postgres`

❯ `su postgres` & ❯ `createuser --interactive` create `root` user ( `su <USER>` and/or `createdb <DBNAME>`)

set db user password

❯ `psql -U postgres` & `\password <username>`

`CREATE DATABASE test OWNER root;`

`su postgres`, `createdb <DBNAME>`, `su` to user `psql -U <USER> -d <DBNAME>`

❯ `psql DBNAME`


### MariaDB

https://wiki.archlinux.org/title/MariaDB

❯ `sudo pacman -S mariadb`

on BTRFS disable CoW

❯ `sudo chattr +C /var/lib/mysql`

initialize

❯ `sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql`

enable/start service

❯ `sudo systemctl start mariadb.service` & `sudo systemctl enable mariadb.service`

log in (default password is empty)

❯ `sudo mysql -u root -p`

(`use mysql;`)

`set password for 'root'@'localhost' = password('YOUR_ROOT_PASSWORD_HERE');`

`flush privileges;`

`quit`

test

❯ `mysql -u root -p`

additionally to create user (change `username` and `password` keep '')

`CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';`

grant privileges,

allow all `*.*` or only on db `dbname.*`

`GRANT ALL PRIVILEGES ON *.* TO 'user'@'localhost';`

apply

`FLUSH PRIVILEGES;`

check

`SHOW GRANTS FOR 'user'@localhost;`

enjoy

!!! akonadi https://userbase.kde.org/Akonadi#Disabling_the_Akonadi_subsystem
!!! https://gist.github.com/aldolat/e8066baf8a390e5d5f5ed6e0849ec78c

`~/.config/akonadi/akonadiserverrc`

```
[Debug]
Tracer=null

[%General]
Driver=QMYSQL

[QMYSQL]
Host=
Name=akonadi_USERNAME
Options="UNIX_SOCKET=/run/mysqld/mysqld.sock"
User=USERNAME
Password=PASSWORD
ServerPath=/usr/bin/mysqld
StartServer=false
```

- check status (or stop/start service)

❯ `akonadictl status`

sample dataset => https://www.mysqltutorial.org/mysql-sample-database.aspx

### DBEAVER

❯ `sudo pacman -S dbeaver`

### mongodb

https://wiki.archlinux.org/title/MongoDB

https://aur.archlinux.org/packages/mongodb-compass/

❯ `yay mongodb-bin mongodb-tools-bin mongosh-bin mongodb-compass`

❯ `sudo systemctl status mongodb`

❯ `sudo systemctl enable mongodb.service`

❯ `sudo systemctl start mongodb.service`


- Check Locate native client

Install mysql/mariadb

Open terminal, then type `which mysql`

result: `/usr/bin/mysql`

Fix native client is not specified for connection

Click "Local client"

Select "Browse"

Click "Add home"

Navigate to locate mysql (default: `/usr/bin`) and click "Open"


cli

❯ `mongosh` (or use legacy `mongo`)

on BTRFS disable CoW https://www.mongodb.com/community/forums/t/mongodb-with-btrfs/5699

❯ `sudo chattr +C /var/lib/mongodb`

### NEO4J

https://aur.archlinux.org/packages/neo4j-desktop

 electron standalone

❯ `yay -S neo4j-desktop`

https://aur.archlinux.org/packages/neo4j-community

database service

`neo4j-community` 

(its easier to use the docker image and persist data w/ volumes)

```
docker run \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    neo4j
```

### vscode

https://wiki.archlinux.org/title/Visual_Studio_Code

❯ `yay visual-studio-code-bin`

install needed keyring

❯ `sudo pacman -S gnome-keyring`

https://stackoverflow.com/questions/34400272/visual-studio-code-is-always-asking-for-git-credentials , https://github.blog/2020-12-15-token-authentication-requirements-for-git-operations/

set up ssh key for github

https://www.golinuxcloud.com/set-up-visual-studio-code-remote-ssh-github/

### GIT GUI

- gitkraken

❯ `yay gitkraken`

`> preferences > SSH > unmark use local SSH agent`

https://aur.archlinux.org/packages/gitkraken

- github desktop

❯ `yay github-desktop-bin`

https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup

https://man.archlinux.org/man/gitcredentials.7


### insomnia

❯ `yay insomnia-bin`

### postman

❯ `yay postman-bin`

## ngrok

https://ngrok.com/download

https://dashboard.ngrok.com/get-started/setup

❯ `yay ngrok`

### python env

https://wiki.archlinux.org/title/python#Package_management

https://github.com/pypa/pipenv

https://wiki.archlinux.org/title/Python/Virtual_environment

❯ `sudo pacman -S python-pipenv`

### nvm, node & npm

https://wiki.archlinux.org/title/Node.js

❯ `sudo pacman -S nodejs npm`

❯ `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash`

❯ `source ~/.zshrc`

### Docker

https://wiki.archlinux.org/title/Docker#Installation

for btrfs https://www.reddit.com/r/docker/comments/mba2c7/how_do_i_make_docker_work_nicely_with_btrfs_host/ , https://github.com/egara/arch-btrfs-installation   

❯ `sudo pacman -S docker`

❯ `sudo systemctl enable docker.service`

❯ `sudo systemctl enable containerd.service`

❯ `sudo systemctl start docker.service`

❯ `sudo systemctl start containerd.service`

❯ `sudo docker info`

remove sudo

❯ `sudo groupadd docker`

❯ `sudo usermod -aG docker $USERTOADD`

REBOOT and test

❯ `docker run hello-world`

PORTAINER GUI 

https://github.com/portainer/portainer

https://docs.portainer.io/v/ce-2.9/start/install/server/docker/linux

https://www.portainer.io/casestudy/firstapp

create volume

❯ `docker volume create portainer_data`

pull/run container

```
docker run -d -p 9000:9000 -p 9443:9443 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest 
```
enterprise edition

```
docker run -d -p 9000:9000 -p 9443:9443 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ee:latest
```


    
❯ `docker ps`

- to update:

NEW (from the docs https://docs.portainer.io/start/upgrade/docker)

❯ `docker stop portainer`

❯ `docker rm portainer`

❯ `docker pull portainer/portainer-ce:latest`

```
docker run -d -p 9000:9000 -p 9443:9443 \
    --name=portainer --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:latest
```

go to http://localhost:9000 or https:9443

otherwise install from aur (not needed if portainer container is running)

❯ `yay portainer-bin` 

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

❯ `sudo pacman -S libreoffice-fresh` (`libreoffice-fresh-LANGUAGE`)

extensions `libreoffice-extension-texmaths libreoffice-extension-writer2latex`

also `hunspell hyphen libmythes` based on language `hunspell-en_us hyphen-en mythes-en`

fonts `ttf-dejavu noto-fonts`

### spotify

https://wiki.archlinux.org/title/Spotify#Installation

❯ `yay spotify`

### authy (mfa)

https://aur.archlinux.org/packages/authy

❯ `yay authy`

### kwallet

https://wiki.archlinux.org/title/KDE_Wallet

https://wiki.archlinux.org/title/GNOME/Keyring#Troubleshooting

❯ `sudo pacman -S khelpcenter kwallet kwalletmanager`

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

❯ `yay breath-theme-git`  

plasma

https://wiki.manjaro.org/index.php/Install_Desktop_Environments

https://gitlab.manjaro.org/artwork/themes/breath
  
https://manjaro.org/branch-compare/?q=breath2

grub

https://gitlab.manjaro.org/artwork/branding/grub-theme

### pamac

https://wiki.manjaro.org/index.php/Pamac

https://aur.archlinux.org/packages/pamac-aur/?O=10&PP=10

❯ `yay pamac` also `pamac-tray-appindicator`
  
### window tiling
  
https://swaywm.org/ (wayland)

japokwm (wayland)
  
https://github.com/kwin-scripts/kwin-tiling
  
https://store.kde.org/p/1309653/
  
https://github.com/lingtjien/Grid-Tiling-Kwin

### Retroarch

❯ `sudo pacman -S retroarch`

Open and close retroarch arch once, to ensure it creates the local directories

Edit the local configuration file at `~/.config/retroarch/retroarch.cfg`

and make sure the following 5 lines are set to these settings

`assets_directory = "~/.config/retroarch/assets"`

`menu_show_core_updater = "true"`

`core_updater_show_experimental_cores = "true"`

`libretro_directory = "~/.config/retroarch/cores/"`

`libretro_info_path = "~/.config/retroarch/cores/info"`

# CHROME WEB EXTENSIONS

https://chrome.google.com/webstore/detail/gmail/pjkljhegncpnkpknbcohdijeoejaedia?hl=en

https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm?utm_source=chrome-ntp-icon

https://chrome.google.com/webstore/detail/duckduckgo-privacy-essent/bkdgflcldnnnapblkhphbgpggdiikppg?utm_source=chrome-ntp-icon

https://chrome.google.com/webstore/detail/dark-reader/eimadpbcbfnmbkopoojfekhnkhdbieeh?utm_source=chrome-ntp-icon

https://chrome.google.com/webstore/detail/json-viewer-pro/eifflpmocdbdmepbjaopkkhbfmdgijcc?utm_source=chrome-ntp-icon

https://chrome.google.com/webstore/detail/picture-in-picture-extens/hkgfoiooedgoejojocmhlaklaeopbecg?utm_source=chrome-ntp-icon

https://chrome.google.com/webstore/detail/bitwarden-free-password-m/nngceckbapebfimnlniiiahkandclblb

apps (spa/pwa)

for screensharing under wayland enable `WebRTC PipeWire support` in chrome://flags/

for https on localhost: chrome://flags/#allow-insecure-localhost

https://chrome.google.com/webstore/detail/gmail/pjkljhegncpnkpknbcohdijeoejaedia/related?hl=en

https://chrome.google.com/webstore/detail/google-drive/apdfllckaahabafndbhieahigkjlhalf

https://chrome.google.com/webstore/detail/docs/aohghmighlieiainnegkcijnfilokake

https://chrome.google.com/webstore/detail/slides/aapocclcgogkmnckokdopfmhonfmgoek

https://chrome.google.com/webstore/detail/sheets/felcaaldnbdncclmgdcncolpebgiejap

https://chrome.google.com/webstore/detail/google-drawings/mkaakpdehdafacodkgkpghoibnmamcme

https://chrome.google.com/webstore/detail/google-forms/jhknlonaankphkkbnmjdlpehkinifeeg

( https://chrome.google.com/webstore/detail/youtube/blpcfgokakmgnkcojhhkbfbldkacnbeo?hl=en )
 
# FONTS

https://wiki.archlinux.org/title/Fonts#Font_packages

https://fontlibrary.org/en

### Basic fonts

❯ `yay -S`

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
