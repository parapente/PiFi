# -*- coding: utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

from typing import Callable
from plugins.qtztextwidget import ZTextWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from plugins.plugskel import PluginSkeleton

__author__ = "Theofilos Intzoglou"
__date__ = "$20 Σεπ 2009 2:39:20 μμ$"


class QtPlugin(PluginSkeleton):
    widget = None
    win = None
    zver = None
    read_line_enabled = False
    def_bg = 2  # Black
    def_fg = 9  # White
    zfont = 1  # Normal z-font

    def prepare_gui(self) -> None:
        self.a = QtWidgets.QApplication([])
        mainframe = QtWidgets.QFrame()
        hbl = QtWidgets.QHBoxLayout()
        hbl.addWidget(QtWidgets.QLabel())
        hbl.addWidget(QtWidgets.QLabel())
        hbl.itemAt(0).widget().setVisible(False)
        hbl.itemAt(1).widget().setVisible(False)
        hbl.itemAt(1).widget().setAlignment(
            QtCore.Qt.Alignment(QtCore.Qt.AlignRight))
        hbl.itemAt(1).widget().setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.widget = ZTextWidget()
        vbl = QtWidgets.QVBoxLayout()
        vbl.addLayout(hbl)
        vbl.addWidget(self.widget)
        mainframe.setLayout(vbl)
        self.win = QtWidgets.QMainWindow()
        self.read_line_enabled = False
        # rect = QtCore.QRect()
        # rect.setWidth(640)
        # rect.setHeight(480)
        # win.setGeometry(rect)
        self.win.setCentralWidget(mainframe)
        self.win.show()

    def exec_(self) -> None:
        self.a.exec_()

    def set_zversion(self, zver: int) -> None:
        self.zver = zver

    def show_cursor(self) -> None:
        self.widget.show_cursor()

    def hide_cursor(self) -> None:
        self.widget.hide_cursor()

    def read_char(self, callback: Callable, time: int,
                  timeout_callback: Callable) -> None:
        self.widget.read_char(callback)

    def read_line(self, callback: Callable, time: int,
                  timeout_callback: Callable, reset: bool) -> None:
        self.read_line_enabled = True
        self.widget.read_line(callback)

    def set_max_input(self, max_input: int) -> None:
        self.widget.set_max_input(max_input)

    def disconnect_input(self, callback: Callable) -> None:
        if self.read_line_enabled:
            self.widget.disconnect_read_line(callback)
            self.read_line_enabled = False
        else:
            self.widget.disconnect_read_char(callback)

    def select_output_stream(self, stream: int) -> None:
        self.widget.select_output_stream(stream)

    def deselect_output_stream(self, stream: int) -> None:
        self.widget.deselect_output_stream(stream)

    def print_string(self, string: str) -> None:
        self.widget.print_string(string)

    def print_status(self, room: str, status: str) -> None:
        vbl = self.win.centralWidget().layout()
        hbl = vbl.itemAt(0).layout()
        s1 = hbl.itemAt(0).widget()
        if not s1.isVisible():
            s1.setVisible(True)
        s2 = hbl.itemAt(1).widget()
        if not s2.isVisible():
            s2.setVisible(True)
        s1.setText(room)
        s2.setText(status)

    def clear_screen(self) -> None:
        self.widget.clear()

    def set_font_style(self, style: int) -> None:
        self.widget.set_font_style(style)

    def show_upper_window(self, lines: int) -> None:
        self.widget.split_window(lines, self.zver)

    def set_window(self, window: int) -> None:
        self.widget.set_window(window)

    def set_cursor(self, x: int, y: int) -> None:
        self.widget.set_cursor(x, y)

    def set_colour(self, fg: int, bg: int) -> None:
        if fg == 1:
            self.widget.set_text_colour(self.def_fg)
        elif fg > 1 and fg < 13:
            self.widget.set_text_colour(fg)
        if bg == 1:
            self.widget.set_text_background_colour(self.def_bg)
        elif bg > 1 and bg < 13:
            self.widget.set_text_background_colour(bg)

    def selected_output_streams(self) -> list[int]:
        return self.widget.selected_output_streams()

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

    def split_window(self, lines: int, version: int) -> None:
        self.widget.split_window(lines, version)

    def erase_window(self, window: int) -> None:
        # TODO: implement
        pass
