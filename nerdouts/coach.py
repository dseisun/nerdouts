import logging
import subprocess

from six import with_metaclass

from singleton import Singleton


class Coach(with_metaclass(Singleton, object)):
    @staticmethod
    def say(sentence):
        subprocess.call('echo "' + sentence + '"| festival --tts', shell=True)
        logging.info(sentence)

    def handle(self, *args, **kwargs):
        if args == ["timer", "countdown"]:
            self._handle_timer_countdown(kwargs["second"])

    def _handle_timer_countdown(self, seconds):
        logging.info("%s seconds until the next exercise".format(seconds))
        if seconds == 10:
            Coach.say("10 Seconds left")
