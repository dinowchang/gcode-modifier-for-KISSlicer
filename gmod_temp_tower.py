#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 2017/10/29

@author: dinowchang
"""
import logging
from gmod_base import GmodBase


class GmodTempTower(GmodBase):
    def __init__(self):
        GmodBase.__init__(self)
        self.h_offset = 0
        self.h_step = 0
        self.t_offset = 0
        self.t_step = 0
        self.h_target = 0
        self.t_target = 0
        self.parser.add_argument('-ho', '--h-offset',
                                 help='The height of first test block, default: %(default)s mm',
                                 type=float,
                                 default=2.0)

        self.parser.add_argument('-hs', '--h-step',
                                 help='The thickness of each test block, default: %(default)s mm',
                                 type=float,
                                 default=7.0)

        self.parser.add_argument('-to', '--temp-offset',
                                 help='The temperature of first test block, default: %(default)s C',
                                 type=int,
                                 default=220)

        self.parser.add_argument('-ts', '--temp-step',
                                 help='The temperature increased for each test block, default: %(default)s C',
                                 type=int,
                                 default=-5)

    def parse_args(self):
        args = GmodBase.parse_args(self)
        self.h_offset = args.h_offset
        self.h_step = args.h_step
        self.t_offset = args.temp_offset
        self.t_step = args.temp_step
        self.h_target = self.h_offset
        self.t_target = self.t_offset

    def show_args(self):
        GmodBase.show_args(self)
        print('Height offset :', self.h_offset, 'mm')
        print('Height step :', self.h_step, 'mm')
        print('Temperature offset :', self.t_offset, 'C')
        print('Temperature step :', self.t_step, 'C')

    def gcode_mod(self, line, i):
        if self.height >= self.h_target:
            logging.debug(
                'Line ' + str(i) + ': Insert G-code, height = ' + str(self.height) + ', temp = ' + str(self.t_target))
            self.write(line)
            self.write('M109 S' + str(self.t_target) + '\n')
            self.h_target += self.h_step
            self.t_target += self.t_step
            return True
        return False


if __name__ == '__main__':
    gmod = GmodTempTower()
    gmod.parse_args()
    gmod.show_args()
    gmod.process()
