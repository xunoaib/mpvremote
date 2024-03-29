# mpvremote - Fully-Programmable IR Receiver and Command Executor

Perform actions on your PC, such as controlling video playback in
[mpv](https://github.com/mpv-player/mpv), using an infrared remote control and
an Arduino.

## Requirements
- Python 3.8+
- Arduino (with a USB cable)
- IR receiver (3-pin)
- Any IR remote control

## Setup

**Arduino:**
1. Connect the IR sensor to pin 7 of your Arduino (and conect the +/- pins to 5V/GND, respectively)
2. Connect the Arduino to your PC via USB
4. From the Arduino IDE, install the [Arduino-IRremote](https://github.com/Arduino-IRremote/Arduino-IRremote) library
5. Compile and flash the `arduino_receiver.ino` sketch to your Arduino

**PC:**
1. Install the `mpvremote` Python package from this repository after customizing `config.py` below
2. Enable IPC support in mpv by adding `input-ipc-server=~~/socket` to your mpv config (`~/.config/mpv/config`)

## Usage

- Ensure the Arduino is correctly wired and connected to your PC
- Run `mpvremote [port]` to start the IR listener, replacing `[port]` with the
  serial port/path of your Arduino device (default: `/dev/ttyUSB0`). Run with
  `-h` for more options
- Press buttons on your IR remote to see their IR codes printed in the console
- Add these codes to `config.py` and customize the action handlers as
  desired. See [Configuration](#Configuration) for more details
- Restart the program and test your changes

## Configuration

Modify `config.py` to suit your needs. For example, you may want to:

- Replace the IR codes and button mappings in `MyMapping` with your own.
- Customize the mpv commands in `MyMpvHandler` with your own.
- Add your own non-mpv related actions by subclassing `BaseHandler` and
  mapping buttons to your own Python functions.
- Modify `MyWebHandler` to perform different actions when mpv is not active, or
  remove it from `MyController` if that behavior is not desired.

The general configuration process is as follows:

- Associate your specific IR codes with buttons like "play", "pause", etc (see `MyMapping` and `BaseMapping`)
- Define handlers which associate these buttons with actions (see `MyMpvHandler`, `MyWebHandler`, and `BaseHandler`)
- Combine them into a single integrated controller which can be used in `cli.py` (see `MyController` and `BaseController`)

### Autostart

A systemd service file is provided for convenience and can be used to autostart
the web server:

- Copy `mpvremote.service` into `~/.config/systemd/user/` and modify as needed (i.e.: to pass custom options to mpvremote)
- Run `systemctl --user daemon-reload`
- Run `systemctl --user enable --now mpvremote` to enable autostart and immediately start the service

## Notes

You can also specify a list of mappings and/or handlers in a controller which
will be queried in order when performing code/button/action lookups. The first
mapping or handler to satisfy the lookup will stop and "consume" it, much like
event bubbling.

`MpvHandler` is a convenience handler which transforms mpv commands (strings)
into callable Python functions. This saves you the trouble of individually
wrapping each mpv command in a function.

Refer to
[input.conf](https://github.com/mpv-player/mpv/blob/master/etc/input.conf) for
a list of available mpv commands.

While this project was originally intended to control mpv, it can be easily
adapted to run other Python code.

### Why Mappings and Handlers?

Mappings and handlers decouple the configurations and provide an interface
between specific IR *codes* generated by specific remotes and actions more
commonly associated with *buttons* like "play" and "pause", etc. This allows
you to easily mix and match a variety of IR remotes with various action
handlers. For example, you can define a single action handler, then add support
to it for a variety of different remotes by creating one mapping for each
remote. If you then wish to use those remotes with a new handler, you can
simply reuse the mappings you already created.
