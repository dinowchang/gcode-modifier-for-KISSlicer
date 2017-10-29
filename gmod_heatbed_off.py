#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 2017/10/27

@author: dinowchang
"""
import logging
from gmod_base import GmodBase


class GmodHeatbedOff(GmodBase):
    def __init__(self):
        GmodBase.__init__(self)
        self.height_heatbed_off = 0
        self.parser.add_argument('height',
                                 help='The height to turn off heatbed',
                                 type=float)

    def parse_args(self):
        args = GmodBase.parse_args(self)
        self.height_heatbed_off = args.height

    def show_args(self):
        GmodBase.show_args(self)
        print('Turn off heatbed at height', self.height_heatbed_off, 'mm')

    def gcode_mod(self, line, i):
        if self.height >= self.height_heatbed_off:
            logging.debug('Line ' + str(i) + ': Insert G-code')
            self.write(line)
            self.write('M140 S0\n')
            self.height_heatbed_off = float("inf")
            return True
        return False


if __name__ == '__main__':
    gmod = GmodHeatbedOff()
    gmod.parse_args()
    gmod.show_args()
    gmod.process()
