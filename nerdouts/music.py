import subprocess

import dbus
from six import with_metaclass

from singleton import Singleton


class Player(with_metaclass(Singleton, object)):
    def next(self):
        raise NotImplementedError("Player must implement 'next' method")

    def pause(self):
        raise NotImplementedError("Player must implement 'pause' method")

    def play(self):
        raise NotImplementedError("Player must implement 'play' method")


class ClementinePlayer(with_metaclass(Singleton, Player)):
    def __init__(self):
        self._player = dbus.SessionBus().get_object('org.mpris.MediaPlayer2.clementine', '/org/mpris/MediaPlayer2')
        self._iface = dbus.Interface(self._player, dbus_interface='org.mpris.MediaPlayer2.Player')
        subprocess.call('clementine -l /home/dseisun/.config/Clementine/Playlists/Workout.xspf', shell=True)

    def next(self):
        self._iface.Next()

    def pause(self):
        self._iface.Pause()

    def play(self):
        self._iface.Play()
