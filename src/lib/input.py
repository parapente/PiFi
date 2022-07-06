# -*- coding: utf-8

from lib.stream import ZStream
from plugins.plugskel import PluginSkeleton
from typing import Callable

__author__ = "Theofilos Intzoglou"
__date__ = "$1 Ιουλ 2009 6:24:20 μμ$"


class ZInput:
    stream = None
    plugin = None

    def __init__(self, p: PluginSkeleton):
        self.stream = [ZStream(), ZStream()]
        self.plugin = p

    def set_current(self, n: int) -> None:
        if n == 0:
            self.stream[1].selected = True
            self.stream[2].selected = False
        else:
            self.stream[1].selected = False
            self.stream[2].selected = True

    def read_char(self, callback: Callable, time: int, timeout_callback: Callable) -> None:
        self.plugin.read_char(callback, time, timeout_callback)

    def read_line(self, max_read: int, callback: Callable, time: int, timeout_callback: Callable, reset: bool = True) -> None:
        self.plugin.set_max_input(max_read)
        self.plugin.show_cursor()
        self.plugin.read_line(callback, time, timeout_callback, reset)

    def disconnect_input(self, callback: Callable) -> None:
        self.plugin.disconnect_input(callback)

    def stop_line_timer(self) -> None:
        self.plugin.stop_line_timer()

    def stop_char_timer(self) -> None:
        self.plugin.stop_char_timer()

    def hide_cursor(self) -> None:
        self.plugin.hide_cursor()
