#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dinow g-code modifier for KISSlicer - Turn off headbed at height

Created on Mon May  1 14:55:47 2017

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

    parser.add_argument('height',
                        help='The height to turn off heatbed',
                        type=float)

    return parser.parse_args()


def add_headbed_off_control(input_file, output_file, height):
    try:
        fInput = open(input_file, 'r')
    except OSError:
        print("Couldn't open input file: ", input_file)
        return False

    try:
        fOutput = open(output_file, 'w')
    except OSError:
        fInput.close()
        print("Couldn't open output file: ", output_file)
        return False

    lineNum = 1
    line = fInput.readline()
    if not 'KISSlicer' in line:
        fOutput.close()
        fInput.close()
        print("Input file is not a KISSlicer gcode file.")
        return False

    fOutput.write(line)

    zTarget = height

    for line in fInput:
        lineNum += 1
        fOutput.write(line)

        if 'BEGIN_LAYER_OBJECT' in line:
            data_str = line.split('z=', 1)[1]
            data_str = data_str.split(' ', 1)[0]
            z = float(data_str)
            if z >= zTarget:
                print('Line :', lineNum, 'Turn off heatbed at', z, 'mm')
                fOutput.write('M140 S0	; Turn off heatbed\n')
                break

    for line in fInput:
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
    print('Turn off heatbed at', args.height, 'mm')
    print('')

    try:
        os.renames(input_file, backup_file)
        ret = add_headbed_off_control(backup_file, input_file, args.height)
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
