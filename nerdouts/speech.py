import logging
import subprocess
import sys
import time
from typing import Callable


def get_speech_engine() -> Callable[..., None]:

    def osx_engine(text) -> None:
        logging.info(text)
        command = f'echo "{text}" | say'
        subprocess.call(command, shell=True)
    
    if sys.platform == 'darwin':
        return osx_engine
    else:
        raise Exception('Sorry, no text to speech interface found for your operating system')


def countdown(exc_time):
    tts = get_speech_engine()
    for sec in range(exc_time):
        logging.info("%d seconds until the next exercise" % (exc_time - sec))
        if exc_time - sec == 10:
            tts("10 Seconds left")
        time.sleep(1)
