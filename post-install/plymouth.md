https://wiki.archlinux.org/title/plymouth#Configuration

https://www.youtube.com/watch?v=eTk2yG1JFsE

- install from aur

\# `yay -S plymouth`

- add `plymouth` hook after `udev`

\# `sudo nano /etc/mkinitcpio.conf`

- rebuild mkinitcpio

\# `sudo mkinitcpio -P`

- edit grub

\# `sudo nano /etc/default/grub`

in `GRUB_CMDLINE_LINUX_DEFAULT` add `quiet splash vt.global_cursor_default=0`

- refresh grub file

\# `grub-mkconfig -o /boot/grub/grub.cfg`

- list all available themes

\# `ls /usr/share/plymouth/themes`

- select a theme

\# `plymouth-set-default-theme -R <theme>`
( `plymouth-set-default-theme -R spinfinity` )

- disable display manager (sddm)

\# `sudo systemctl disable sddm`

- enable the respective DM-plymouth unit provided, e.g. lxdm-plymouth.service

\# `sudo systemctl enable sddm-plymouth.service`

- remove delay

\# `sudo nano /etc/plymouth/plymouthd.conf`

set `ShowDelay=0`

- rebuild mkinitcpio

\# `sudo mkinitcpio -P`

- reboot

# ENJOY



By default, the spinner theme is selected. The theme can be changed by editing /etc/plymouth/plymouthd.conf, for example:

`/etc/plymouth/plymouthd.conf`

---

[Daemon]

Theme=spinner

ShowDelay=5

---


Every time a theme is changed, the initrd must be rebuilt. The -R option ensures that it is rebuilt (otherwise manually run mkinitcpio -P):

\# `plymouth-set-default-theme -R <theme>`

Show kernel messages

During boot you can switch to kernel messages by pressing the Home or Esc keys.

Disable vendor logo

Add `fbcon=nodefer` to kernel parameters

- costumize https://www.youtube.com/watch?v=hKEd9bTou1g
