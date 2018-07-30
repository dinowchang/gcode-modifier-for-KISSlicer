#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 2017/10/25

@author: dinowchang
"""

import argparse
import logging
import os


class GmodBase:

    def __init__(self):
        # process parameter
        self.origin_file = ""
        self.backup_file = ""
        self.f_origin = None
        self.f_backup = None
        self.pause = False
        self.test_only = False
        self.comment_parser = self.generic_parser

        # g-code state
        self.pos = [None, None, None]
        self.ext_pos = None
        self.ext_prev_pos = None
        self.begin_of_layer = False
        self.height = 0
        self.layer = 0
        self.relative_position = False
        self.relative_extruder = False
        self.temperature = 0

        self.parser = argparse.ArgumentParser()

        self.parser.add_argument('-p', '--pause',
                                 help='Pause before exit',
                                 action='store_true')

        self.parser.add_argument('-d', '--debug',
                                 help='Enable debug mode',
                                 action='store_true')

        self.parser.add_argument('--test',
                                 help='Run test flow only, won\'t modity file.',
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

        if args.test:
            self.test_only = True
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

        return args

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

    def write(self, line):
        self.f_origin.write(line)

    def close(self):
        self.f_origin.close()
        self.f_backup.close()

    def generic_parser(self, line, i):
        if 'KISSlicer' in line:
            logging.debug('Line ' + str(i) + ': g-code is generated by KISSlicer')
            self.comment_parser = self.kisslicer162_parser


    def kisslicer162_parser(self, line, i):
        if 'version' in line:
            data = line.split(' ')[2]
            logging.debug('Line ' + str(i) + ': KISSlicer ver: ' + str(data))
            if data != "1.6.2":
                print("KISSlicer ver " + data + " maybe not supported correctly.")

        if 'BEGIN_LAYER_OBJECT' in line:
            self.begin_of_layer = True
            data = line.split('z=', 1)[1]
            data = data.split(' ', 1)[0]
            self.height = float(data)
            self.layer += 1
            # logging.debug('Line ' + str(i) + ': Height = ' + str(self.height))
        else:
            self.begin_of_layer = False

    def gcode_parser(self, line, _):
        line = line.upper().split(';', 1)[0]
        if line.startswith('M83'):
            self.relative_extruder = True
        if line.startswith('M82'):
            self.relative_extruder = False
        if line.startswith('G91'):
            self.relative_position = True
        if line.startswith('G90'):
            self.relative_position = False
        if line.startswith('M109') or line.startswith('M104'):
            data = line.split(';', 1)[0]
            data = data.rsplit('S', 1)[1]
            data = data.split(' ', 1)[0]
            self.temperature = float(data)
        if line.startswith('G28'):
            if 'X' not in line and 'Y' not in line and 'Z' not in line:
                self.pos = [0, 0, 0]
            else:
                if 'X' in line:
                    self.pos[0] = 0
                if 'Y' in line:
                    self.pos[1] = 0
                if 'Z' in line:
                    self.pos[2] = 0

    def gcode_mod(self, line, i):
        """  rewrite this method to modify gcode
                return True if you don't want to write line back"""
        return False

    def process(self):
        ret = self.open()
        if ret is False:
            if self.pause is True:
                print('')
                os.system('pause')
            return

        for i, line in enumerate(self.f_backup, 1):
            if line[0] == ';':
                self.comment_parser(line, i)
            else:
                self.gcode_parser(line, i)

            ret = self.gcode_mod(line, i)
            if ret is False:
                self.write(line)

        self.close()

        if self.pause is True:
            print('')
            os.system('pause')


    def test_flow(self):
        try:
            self.f_origin = open(self.origin_file, 'r')
        except OSError:
            print("Couldn't open origin file: ", self.origin_file)
            return

        for i, line in enumerate(self.f_origin, 1):
            if line[0] == ';':
                self.comment_parser(line, i)
            else:
                self.gcode_parser(line, i)

        self.f_origin.close()


if __name__ == '__main__':
    gmod = GmodBase()
    gmod.parse_args()
    gmod.show_args()
    if gmod.test_only:
        gmod.test_flow()
    else:
        gmod.process()

