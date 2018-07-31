#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 2018/7/29

@author: dinowchang
"""
from unittest import TestCase
from gmod_base import GmodBase

# comment test pattern
comment_Nothing = ["; Nothing\n"]
kiss_begin_of_layer = ["; BEGIN_LAYER_OBJECT z=0.300 z_thickness=0.100\n"]

# g-code test pattern
gcode_G28 = ["G28     ; Home all axes\n"]
gcode_G28_XZ = ["G28 X Z ; Home the X and Z axes\n"]

class TestGmodBase(TestCase):
    def setUp(self):
        self.gmod = GmodBase()

    def tearDown(self):
        del self.gmod

    def test_kiss_parser_begin_of_layer(self):
        for i, line in enumerate(kiss_begin_of_layer, 1):
            self.gmod.kisslicer162_parser(line, i)
        self.assertEqual(self.gmod.begin_of_layer, True)
        self.assertEqual(self.gmod.height, 0.3)

        for i, line in enumerate(comment_Nothing, 1):
            self.gmod.kisslicer162_parser(line, 1)
        self.assertEqual(self.gmod.begin_of_layer, False)

    def test_gcode_parser_G28(self):
        for i, line in enumerate(gcode_G28, 1):
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.pos, [0, 0, 0])

    def test_gcode_parser_G28_XZ(self):
        for i, line in enumerate(gcode_G28_XZ, 1):
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.pos, [0, None, 0])
