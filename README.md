# IR Receiver and Controller for mpv (and more!)

Control a desktop media player or execute predefined commands using an infrared remote control.

## Overview

This project uses an Arduino, IR receiver, IR remote, and Python.

- The Arduino receives IR signals and forwards them to your computer via USB.
- The Python program reads these codes and executes various commands assigned to them.

IR remotes vary, so you will have to replace the existing IR codes in `controller.py` with those produced by your specific remote.

While this project was originally designed to control
[mpv](https://github.com/mpv-player/mpv), it can be easily adapted to run other Python code of your choosing.

### mpv Commands

The provided program controls mpv through an IPC socket. It supports common mpv
playback commands like play, pause, fast-forward, seek, next/previous chapter,
volume up/down, and any others that you may wish to add. See
[input.conf](https://github.com/mpv-player/mpv/blob/master/etc/input.conf) for
a complete list of available mpv commands.

## Requirements

- Arduino (with a USB cable)
- IR receiver (3-pin)
- IR remote
- Python 3.8+

## Installation

1. Connect the IR sensor to pin 7 of your Arduino (and the +/- pins to 5V/GND, respectively)
2. Connect the Arduino to your PC via USB
3. Install the [Arduino-IRremote](https://github.com/Arduino-IRremote/Arduino-IRremote) library in the Arduino IDE
4. Flash the `receiver.ino` sketch to your Arduino
5. Install the [pyserial](https://github.com/pyserial/pyserial) Python library (`pip3 install pyserial`)
6. Enable IPC support in mpv by adding `input-ipc-server=~~/socket` to `~/.config/mpv/socket`
7. Run `python3 controller.py [port]`, replacing `[port]` with the port/path of your Arduino device (default: `/dev/ttyUSB0`). Run with `-h` for more options
8. Press buttons on your IR remote to see their codes, then add them to the `IRCODE_COMMANDS` table in `controller.py`
9. Restart the program and enjoy remote mpv control!
