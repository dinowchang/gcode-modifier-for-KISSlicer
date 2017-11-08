#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 2017/10/31

@author: dinowchang
"""
import logging
from gmod_base import GmodBase


class GmodPause(GmodBase):
    def __init__(self):
        GmodBase.__init__(self)
        self.pause = []
        self.z_lift = 0
        self.x_loc = None
        self.y_loc = None
        self.cool_down = False
        self.retraction_l = 0
        self.retraction_s = 1200
        self.h_index = 0
        self.h_target = 0

        self.parser.add_argument('height',
                                 help='The height list to pause',
                                 type=float,
                                 nargs='+')

        self.parser.add_argument('-z', '--z_lift',
                                 help='The height to lift before pause, default: %(default)s mm',
                                 type=float,
                                 default=5.0)

        self.parser.add_argument('-x', '--x_loc',
                                 help='The x-axis location to park when paused. ' +
                                      'The head won\'t move if this value is not set.',
                                 type=float,
                                 default=None)

        self.parser.add_argument('-y', '--y_loc',
                                 help='The y-axis location to park when paused. ' +
                                      'The head won\'t move if this value is not set.',
                                 type=float,
                                 default=None)

        self.parser.add_argument('-c', '--cool_down',
                                 help='Cool down the extruder when printer is paused. ' +
                                      'The 1st resume will warm up extruder then pause again.',
                                 action='store_true')

        self.parser.add_argument('-rl', '--retraction_length',
                                 help='The length to retract before printer is paused, default: %(default)s mm',
                                 type=float,
                                 default=0)

        self.parser.add_argument('-rs', '--retraction_speed',
                                 help='The speed of retraction before printer is paused, default: %(default)s mm/s',
                                 type=int,
                                 default=20)

    def parse_args(self):
        args = GmodBase.parse_args(self)
        self.pause = sorted(args.height) + [float("inf")]
        self.z_lift = args.z_lift
        self.x_loc = args.x_loc
        self.y_loc = args.y_loc
        self.cool_down = args.cool_down
        self.retraction_l = args.retraction_length
        self.retraction_s = args.retraction_speed * 60

        self.h_target = self.pause[self.h_index]

    def show_args(self):
        GmodBase.show_args(self)
        print('Pause at height :', self.pause[:-1])
        print('Lift extruder', self.z_lift)
        print('Move extruder to (', self.x_loc, ',', self.y_loc, ')')
        print('Cool down :', self.cool_down)
        print('Retraction :', self.retraction_l, 'mm', self.retraction_s / 60, 'mm/s')

    def gcode_mod(self, line, i):
        if self.height >= self.h_target:
            logging.debug(
                'Line ' + str(i) + ': Insert pause G-code, height = ' + str(self.height))
            self.write(line)
            self.h_index += 1
            self.h_target = self.pause[self.h_index]

            self.write('; BEGIN_PAUSE_PROCESS\n')
            # lift z
            self.write('G91 ; Relative position mode\n')
            self.write('G1 Z' + str(self.z_lift) + ' ; Lift extruder before pause\n')

            # retraction
            if self.retraction_l > 0:
                if self.relative_extruder is False:
                    self.write('M83 ; Relative Extruder mode\n')
                self.write('G1 E-' + str(self.retraction_l) +
                           ' F' + str(self.retraction_s) +
                           '; Retraction\n')
                if self.relative_extruder is False:
                    self.write('M82 ; Absolute Extruder mode\n')
                    self.write('G92 E0 ; Reset extruder pos\n')

            # move to parking position
            self.write('G90 ; Absolute position mode\n')
            if self.x_loc or self.y_loc:
                self.write('G1')
                if self.x_loc:
                    self.write(' X' + str(self.x_loc))
                if self.y_loc:
                    self.write(' Y' + str(self.y_loc))
                self.write(' ; Move to pause location\n')
            if self.relative_position is True:
                self.write('G91 ; Relative position mode\n')

            # beep
            self.write('M300 S880 P1000 ; Beep\n')

            #  cool down
            if self.cool_down is True:
                self.write('M104 S0 ; Cool down\n')
                self.write('M0 ; Pause\n')
                self.write('M109 S' + str(self.temperature) + ' ; Warm up\n')

            #  pause
            self.write('M0 ; Pause\n')
            self.write('; END_PAUSE_PROCESS\n')
            return True

        return False


if __name__ == '__main__':
    gmod = GmodPause()
    gmod.parse_args()
    gmod.show_args()
    gmod.process()
