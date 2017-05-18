#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dinow g-code modifier for KISSlicer - Temperature Tower

Created on Fri Feb 24 23:56:05 2017

@author: dinowchang
"""

import argparse
import logging
import os
import sys


def parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug',
                        help='Enable debug mode',
                        action='store_true')

    parser.add_argument('-p', '--pause',
                        help='Pause before exit',
                        action='store_true')

    parser.add_argument('input-file',
                        help='Input gcode file',
                        type=str)

    parser.add_argument('-zo', '--z-offset',
                        help='The height of first test block',
                        type=float,
                        default=1.8)

    parser.add_argument('-zs', '--z-step',
                        help='The thickness of each test block',
                        type=float,
                        default=7.0)

    parser.add_argument('-to', '--temp-offset',
                        help='The temperature of first test block',
                        type=int,
                        default=220)

    parser.add_argument('-ts', '--temp-step',
                        help='The temperature increased for each test block',
                        type=int,
                        default=-5)

    return parser.parse_args()


def add_temp_control(inputFile, outputFile, zOffset, zStep, tOffset, tStep):
    try:
        fInput = open(inputFile, 'r')
    except OSError:
        print("Couldn't open input file: ", inputFile)
        return False

    try:
        fOutput = open(outputFile, 'w')
    except OSError:
        fInput.close()
        print("Couldn't open output file: ", outputFile)
        return False

    zTarget = zOffset
    tTaeget = tOffset

    lineNum = 1
    line = fInput.readline()
    if line.find('KISSlicer') == -1:
        fOutput.close()
        fInput.close()
        print("Input file is not a KISSlicer gcode file.")
        return False

    fOutput.write(line)

    for line in fInput:
        lineNum += 1
        if line.find('BEGIN_LAYER_OBJECT') >= 0:
            fOutput.write(line)
            dummy, data_str = line.rsplit('=', 1)
            z = float(data_str)
            if z >= zTarget:
                fOutput.write('M109 S' + str(tTaeget) + '\n')
                lineNum += 1
                print('Set temperature to', tTaeget, 'C at', z, 'mm ( line',
                      lineNum, ')')
                zTarget += zStep
                tTaeget += tStep
        elif line.find('M109 S') == 0:
            if zTarget == zOffset:
                # Base
                fOutput.write('M109 S' + str(tTaeget) + '\n')
                print('Modity temperature to', tTaeget, 'C at line', lineNum)
            else:
                # Test block
                fOutput.write('M109 S' + str(tTaeget-tStep) + '\n')
                print('Modity temperature to', tTaeget, 'C at line', lineNum)
        else:
            fOutput.write(line)

    fOutput.close()
    fInput.close()
    return True


def main():
    args = parser()
    FORMAT = "[%(filename)s:%(lineno)s] %(message)s"
    if args.debug:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    else:
        logging.basicConfig(format=FORMAT)

    input_file = getattr(args, 'input-file')

    backup_file = input_file + ".bak"
    i = 0
    while os.path.exists(backup_file):
        backup_file = input_file + ".b" + format(i, '02d')
        i += 1

    print('')
    print('Input file :', input_file)
    print('Backup file :', backup_file)
    print('Z offset :', args.z_offset, 'mm')
    print('Z step :', args.z_step, 'mm')
    print('Temperature offset :', args.temp_offset, 'C')
    print('Temperature step :', args.temp_step, 'C')
    print('')

    try:
        os.renames(input_file, backup_file)
        ret = add_temp_control(backup_file, input_file,
                               args.z_offset, args.z_step,
                               args.temp_offset, args.temp_step)

        if not ret:
            os.renames(backup_file, input_file)

    except FileNotFoundError:
        print("Input file is not found !!!")
    except OSError:
        print("Fail to backup input file !!!")
    except:
        print("Unexpected error:", sys.exc_info()[0])

    if args.pause:
        print('')
        os.system('pause')


if __name__ == '__main__':
    main()
