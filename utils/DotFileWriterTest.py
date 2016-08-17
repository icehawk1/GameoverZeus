#!/usr/bin/env python2
# coding=UTF-8
"""Tests whether the SVG and PDF is actually generated"""

import os
import tempfile
import unittest

from DotFileWriter import DotFileWriter
from resources import emu_config
from topologies.BriteTopology import applyBriteFile


class DotFileWriterTest(unittest.TestCase):
    def setUp(self):
        self.dotwriter = DotFileWriter()
        self.pdffile = tempfile.mkstemp(suffix=".pdf")[1]
        self.svgfile = tempfile.mkstemp(suffix=".svg")[1]

    def testFlatrouter(self):
        applyBriteFile(emu_config.basedir + "/testfiles/flatrouter.brite", [self.dotwriter])
        self.dotwriter.generatePdf(self.pdffile)
        self.dotwriter.generateSvg(self.svgfile)

        self.assertTrue(os.path.getsize(self.pdffile) > 1)
        self.assertTrue(os.path.getsize(self.svgfile) > 1)
