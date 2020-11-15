# NFC-boombox
using a raspberry pi with RC522 NFC reader to chose music/album.

# Hardware used

## Raspberry Pi 4 2 GB

A Raspberry Pi 3 should be more than enough, but I wanted to use a newer model. If you want to solder yourself use the compute model.

## RC522 NFC reader with SPI+IRQ

I used Jolicobo RFID Kit RC522, but in my experience everything with a RC522 would work. But look for SPI and IRQ support. Do not use an I2C Version, because the HifiBerry or an alternative Sound card needs the I2C and If you don't know the depths of I2C don't get into that. But if you want to learn than it would be a great experience.

## HifiBerry AMP for power out

I choose the HifiBerry AMP for music playback, the reason behind it is it can directly drive my speakers and it promises great audio quality. But you can use what you want.
My research just told me don't use the onboard stuff and USB Sound Cards have a lag.

# Software used

## [ondryaso/pi-rc522](https://github.com/ondryaso/pi-rc522)

Looks like a simple library to interface with the NFC Tags.

## [Music Player Daemon](http://musicpd.org/) with [Mic92/python-mpd2](https://github.com/Mic92/python-mpd2)

For the music itself.

