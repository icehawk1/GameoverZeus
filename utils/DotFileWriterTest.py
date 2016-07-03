#!/usr/bin/env python2.7
# coding=UTF-8
import os
import tempfile
import unittest

import emu_config
from DotFileWriter import DotFileWriter
from topologies.BriteTopology import createGraphFromBriteFile


class DotFileWriterTest(unittest.TestCase):
    def setUp(self):
        self.dotwriter = DotFileWriter()
        self.pdffile = tempfile.mkstemp(suffix=".pdf")[1]
        self.svgfile = tempfile.mkstemp(suffix=".svg")[1]

    def testFlatrouter(self):
        createGraphFromBriteFile(emu_config.basedir + "/testfiles/flatrouter.brite", [self.dotwriter])
        self.dotwriter.generatePdf(self.pdffile)
        self.dotwriter.generateSvg(self.svgfile)

        self.assertTrue(os.path.getsize(self.pdffile) > 1)
        self.assertTrue(os.path.getsize(self.svgfile) > 1)
