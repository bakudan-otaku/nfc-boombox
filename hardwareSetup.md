# Everything to get the Hardware going

Skipping Raspberry Pi Setup, please google it, I could not do it any better.

## Hifiberry

[Software Guide from hifiberry](https://www.hifiberry.com/docs/software/configuring-linux-3-18-x/)

edit /boot/config.txt:
```
Remove dtparam=audio=on simple put a # infront:
#dtparam=audio=on

Add:
dtoverlay=hifiberry-dacplus
force_eeprom_read=0

```

edit /etc/asound.conf
```
pcm.!default {
  type hw card 0
}
ctl.!default {
  type hw card 0
}
```

Check via `aplay -l`, sample output:
```
**** List of PLAYBACK Hardware Devices ****
card 0: sndrpihifiberry [snd_rpi_hifiberry_dacplus], device 0: HiFiBerry DAC+ HiFi pcm512x-hifi-0 [HiFiBerry DAC+ HiFi pcm512x-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```


