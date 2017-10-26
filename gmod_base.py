#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 2017/10/25

@author: dinowchang
"""

import argparse
import logging
import os
import sys


class GmodBase:

    def __init__(self):
        self.origin_file = ""
        self.backup_file = ""
        self.f_origin = None
        self.f_backup = None
        self.pause = False
        self.comment_parser = self.generic_parser

        self.z = 0
        self.relative_extruder = False

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-d', '--debug',
                                 help='Enable debug mode',
                                 action='store_true')

        self.parser.add_argument('-p', '--pause',
                                 help='Pause before exit',
                                 action='store_true')

        self.parser.add_argument('input-file',
                                 help='Input gcode file',
                                 type=str)

    def parse_args(self):
        args = self.parser.parse_args()

        log_format = "[%(filename)s:%(lineno)s] %(message)s"
        if args.debug:
            logging.basicConfig(format=log_format, level=logging.DEBUG)
        else:
            logging.basicConfig(format=log_format)

        self.origin_file = getattr(args, 'input-file')

        self.backup_file = self.origin_file + ".bak"

        i = 0
        while os.path.exists(self.backup_file):
            self.backup_file = self.origin_file + ".b" + format(i, '02d')
            i += 1

        if args.pause:
            self.pause = True

    def show_args(self):
        print('Input file :', self.origin_file)
        print('Backup file :', self.backup_file)
        print('Pause :', self.pause)

    def open(self):
        try:
            os.renames(self.origin_file, self.backup_file)
        except FileNotFoundError:
            print("Input file is not found !!!")
            return False
        except OSError:
            print("Fail to backup input file !!!")
            return False
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return False

        try:
            self.f_backup = open(self.backup_file, 'r')
        except OSError:
            os.renames(self.backup_file, self.origin_file)
            print("Couldn't open backup file: ", self.backup_file)
            return False

        try:
            self.f_origin = open(self.origin_file, 'w')
        except OSError:
            self.f_backup.close()
            os.renames(self.backup_file, self.origin_file)
            print("Couldn't open origin file: ", self.origin_file)
            return False

    def close(self):
        self.f_origin.close()
        self.f_backup.close()

    def generic_parser(self, line, i):
        if 'KISSlicer' in line:
            logging.debug('Line ' + str(i) + ': Find KISSlicer')
            self.comment_parser = self.kisslicer_parser

    def kisslicer_parser(self, line, i):
        if 'BEGIN_LAYER_OBJECT' in line:
            data = line.split('z=', 1)[1]
            data = data.split(' ', 1)[0]
            self.z = float(data)
            logging.debug('Line ' + str(i) + ': Height = ' + str(self.z))

    def gcode_parser(self, line, i):
        if line.find('M83') == 0 or line.find('m83') == 0:
            self.relative_extruder = True
        if line.find('M82') == 0 or line.find('m82') == 0:
            self.relative_extruder = False

    def process(self):
        ret = self.open()
        if ret is False:
            return

        for i, line in enumerate(self.f_backup, 1):
            if line[0] == ';':
                self.comment_parser(line, i)
            else:
                self.gcode_parser(line, i)

            # modify G-code here
            self.f_origin.write(line)

        self.close()


if __name__ == '__main__':
    gmod = GmodBase()
    gmod.parse_args()
    gmod.show_args()
    gmod.process()
    if gmod.pause is True:
        print('')
        os.system('pause')


