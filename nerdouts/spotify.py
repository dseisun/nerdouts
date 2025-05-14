from nerdouts.music_player import MusicPlayer
import subprocess

class SpotifyPlayer(MusicPlayer):
    def run_applescript(self, script):
        osa_command = ['osascript', '-e', script]
        subprocess.run(osa_command)

    def play(self) -> None:
        self.run_applescript('tell application "Spotify" to play')

    def pause(self) -> None:
        self.run_applescript('tell application "Spotify" to pause')

    def next_track(self) -> None:
        self.run_applescript('tell application "Spotify" to next track')

    def previous_track(self) -> None:
        self.run_applescript('tell application "Spotify" to previous track')