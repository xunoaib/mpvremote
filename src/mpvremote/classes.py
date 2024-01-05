import os
import socket
from collections.abc import Callable
from enum import Enum

MPV_SOCKET = os.getenv('MPV_SOCKET_PATH', '~/.config/mpv/socket')

Button = Enum('Button', [
    'play', 'pause', 'stop', 'rewind', 'forward', 'mute', 'volup', 'voldown',
    'info', 'option', 'back', 'cancel', 'home', 'subtitle', 'power',
    'channelup', 'channeldown', 'menu', 'setup', 'chapternext',
    'chapterprevious', 'up', 'right', 'down', 'left', 'enter', 'stepleft',
    'stepright', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7',
    'num8', 'num9', 'num0', 'topmenu', 'Return', 'display', 'zoom', 'slowplay',
    'fastplay', 'sur', 'audio', 'angle', 'openclose', 'tvpower'
])


class BaseMapping:
    '''Associates IR codes with named Buttons'''

    codes: dict[int, Button | None]

    def get(self, code: int):
        return self.codes.get(code)

    def __contains__(self, code: int):
        return code in self.codes


class BaseHandler:
    '''Associates named Buttons with executable functions and descriptions'''

    funcs: dict[Button, tuple[Callable, str]]

    def get(self, button: Button):
        return self.funcs.get(button)

    def __contains__(self, button: Button):
        return button in self.funcs


class BaseController:
    '''
    Primary base class composed of mappings and handlers. Each are queried in
    order until one or none report being able to handle a given event.
    '''

    mappings: list[BaseMapping]
    handlers: list[BaseHandler]

    def code_to_button(self, code: int):
        '''Finds the button associated with an IR code'''

        for mapping in self.mappings:
            if button := mapping.get(code):
                return button

    def button_to_action(self, button: Button):
        '''
        Finds the first action handler which can handle the given button.
        Return the handler, an executable function associated with the button,
        and its description.
        '''

        for handler in self.handlers:
            if func_desc := handler.get(button):
                return handler, *func_desc

    def code_to_action(self, code: int):
        '''Converts code -> '''
        if button := self.code_to_button(code):
            return button, self.button_to_action(button)


def send_mpv_command(command: str, socket_path=MPV_SOCKET):
    '''
    Sends an mpv command to an IPC socket. Raises an exception if the socket
    doesn't exist or rejects the connection.
    '''

    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(os.path.expanduser(socket_path))
        client.sendall(command.encode() + b'\n')
        client.close()
    except (ConnectionRefusedError, FileNotFoundError) as exc:
        raise exc.__class__(
            f'{exc}. Failed to execute mpv command: "{command}"') from exc


def mpv_command_to_func(command: str, socket_path):
    return lambda: send_mpv_command(command, socket_path)


class MpvHandler(BaseHandler):
    '''
    Converts a dict of mpv string commands to functions which execute those mpv
    commands. Subclass this class to define which buttons will trigger which
    mpv commands.
    '''

    def __init__(self, commands: dict[Button, str], socket_path: str):
        self.funcs = {
            button: (mpv_command_to_func(command, socket_path), command)
            for button, command in commands.items()
        }
