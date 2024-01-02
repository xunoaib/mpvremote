#!/usr/bin/env python3
'''
Executes mpv commands based on IR codes read from an Arduino.
Commands are sent to mpv through an IPC socket configured in mpv.conf (see input-ipc-server).
'''

import argparse
import os
import socket
import sys
from time import time

import serial

MPV_SOCKET = os.getenv('MPV_SOCKET_PATH', '~/.config/mpv/socket')


def send_mpv_command(command, socket_path=MPV_SOCKET):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(os.path.expanduser(socket_path))
    client.sendall(command.encode() + b'\n')
    client.close()


IRCODE_COMMANDS = {
    '49d32': 'set pause no; set speed 1; set mute no',  # play
    '49d39': 'set pause yes; set speed 1',  # pause
    '49d23': 'multiply speed 2; set pause no; set mute yes',  # ff
    '49d22': 'set speed 1; seek -5',  # rewind
    '49d30': 'add chapter -1',  # |<< (prev chapter)
    '49d31': 'add chapter 1',  # >>| (next chapter)
    '49d5c': 'seek -1',  # step left
    '62d14': 'seek 1',  # step right
    '49d63': 'cycle sub',  # subtitle
    '49d0b': 'show-progress',  # enter button
    '49d38': 'quit-watch-later',  # stop
    '49d7b': 'seek -5',  # left
    '49d7c': 'seek 5',  # right
    '49d7a': 'seek -60',  # down
    '49d79': 'seek 60',  # up
    '92': 'add volume 2',  # volume up
    '93': 'add volume -2',  # volume down
}


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'port',
        help='Arduino device path or port name (default: /dev/ttyUSB0)')
    parser.add_argument('baud',
                        nargs='?',
                        type=int,
                        default=9600,
                        help='Arduino serial baud rate (default: 9600)')
    parser.add_argument(
        '-r',
        '--repeat-code',
        nargs='?',
        type=str,
        default='0',
        help=
        'Convert this code to the last received code, like a "repeat" signal (default: 0)'
    )
    parser.add_argument(
        '-c',
        '--cooldown',
        type=float,
        default=.2,
        help='Cooldown between executing duplicate commands (default: .2)')
    parser.add_argument('-s',
                        '--socket',
                        default=MPV_SOCKET,
                        help=f'Path to mpv socket (default: {MPV_SOCKET})')
    args = parser.parse_args()

    if not os.path.exists(os.path.expanduser(args.socket)):
        print("Warning: missing mpv socket:", args.socket)

    com = serial.Serial(args.port, args.baud)
    print('Connected. Waiting for IR codes...')

    last_code = ''
    last_time = time()

    while True:
        code = com.readline().decode().strip().lower()

        # detect repeated codes and enforce a cooldown
        if code in (last_code, args.repeat_code):
            code = last_code
            if time() - last_time < args.cooldown:
                continue
        last_code = code

        if command := IRCODE_COMMANDS.get(code):
            print(code, command)
            try:
                send_mpv_command(command, args.socket)
            except FileNotFoundError:
                print('Failed to send command to non-existent socket')
            last_time = time()
        else:
            print(code)


def main():
    try:
        return _main()
    except KeyboardInterrupt:
        pass
    except serial.SerialException as exc:
        print(exc, file=sys.stderr)
    return 1


if __name__ == '__main__':
    exit(main())
