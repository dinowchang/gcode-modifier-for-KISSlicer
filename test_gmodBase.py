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
kiss_thickness = ["; layer_thickness_mm = 0.1\n"]
kiss_begin_of_layer = ["; BEGIN_LAYER_OBJECT z=0.300 z_thickness=0.100\n"]

s3d_thickness = [";   layerHeight,0.3\n"]
s3d_begin_of_layer = ["; layer 8, Z = 0.948\n"]

cura_thickness = [";Layer height: 0.1\n"]
cura_begin_of_layer = [";Layer height: 0.1\n",
                       ";LAYER:29",
                       "G0 X101.802 Y96.2 Z3.1",
                       ";LAYER:30\n"]

# g-code test pattern
gcode_G1_M82 = ["M82\n",
                "G28\n",
                "G92 E0\n",
                "G1 X5 Y-5 Z0.5\n",
                "G1 X10 Y10 E1\n",
                "G1 X5 Y-5 Z0.5\n"
                ]

gcode_G1_M83 = ["M83\n",
                "G28\n",
                "G92 E0\n",
                "G1 X5 Y-5 Z0.5\n",
                "G1 X10 Y10 E1\n",
                "G1 X5 Y-5 Z0.5\n"
                ]

gcode_G28 = ["G28     ; Home all axes\n"]
gcode_G28_XZ = ["G28 X Z ; Home the X and Z axes\n"]
gcode_G92 = ["G92 E10\n"]
gcode_M109 = ["M109 S200 T0\n"]


class TestGmodBase(TestCase):
    def setUp(self):
        self.gmod = GmodBase()

    def tearDown(self):
        del self.gmod

    def test_kiss_parser_thickness(self):
        for i, line in enumerate(kiss_thickness, 1):
            self.gmod.kisslicer_v162_parser(line, i)
        self.assertEqual(self.gmod.thickness, 0.1)

    def test_kiss_parser_begin_of_layer(self):
        for i, line in enumerate(kiss_begin_of_layer, 1):
            self.gmod.kisslicer_v162_parser(line, i)
        self.assertEqual(self.gmod.begin_of_layer, True)
        self.assertEqual(self.gmod.height, 0.3)
        self.assertEqual(self.gmod.thickness, 0.1)

        for i, line in enumerate(comment_Nothing, 1):
            self.gmod.kisslicer_v162_parser(line, 1)
        self.assertEqual(self.gmod.begin_of_layer, False)

    def test_s3d_parser_thickness(self):
        for i, line in enumerate(s3d_thickness, 1):
            self.gmod.s3d_v302_parse(line, i)
        self.assertEqual(self.gmod.thickness, 0.3)

    def test_s3d_parser_begin_of_layer(self):
        for i, line in enumerate(s3d_begin_of_layer, 1):
            self.gmod.s3d_v302_parse(line, i)
        self.assertEqual(self.gmod.begin_of_layer, True)
        self.assertEqual(self.gmod.height, 0.948)
        self.assertEqual(self.gmod.layer, 8)

        for i, line in enumerate(comment_Nothing, 1):
            self.gmod.s3d_v302_parse(line, 1)
        self.assertEqual(self.gmod.begin_of_layer, False)

    def test_cura_parser_thickness(self):
        for i, line in enumerate(cura_thickness, 1):
            self.gmod.cura_v303_parser(line, i)
        self.assertEqual(self.gmod.thickness, 0.1)

    def test_gcode_parser_G1_M82(self):
        for i, line in enumerate(gcode_G1_M82, 1):
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.pos, [5, -5, 0.5])
        self.assertEqual(self.gmod.ext_pos, 1)
        self.assertEqual(self.gmod.model_height, 0.5)

    def test_gcode_parser_G1_M83(self):
        for i, line in enumerate(gcode_G1_M83, 1):
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.pos, [5, -5, 0.5])

    def test_gcode_parser_G28(self):
        for i, line in enumerate(gcode_G28, 1):
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.pos, [0, 0, 0])

    def test_gcode_parser_G28_XZ(self):
        for i, line in enumerate(gcode_G28_XZ, 1):
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.pos, [0, None, 0])

    def test_gcode_parser_G92(self):
        for i, line in enumerate(gcode_G92, 1):
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.ext_pos, 10)

    def test_gcode_parser_M109(self):
        for i, line in enumerate(gcode_M109, 1):
            self.gmod.gcode_parser(line, 1)
        self.assertEqual(self.gmod.temperature, 200)
