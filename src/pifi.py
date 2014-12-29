#!/usr/bin/python
# -*- coding: utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

from lib.machine import ZMachine
from plugins.qtplugin import QtPlugin
from plugins.qtplugin_v2 import QtPluginV2
from plugins.qtplugin_v3 import QtPluginV3
import sys
import argparse
import signal

__author__="Theofilos Intzoglou"
__date__ ="$17 Ιουν 2009 2:24:30 πμ$"

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal.SIG_DFL) # Break on control-c

    # @type f file
    # @type parser argparse.ArgumentParser
    parser = argparse.ArgumentParser(description='PiFi - Python Interactive Fiction Interpreter')
    parser.add_argument('-p', '--plugin', help='specify the plugin to use; use QtPlugin for now', default='QtPluginV2')
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
    # Initialize the appropriate plugin
    if args.plugin in globals() and isinstance(globals()[args.plugin], type):
        plugin = globals()[args.plugin]()
    else:
        print "Plugin " + args.plugin + " not found!"
        sys.exit(3)

    plugin.prepare_gui()
    plugin.set_debug_level(args.log_level)
    m = ZMachine(plugin) # Attach plugin to ZMachine
    m.load_story(f)
    plugin.set_zversion(m.zver) # Store version of z-code file
    m.init()
    m.boot()
    plugin.exec_() # Start exec loop
