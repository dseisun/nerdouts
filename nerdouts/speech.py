import logging
import subprocess
import sys
import time
from typing import Callable


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


def countdown(exc_time):
    tts = get_speech_engine()
    for sec in range(exc_time):
        print(" %d seconds until the next exercise    " % (exc_time - sec), end='\r')
        if exc_time - sec == 10:
            tts("10 Seconds left")
        time.sleep(1)
