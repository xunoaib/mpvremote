import os
import socket

from dotenv import load_dotenv

load_dotenv()

MPV_SOCKET = os.getenv('MPV_SOCKET_PATH', '~/.config/mpv/socket')


def send_mpv_command(command, socket_path=MPV_SOCKET):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(os.path.expanduser(socket_path))
    client.sendall(command.encode() + b'\n')
    client.close()
