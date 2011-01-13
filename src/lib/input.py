# -*- coding: utf-8

from stream import ZStream

__author__="Theofilos Intzoglou"
__date__ ="$1 Ιουλ 2009 6:24:20 μμ$"

class ZInput:
    stream = None
    plugin = None

    def __init__(self,p):
        self.stream = [ZStream(), ZStream()]
        self.plugin = p

    def set_current(self,n):
        if n == 0:
            self.stream[1].selected = True
            self.stream[2].selected = False
        else:
            self.stream[1].selected = False
            self.stream[2].selected = True

    def read_char(self, callback):
        self.plugin.show_cursor()
        self.plugin.read_char(callback)

    def read_line(self, max_read, callback):
        self.plugin.set_max_input(max_read)
        self.plugin.show_cursor()
        self.plugin.read_line(callback)

    def disconnect_input(self, callback):
        self.plugin.disconnect_input(callback)

    def hide_cursor(self):
        self.plugin.hide_cursor()