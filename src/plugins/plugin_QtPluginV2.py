# -*- coding: utf-8

from plugins.qtztextwidget_v2 import ZTextWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from .plugskel import PluginSkeleton
import traceback
import sys

__author__ = "Theofilos Intzoglou"
__date__ = "$20 Σεπ 2009 2:39:20 μμ$"


class QtPluginV2(PluginSkeleton):
    win = None
    zver = None
    rline = False
    def_bg = 2  # Black
    def_fg = 9  # White
    zfont = 1  # Normal z-font
    current_window = 0

    def prepare_gui(self):
        print("This is an experimental plugin, not ready for use...")
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
        self.rline = False
        self.win.setCentralWidget(mainframe)
        self.win.show()

    def exec_(self):
        sys.exit(self.a.exec_())

    def print_status(self, room, status):
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

    def new_line(self):
        self.widget.prints('\n', self.window[self.current_window])

    def prints(self, s):
        if (self._output_stream[0].selected == True):
            self.widget.prints(s, self.window[self.current_window])

    def split_window(self, lines, ver):
        if (ver == 6):
            traceback.print_stack()
            sys.exit()
        else:
            if (self.window[1].line_count < lines):
                self.window[1].set_cursor_position(1, 1)
                self.window[1].set_cursor_real_position(
                    2, self.widget.linesize)
            self.window[1].set_line_count(lines)
            self.widget.split_window(lines, ver)

    def show_cursor(self):
        self.widget.show_cursor(self.window[self.current_window])

    def hide_cursor(self):
        self.widget.hide_cursor(self.window[self.current_window])

    def set_window(self, w):
        self.current_window = w
        if (self.zver != 6 and w == 1):
            self.window[1].set_cursor_position(1, 1)
            self.widget.update_real_cursor_position(self.window[1])

    def set_cursor(self, x, y):
        if (self.current_window == 1):
            self.window[1].set_cursor_position(x, y)
            self.widget.update_real_cursor_position(self.window[1])

    def quit(self):
        self.win.close()

    def unsplit(self):
        self.widget.pbuffer_painter = [None]*8
        self.widget.pbuffer = [None]*8
        self.widget.init0()
