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

        self.remove_gcode = False
        self.h_start = 0
        self.parser.add_argument('-ht', '--height',
                                 help='The height start to print',
                                 type=float)

    def parse_args(self):
        args = GmodBase.parse_args(self)

        log_format = "[%(filename)s:%(lineno)s] %(message)s"

        if args.test:
            self.test_only = True

        if args.debug or args.test:
            logging.basicConfig(format=log_format, level=logging.DEBUG)
        else:
            logging.basicConfig(format=log_format)

        if args.height is None:
            while True:
                try:
                    self.h_start = float(input('Print model from height(mm):'))
                    break
                except ValueError:
                    print("Please input a float value.")
        else:
            self.h_start = args.height
        return args

    def show_args(self):
        GmodBase.show_args(self)
        print('Height :', self.h_start, 'mm')

    def gcode_mod(self, line, i):
        """  rewrite this method to modify gcode
                return True if you don't want to write line back"""
        if self.begin_of_layer is True:
            if self.remove_gcode is False:
                if self.height + self.thickness < self.h_start:
                    self.remove_gcode = True
                    logging.debug("Start removing gcode at line: " + str(i))
            else:
                if self.height + self.thickness >= self.h_start:
                    self.remove_gcode = False
                    logging.debug("Stop removing gcode at line: " + str(i))
                    self.write('G1 Z' + str(self.height + 10) + ' ; Lift the extruder higher then the model\n')

        return self.remove_gcode


if __name__ == '__main__':
    gmod = GmodPrintFromHeight()
    gmod.parse_args()
    gmod.show_args()
    if gmod.h_start <= 0:
        print("The height is less than 0.")
        exit(0)

    if gmod.test_only:
        gmod.test_flow()
    else:
        gmod.process()
