#!/usr/bin/env python2
# coding=UTF-8
import logging
from resources import emu_config

logdir = "/tmp/botnetemulator"
#: The file where the logs are written to
logfile = "%s/machine_readable.log" % logdir


def _configureMRLogger(filename=logfile):
    handler = logging.FileHandler(filename=filename, mode="a")
    handler.setFormatter(logging.Formatter("%(asctime)s|%(name)s|%(message)s"))
    logging.getLogger("machine_readable").addHandler(handler)
    logging.getLogger("machine_readable").setLevel(logging.INFO)
    logging.getLogger("machine_readable").propagate = 0
    logging.debug("Configure machine readable logger")


def _configureRootLogger(filename=logfile):
    handler = logging.FileHandler(filename=filename, mode="a")
    formatter = logging.Formatter("[%(module)s.py:%(lineno)d (thread: %(threadName)s)]:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().propagate = 0
    logging.debug("Configure root logger")


if __name__ == '__main__':
    logging.basicConfig(**emu_config.logging_config)

    if len(logging.getLogger("machine_readable").handlers) == 0:  # If it is not configured already
        _configureRootLogger()
        _configureMRLogger()

    # log something
    logging.debug('logging.debug message')
    logging.info('logging.info message')
    logging.warn('logging.warn message')
    logging.error('logging.error message')
    logging.critical('logging.critical message')

    # log something
    mrlogger = logging.getLogger("machine_readable").getChild("blub")
    mrlogger.debug('mrlogger.debug message')
    mrlogger.info('mrlogger.info message')
    mrlogger.warn('mrlogger.warn message')
    mrlogger.error('mrlogger.error message')
    mrlogger.critical('mrlogger.critical message')
