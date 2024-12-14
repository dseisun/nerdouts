import logging
import subprocess
import sys
import time
from typing import Callable
import threading
import queue
import select

def get_speech_engine() -> Callable[..., None]:
    def osx_engine(text) -> None:
        logging.info(text)
        command = f'echo "{text}" | say'
        # Timeout is because sometimes the subprocess hangs on a mac
        try:
            subprocess.call(command, shell=True, timeout=10)
        except subprocess.TimeoutExpired:
            logging.error(f'command {command} hung and timed out after 10 seconds')
    
    if sys.platform == 'darwin':
        return osx_engine
    else:
        raise Exception('Sorry, no text to speech interface found for your operating system')

# Global flag for controlling the input thread
_stop_input = threading.Event()
_input_queue = queue.Queue()

def input_thread():
    """Thread function to handle keyboard input."""
    while not _stop_input.is_set():
        try:
            if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                char = sys.stdin.read(1)
                if char == 's':
                    _input_queue.put('skip')
                elif char in ('q', '\x03'):  # 'q' or Ctrl+C
                    _input_queue.put('quit')
                    break
        except (select.error, ValueError):
            # Handle potential errors from select
            break

def countdown(exc_time):
    """
    Countdown timer with skip functionality.
    Returns True if exercise was skipped, False otherwise.
    """
    tts = get_speech_engine()
    
    # Start input thread
    _stop_input.clear()
    input_thread_handle = threading.Thread(target=input_thread)
    input_thread_handle.daemon = True
    input_thread_handle.start()
    
    try:
        start_time = time.time()
        while time.time() - start_time < exc_time:
            remaining = exc_time - int(time.time() - start_time)
            print(f" {remaining} seconds until the next exercise (press 's' to skip, 'q' to quit)    ", end='\r')
            
            try:
                command = _input_queue.get_nowait()
                if command == 'skip':
                    print("\nSkipping exercise...")
                    return True
                elif command == 'quit':
                    print("\nQuitting...")
                    sys.exit(0)
            except queue.Empty:
                pass
            
            if remaining == 10:
                tts("10 Seconds left")
            
            time.sleep(0.1)
            
        return False
    finally:
        # Clean up input thread
        _stop_input.set()
        input_thread_handle.join(timeout=1)
