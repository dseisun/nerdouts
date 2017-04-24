import subprocess

import dbus
from six import with_metaclass

from singleton import Singleton


class Player(with_metaclass(Singleton, object)):
    _player = dbus.SessionBus().get_object('org.mpris.clementine', '/Player')
    _iface = dbus.Interface(_player, dbus_interface='org.freedesktop.MediaPlayer')

    def __init__(self):
        subprocess.call('clementine -l /home/dseisun/.config/Clementine/Playlists/Workout.xspf', shell=True)

    @staticmethod
    def next():
        Player._iface.Next()

    @staticmethod
    def pause():
        Player._iface.Pause()

    @staticmethod
    def play():
        Player._iface.Play()
