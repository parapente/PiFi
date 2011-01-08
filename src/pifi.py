#!/usr/bin/python
# -*- coding: utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

from lib.machine import ZMachine
from plugins.qtplugin import QtPlugin
import sys
import argparse

__author__="oscar"
__date__ ="$17 Ιουν 2009 2:24:30 πμ$"

if __name__ == "__main__":

    # @type f file
    # @type parser argparse.ArgumentParser
    parser = argparse.ArgumentParser(description='PiFi - Python Interactive Fiction Interpreter')
    parser.add_argument('-p', '--plugin', help='specify the ouput plugin to use; use QtPlugin for now')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-l', '--log-level', type=int, default=0, help='debug log level (0-2); default: %(default)s')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('zfile')
    args = parser.parse_args()

    try:
        f = open(args.zfile,'rb');
        #f = open("/home/oscar/games/wcastle.z5",'rb');
    except IOError as (errno,strerror):
        print "I/O error ({0}): {1}".format(errno,strerror)
        sys.exit(2)

    reload(sys)
    sys.setdefaultencoding("utf-8")
    plugin = QtPlugin()
    m = ZMachine(plugin)
    plugin.set_zversion(m.zver)
    m.load_story(f)
    m.init()
    m.boot()
    plugin.exec_()