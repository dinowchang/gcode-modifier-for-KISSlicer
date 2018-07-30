#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 2018/7/29

@author: dinowchang
"""
from unittest import TestCase
from gmod_base import GmodBase

gcode_G28 = ["G28     ; Home all axes\n"]
gcode_G28_XZ = ["G28 X Z ; Home the X and Z axes\n"]

class TestGmodBase(TestCase):
    def setUp(self):
        self.gmod = GmodBase()

    def tearDown(self):
        del self.gmod

    def test_gcode_parser_G28(self):
        for line in gcode_G28:
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.pos, [0, 0, 0])

    def test_gcode_parser_G28_XZ(self):
        for line in gcode_G28_XZ:
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.pos, [0, None, 0])
