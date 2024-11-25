import subprocess
from typing import Protocol

class MusicPlayer(Protocol):
    """Protocol defining the interface for music players."""
    
    def play(self) -> None:
        """Start or resume playback."""
        ...

    def pause(self) -> None:
        """Pause playback."""
        ...

    def next(self) -> None:
        """Skip to next track."""
        ...

class SpotifyPlayer:
    """AppleScript-based Spotify controller for macOS."""

    def run_applescript(self, script: str) -> None:
        """Run an AppleScript command."""
        osa_command = ['osascript', '-e', script]
        subprocess.run(osa_command, check=True)
    
    def play(self) -> None:
        self.run_applescript('tell application "Spotify" to play')

    def pause(self) -> None:
        self.run_applescript('tell application "Spotify" to pause')

    def next(self) -> None:
        self.run_applescript('tell application "Spotify" to next track')