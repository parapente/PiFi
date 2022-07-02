#!/usr/bin/python3
# -*- coding: utf-8
""" Python Interactive Fiction Interpreter """

from lib.machine import ZMachine
from importlib import reload, import_module
from pkgutil import iter_modules
import sys
import argparse
import signal

__author__ = "Theofilos Intzoglou"
__date__ = "$17 Ιουν 2009 2:24:30 πμ$"

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Break on control-c

    # @type f file
    # @type parser argparse.ArgumentParser
    parser = argparse.ArgumentParser(
        description='PiFi - Python Interactive Fiction Interpreter')
    parser.add_argument(
        '-p',
        '--plugin',
        help='specify the plugin to use; use QtPlugin for now',
        default='QtPluginV3'
    )
    parser.add_argument(
        '-P',
        '--list-plugins',
        action='store_true',
        help='list all available plugins'
    )
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-l', '--log-level', type=int, default=0,
                        help='debug log level (0-2); default: %(default)s')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s 0.1')
    parser.add_argument('zfile')
    args = parser.parse_args()

    discovered_plugins = {
        name.removeprefix('plugin_'): import_module('plugins.' + name)
        for _, name, _
        in iter_modules(path=['plugins'])
        if name.startswith('plugin_')
    }

    if args.list_plugins:
        for plugin_name in discovered_plugins.keys():
            print(plugin_name)
        exit(0)

    try:
        f = open(args.zfile, 'rb')
    except IOError as cannot_open_file:
        (errno, strerror) = cannot_open_file.args
        print("I/O error ({0}): {1}".format(errno, strerror))
        sys.exit(2)

    reload(sys)
    # Initialize the appropriate plugin
    if args.plugin not in discovered_plugins:
        print("Plugin " + args.plugin + " not found!")
        sys.exit(3)

    class_name = args.plugin
    plugin = getattr(discovered_plugins[args.plugin], class_name)()

    plugin.prepare_gui()
    plugin.set_debug_level(args.log_level)
    m = ZMachine(plugin)  # Attach plugin to ZMachine
    m.load_story(f)
    plugin.set_zversion(m.zver)  # Store version of z-code file
    m.init()
    m.boot()
    plugin.exec_()  # Start exec loop
