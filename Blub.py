from tornado.platform.twisted import TwistedIOLoop
from twisted.internet import reactor

TwistedIOLoop(reactor).install()

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import logging, time, os
import tornado.web
from threading import Thread
from resources.emu_config import logging_config
from actors.AbstractBot import Runnable
from actors.AbstractBot import CurrentCommandHandler

_current_command = {"command": "default_command", "kwargs": {}}


# noinspection PyAbstractClass
class BlubCommandHandler(CurrentCommandHandler):
    def __init__(self, *args, **kwargs):
        super(BlubCommandHandler, self).__init__(*args, **kwargs)

    @property
    def current_command(self):
        return _current_command

    @current_command.setter
    def current_command(self, value):
        global _current_command
        logging.info("Set command: %s"%value)
        _current_command = value


class NewServent(Runnable):
    def start(self):
        lc = LoopingCall(self.performDuty)
        lc.start(1)

        app = tornado.web.Application([(r"/current_command", BlubCommandHandler)])
        app.listen(8888)

        reactor.run(installSignalHandlers=0)

    def stop(self):
        reactor.stop()

    def performDuty(self):
        logging.info("duty performed")


if __name__ == "__main__":
    logging.basicConfig(**logging_config)
    obj = NewServent()
    serverthread = Thread(target=obj.start)
    serverthread.start()

    time.sleep(3)
    os.system(
        'wget -q  --post-data=\'command=joinParams&kwargs={"hallo":"welt", "hello":"world"}\' -O - "http://localhost:8888/current_command"')
    time.sleep(2)
    os.system('wget -q -O - "http://localhost:8888/current_command"')

    obj.stop()
    print "join"
    serverthread.join()
