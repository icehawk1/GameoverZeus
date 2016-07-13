#!/usr/bin/env python2
# coding=UTF-8
import unittest, string, logging
from BotCommands import executeCurrentCommand, BotCommands
from resources.emu_config import logging_config


def tmpfunc(self, abc):
    return string.swapcase(abc)


class BotCommandsTest(unittest.TestCase):
    def testExecuteExistingCommand(self):
        actual = executeCurrentCommand({"command": "joinParams", "kwargs": {"hallo": "welt", "hello": "world"}})
        self.assertEquals("weltworld", actual)

    def testInsertCommand(self):
        BotCommands.newCommand = tmpfunc
        actual = executeCurrentCommand({"command": "newCommand", "kwargs": {"abc": "AbCdF"}})
        self.assertEquals("aBcDf", actual)


if __name__ == '__main__':
    logging.basicConfig(**logging_config)
    unittest.main()
