# -*- coding: utf-8

from typing import Callable
from lib.window import ZWindow
from lib.stream import ZStream
import sys

__author__ = "Theofilos Intzoglou"
__date__ = "$9 Ιαν 2011 1:56:17 πμ$"


class PluginSkeleton(object):

    def __init__(self):
        self._output_stream = [ZStream(), ZStream(), ZStream(), ZStream()]
        self._output_stream[0].selected = True
        self.level = 0  # Default debug level

    def prepare_gui(self) -> None:
        # Nothing to do
        pass

    def set_debug_level(self, level: int) -> None:
        self.level = level

    def debug_print(self, msg, level: int) -> None:
        if (level <= self.level):
            print(msg)
            sys.stdout.flush()

    def set_zversion(self, zver: int) -> None:
        self.zver = zver
        if (zver < 3):
            self.window = [ZWindow(0)]
        elif (zver == 6):
            self.window = [ZWindow(0), ZWindow(1), ZWindow(2), ZWindow(3),
                           ZWindow(4), ZWindow(5), ZWindow(6), ZWindow(7)]
        else:
            self.window = [ZWindow(0), ZWindow(1)]
            # The upper window is a special type of window
            self.window[1].set_buffering(False)
            self.window[1].set_wrapping(False)
            self.window[1].set_scrolling(False)
        self.current_window = 0

    def exec_(self) -> None:
        # Nothing to do
        pass

    def show_cursor(self) -> None:
        self.widget.show_cursor()

    def hide_cursor(self) -> None:
        self.widget.hide_cursor()

    def read_char(self, callback: Callable, time: int,
                  timeout_callback: Callable):
        self.widget.read_char(
            self.window[self.current_window], callback, time, timeout_callback)

    def read_line(self, callback: Callable, time: int,
                  timeout_callback: Callable, reset: bool) -> None:
        self.read_line_enabled = True
        self.widget.read_line(
            self.window[self.current_window],
            callback,
            time,
            timeout_callback,
            reset
        )

    def set_max_input(self, max_input: int) -> None:
        self.widget.set_max_input(max_input)

    def disconnect_input(self, callback: Callable):
        if self.read_line_enabled:
            self.widget.disconnect_read_line(callback)
            self.read_line_enabled = False
        else:
            self.widget.disconnect_read_char(callback)

    def print_string(self, string: str) -> None:
        self.widget.print_string(string)

    def print_status(self, room: str, status: str) -> None:
        self.widget.print_status(room, status)

    def clear_screen(self) -> None:
        self.widget.clear()

    def set_font_style(self, style: int) -> None:
        window = self.current_window
        self.widget.set_font_style(style, window)

    def show_upper_window(self, lines: int) -> None:
        self.split_window(lines, self.zver)

    def set_window(self, window: int) -> None:
        self.current_window = window
        if (self.zver != 6 and window == 1):
            self.window[1].set_cursor_position(1, 1)

    def set_cursor(self, x: int, y: int) -> None:
        if (self.current_window == 1):
            self.window[1].set_cursor_position(x, y)

    def set_colour(self, fg: int, bg: int) -> None:
        win = self.current_window
        widget = self.widget
        if (fg != 0):
            if fg == 1:
                widget.set_text_colour(self.def_fg, win)
            else:
                widget.set_text_colour(fg, win)
        if (bg != 0):
            if bg == 1:
                widget.set_text_background_colour(self.def_bg, win)
            else:
                widget.set_text_background_colour(bg, win)

    def width(self) -> int:
        return self.widget.width

    def height(self) -> int:
        return self.widget.height

    def new_line(self) -> None:
        self.widget.new_line()

    def set_default_bg(self, bg: int) -> None:
        self.def_bg = bg

    def set_default_fg(self, fg: int) -> None:
        self.def_fg = fg

    def set_font(self, font_num: int) -> int:
        if font_num == 1 or font_num == 3:
            res = self.zfont
            self.zfont = font_num
            return res
        else:
            return 0

    def selected_output_streams(self) -> list[int]:
        s = []
        for i in range(4):
            if self._output_stream[i].selected is True:
                s.append(i+1)
        return s

    def select_output_stream(self, n: int) -> None:
        if n != 0:
            self._output_stream[n - 1].selected = True

    def deselect_output_stream(self, n: int) -> None:
        self._output_stream[n - 1].selected = False

    def update_screen_size(self) -> None:
        self.screen_size_callback(self.width(), self.height())
        print(self.width(), self.height())

    def erase_window(self, window: int) -> None:
        self.widget.erase_window(self.window[window])

    def stop_line_timer(self) -> None:
        self.widget.stop_line_timer()

    def stop_char_timer(self) -> None:
        self.widget.stop_char_timer()

    def quit(self) -> None:
        # Nothing to do
        pass

    def unsplit(self) -> None:
        # Nothing to do
        pass
