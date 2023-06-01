#!/usr/bin/env python3
'''
Executes mpv commands based on IR codes read from an Arduino.
Commands are sent to mpv through an IPC socket configured in mpv.conf (see input-ipc-server).
'''

import argparse
import socket
import sys
from time import time

import serial

SOCKET_PATH = '~/.config/mpv/socket'

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


def send_mpv_command(command):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(command.encode())
    client.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', default='/dev/ttyUSB0',
                        help='Arduino device path or port name')
    parser.add_argument('baud', nargs='?', type=int, default=9600,
                        help='Arduino serial baud rate')
    parser.add_argument('-r', '--repeat-code', nargs='?', type=str, default='0',
                        help='Convert this code to the last received code, like a "repeat" signal')
    parser.add_argument('-c', '--cooldown', type=float, default=.2,
                        help='Cooldown between executing duplicate commands')
    args = parser.parse_args()

    com = serial.Serial(args.port, args.baud)
    print('Connected. Waiting for IR codes...')

    last_code = None
    last_time = time()

    while True:
        code = com.readline().decode().strip().lower()

        # detect repeated codes and enforce a cooldown
        if code in (last_code, args.repeat_code):
            code = last_code
            if time() - last_time < args.cooldown:
                continue

        if command := IRCODE_COMMANDS.get(code):
            print(code, command)
            send_mpv_command(command)
            last_time = time()
        else:
            print(code)

        last_code = code


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except serial.SerialException as exc:
        print(exc, file=sys.stderr)
