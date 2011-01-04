#!/usr/bin/python
# -*- coding: utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

from lib.machine import ZMachine
from plugins.qtplugin import QtPlugin
import sys

__author__="oscar"
__date__ ="$17 Ιουν 2009 2:24:30 πμ$"

if __name__ == "__main__":

    # @type f file
    if ( len(sys.argv) == 1 or len(sys.argv[1]) == 0 or (sys.argv[1] == "-p" and len(sys.argv) < 4) or (sys.argv[1] <> "-p" and len(sys.argv) < 2)):
        print "Usage: ",sys.argv[0],"[-p <plugin name>] <z-code file>"
        print "Default plugin: QtPlugin"
        sys.exit(1);

    # TODO: Handle -p option

    try:
        f = open(sys.argv[1],'rb');
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