 
# grub theme installation:

- Download and extract `<THEME>.tar.gz/zip`

- Copy the "THEME" folder with root privileges to `/boot/grub/themes/`

- Edit `/etc/default/grub` and add:

```
GRUB_THEME=/boot/grub/themes/<THEMEFOLDER>/theme.txt
```

- optional force resolution

`GRUB_GFXMODE=1920x1080`

- Uncomment to get a beep at grub start,
default `#GRUB_INIT_TUNE="480 440 1"`

`GRUB_INIT_TUNE="1750 523 1 392 1 523 1 659 1 784 1 1047 1 784 1 415 1 523 1 622 1 831 1 622 1 831 1 1046 1 1244 1 1661 1 1244 1 466 1 587 1 698 1 932 1 1195 1 1397 1 1865 1 1397 1"`

- Update grub as root/sudo:

\# `grub-mkconfig -o /boot/grub/grub.cfg`


https://wiki.archlinux.org/title/GRUB/Tips_and_tricks#Theme

https://breadmaker.github.io/grub-tune-tester/

https://www.askapache.com/linux/grub_init_tune-play-sound-through-pcspkr/

https://github.com/JOELwindows7/GRUB_INIT_TUNE_Compilation/blob/master/List.of.GRUB_INIT_TUNE.music.txt

https://gist.github.com/MaxLaumeister/f93717e91c8bd9d435a5

blender logo

https://www.lumalab.net/download/archlogo/
