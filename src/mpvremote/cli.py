#!/usr/bin/env python3
import argparse
import os
import sys
from time import time

import serial

from .classes import MPV_SOCKET
from .config import MyController


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'port',
        nargs='?',
        default='/dev/ttyUSB0',
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

    last_code = -1
    last_time = time()

    controller = MyController(args.socket)

    while True:
        code = int(com.readline().decode().strip().lower(), 16)

        # detect repeated codes and enforce a cooldown
        if code in (last_code, args.repeat_code):
            code = last_code
            if time() - last_time < args.cooldown:
                continue
        last_code = code

        if button := controller.code_to_button(code):
            if action := controller.button_to_action(button):
                handler, func, desc = action
                print(
                    f'{code:#x} {button} -- {handler.__class__.__name__}: "{desc}"'
                )
                try:
                    func()
                    last_time = time()
                except (ConnectionRefusedError, FileNotFoundError) as exc:
                    print(f'\033[91m{exc}\033[0m')
            else:
                print(
                    f'{code:#x} {button} -- No action associated with button')
        else:
            print(f'{code:#x} -- No button associated with code')


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
