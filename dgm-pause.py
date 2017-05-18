#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dinow g-code modifier for KISSlicer - Pause at height

Created on Sun Apr 30 12:10:11 2017

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
                        help='The height to pause',
                        type=float,
                        nargs='+')

    parser.add_argument('-z', '--zlift',
                        help='The height to lift before pause',
                        type=float,
                        default=10.0)

    parser.add_argument('-x', '--x_loc',
                        help='The x-axis location to pause',
                        type=float,
                        default=None)

    parser.add_argument('-y', '--y_loc',
                        help='The y-axis location to pause',
                        type=float,
                        default=None)

    parser.add_argument('-c', '--cooldown',
                        help='Cool down extruder after printer is paused',
                        action='store_true')

    return parser.parse_args()


def add_pause_control(
        inputFile, outputFile, height,
        zlift, x_loc, y_loc, cooldown=False):
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

    lineNum = 1
    line = fInput.readline()
    if line.find('KISSlicer') == -1:
        fOutput.close()
        fInput.close()
        print("Input file is not a KISSlicer gcode file.")
        return False
    fOutput.write(line)

    hIndex = 0
    zTarget = height[hIndex]
    use_destring = 0
    destring_suck = 6.0
    destring_suck_speed = 80.0
    cur_temp = 0

    for line in fInput:
        lineNum += 1
        if line.find('use_destring ') >= 0:
            dummy, data_str = line.rsplit('=', 1)
            use_destring = int(data_str)
            logging.debug('use_destring = ' + str(use_destring))
        elif line.find('destring_suck ') >= 0:
            dummy, data_str = line.rsplit('=', 1)
            destring_suck = float(data_str)
            logging.debug('destring_suck = ' + str(destring_suck))
        elif line.find('destring_suck_speed_mm_per_s ') >= 0:
            dummy, data_str = line.rsplit('=', 1)
            destring_suck_speed = float(data_str)
            logging.debug('destring_suck_speed = ' + str(destring_suck_speed))
        elif line.find('M109') == 0 or line.find('M104') == 0:
            gcode = line.split(';', 1)
            dummy, data_str = gcode[0].rsplit('S', 1)
            cur_temp = int(data_str)
            logging.debug('Line' + str(lineNum) + ' Temp = ' + str(cur_temp))
        elif line.find('BEGIN_LAYER_OBJECT') >= 0:
            dummy, data_str = line.rsplit('=', 1)
            z = float(data_str)
            if z >= zTarget:
                print('Line :', lineNum, 'Pause at', z, 'mm')
                hIndex += 1
                zTarget = height[hIndex]

                fOutput.write(';BEGIN_PAUSE_PROCESS\n')
                fOutput.write('G1 Z' + str(z + zlift) +
                              ' ; Lift extruder before pause\n')

                if x_loc or y_loc:
                    fOutput.write('G1')
                    if x_loc:
                        fOutput.write(' X' + str(x_loc))
                    if y_loc:
                        fOutput.write(' Y' + str(y_loc))
                    fOutput.write(' ; Move to pause location\n')

                if cooldown:
                    fOutput.write('M104 S0\n')
                    fOutput.write('M0 ; Pause\n')
                    fOutput.write('M109 S' + str(cur_temp) + '\n')

                fOutput.write('M0 ; Pause\n')

                if use_destring == 1:
                    fOutput.write('G1 E-' + str(destring_suck) +
                                  ' F' + str(destring_suck_speed*60) +
                                  '; Destring Suck\n')
                    fOutput.write('G92 E0 ; Reset extruder pos\n')
                fOutput.write(';END_PAUSE_PROCESS\n')
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

    height = sorted(args.height) + [float("inf")]
    # logging.debug('output :' + output_file)
    print('')
    print('Input file :', input_file)
    print('Backup file :', backup_file)
    print('Pause at', sorted(args.height))
    print('Lift extruder', args.zlift, 'mm before pause')
    print('Move extruder to (', args.x_loc, ',', args.y_loc, ')')
    print('Cooldown :', args.cooldown)
    print('')

    try:
        os.renames(input_file, backup_file)
        ret = add_pause_control(
                backup_file, input_file, height,
                args.zlift, args.x_loc, args.y_loc,
                args.cooldown)

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
