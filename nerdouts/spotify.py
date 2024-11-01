import subprocess

def run_applescript(script):
    osa_command = ['osascript', '-e', script]
    subprocess.run(osa_command)

def play_spotify():
    run_applescript('tell application "Spotify" to play')

def pause_spotify():
    run_applescript('tell application "Spotify" to pause')

def next_track():
    run_applescript('tell application "Spotify" to next track')

def previous_track():
    run_applescript('tell application "Spotify" to previous track')