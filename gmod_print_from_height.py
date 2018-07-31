#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 2018/7/30

@author: dinowchang
"""
import logging
from gmod_base import GmodBase


class GmodPrintFromHeight(GmodBase):
    def __init__(self):
        GmodBase.__init__(self)

    def parse_args(self):
        args = GmodBase.parse_args(self)
        return args

    def show_args(self):
        GmodBase.show_args(self)

    def gcode_mod(self, line, i):
        """  rewrite this method to modify gcode
                return True if you don't want to write line back"""
        return False


if __name__ == '__main__':
    gmod = GmodPrintFromHeight()
    gmod.parse_args()
    gmod.show_args()
    if gmod.test_only:
        gmod.test_flow()
    else:
        gmod.process()
