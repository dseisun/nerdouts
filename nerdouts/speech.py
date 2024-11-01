import logging
import subprocess
import sys
import time
from typing import Callable
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


def is_data():
    """Check if there is data waiting on stdin."""
    return select.select([sys.stdin], [], [], 0.1)[0] != []


def countdown(exc_time):
    tts = get_speech_engine()        
    for sec in range(exc_time):
        print(" %d seconds until the next exercise (press 's' to skip)    " % (exc_time - sec), end='\r')
        time.sleep(1)
        if is_data():
                c = sys.stdin.read(1)
                if c == 's':  # Skip if 's' is pressed
                    print("\nSkipping exercise...")
                    return True  # Return True to indicate skip
        
        if exc_time - sec == 10:
            tts("10 Seconds left")
                    
    return False  # Return False to indicate normal completion
