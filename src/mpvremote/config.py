from pyautogui import press

from .classes import (BaseController, BaseHandler, BaseMapping, Button,
                      MpvHandler, send_mpv_command)


class MyMapping(BaseMapping):
    '''Associates IR codes with their corresponding buttons on a specific remote'''

    codes = {
        0x7f3e0140: Button.play,
        0x5f3e2140: Button.pause,
        0x4f3e3140: Button.chapterprevious,
        0x3f3e4140: Button.chapternext,
        0xbd3cc140: Button.channelup,
        0xad3cd140: Button.channeldown,
        0x66270140: Button.info,
        0x2a3b5140: Button.option,
        0x63022140: Button.back,
        0xb001f140: Button.enter,
        0x9001d140: Button.left,
        0xa001e140: Button.right,
        0x8001c140: Button.down,
        0xf001b140: Button.up,
        0x56170140: Button.volup,
        0x46171140: Button.voldown,
        0x76172140: Button.mute,
    }


class MyMpvHandler(MpvHandler):
    '''Associates buttons with mpv commands by subclassing MpvHandler'''

    def __init__(self, socket_path):
        commands = {
            Button.play:
            'set pause no; set speed 1; set mute no; show-text "Play"',
            Button.pause: 'set pause yes; set speed 1; show-text "Pause"',
            Button.forward:
            'multiply speed 2; set pause no; set mute yes; show-text "Fast-forward"',
            Button.rewind: 'set speed 1; seek -5; show-text "Rewind"',
            Button.chapterprevious: 'add chapter -1',
            Button.chapternext: 'add chapter 1',
            Button.stepleft: 'seek -1',
            Button.stepright: 'seek 1',
            Button.subtitle: 'cycle sub',
            Button.enter: 'show-progress',
            Button.stop: 'quit-watch-later',
            Button.left: 'seek -5',
            Button.right: 'seek 5',
            Button.down: 'seek -60',
            Button.up: 'seek 60',
            Button.volup: 'add volume 2',
            Button.voldown: 'add volume -2',
            Button.mute: 'cycle mute',
        }
        super().__init__(commands, socket_path)


class MyWebHandler(BaseHandler):
    '''A custom handler which only performs actions when mpv is inactive'''

    funcs = {
        Button.left: (lambda: press('left'), 'Press left arrow'),
        Button.right: (lambda: press('right'), 'Press right arrow'),
        Button.enter: (lambda: press('enter'), 'Press enter'),
    }

    def get(self, button: Button):
        # dont perform webhandler actions if mpv is active
        try:
            send_mpv_command('ignore')  # throws exception if mpv is closed
            return None  # mpv is active, so suppress webhandler
        except (ConnectionRefusedError, FileNotFoundError):
            return super().get(button)


class MyController(BaseController):
    '''
    A custom controller which allows a specific IR remote to send button events
    to a list of action handlers. The first handler capable of processing the
    button press will consume it.
    '''

    def __init__(self, socket_path):
        self.mappings = [MyMapping()]
        self.handlers = [
            MyWebHandler(),
            MyMpvHandler(socket_path),
        ]
