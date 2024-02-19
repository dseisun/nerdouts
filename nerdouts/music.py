import subprocess

# TODO Fix broken dbus import
# import dbus

from abc import ABC, abstractmethod




class Player(ABC):
    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def play(self):
        pass


class ClementinePlayer(Player):
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

class SpotifyPlayer(Player):

    @staticmethod
    def run_applescript(script):
        osa_command = ['osascript', '-e', script]
        subprocess.run(osa_command)
    
    
    def play(self):
        SpotifyPlayer.run_applescript('tell application "Spotify" to play')

    def pause(self):
        SpotifyPlayer.run_applescript('tell application "Spotify" to pause')

    def next(self):
        SpotifyPlayer.run_applescript('tell application "Spotify" to next track')