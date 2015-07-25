# -*- coding: utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

from plugins.qtztextwidget import ZTextWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from plugins.plugskel import PlugSkel

__author__="Theofilos Intzoglou"
__date__ ="$20 Σεπ 2009 2:39:20 μμ$"

class QtPlugin(PlugSkel):
    widget = None
    win = None
    zver = None
    rline = False
    def_bg = 2 # Black
    def_fg = 9 # White
    zfont = 1 # Normal z-font

    def prepare_gui(self):
        self.a = QtWidgets.QApplication([])
        mainframe = QtWidgets.QFrame()
        hbl = QtWidgets.QHBoxLayout()
        hbl.addWidget(QtWidgets.QLabel())
        hbl.addWidget(QtWidgets.QLabel())
        hbl.itemAt(0).widget().setVisible(False)
        hbl.itemAt(1).widget().setVisible(False)
        hbl.itemAt(1).widget().setAlignment(QtCore.Qt.Alignment(QtCore.Qt.AlignRight))
        hbl.itemAt(1).widget().setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.widget = ZTextWidget()
        vbl = QtWidgets.QVBoxLayout()
        vbl.addLayout(hbl)
        vbl.addWidget(self.widget)
        mainframe.setLayout(vbl)
        self.win = QtWidgets.QMainWindow()
        self.rline = False
        #rect = QtCore.QRect()
        #rect.setWidth(640)
        #rect.setHeight(480)
        #win.setGeometry(rect)
        self.win.setCentralWidget(mainframe)
        self.win.show()

    def exec_(self):
        self.a.exec_()

    def set_zversion(self,zver):
        self.zver = zver

    def show_cursor(self):
        self.widget.show_cursor()
    
    def hide_cursor(self):
        self.widget.hide_cursor()

    def read_char(self, callback):
        self.widget.read_char(callback)

    def read_line(self,callback):
        self.rline = True
        self.widget.read_line(callback)

    def set_max_input(self,max_in):
        self.widget.set_max_input(max_in)

    def disconnect_input(self,callback):
        if self.rline:
            self.widget.disconnect_read_line(callback)
            self.rline = False
        else:
            self.widget.disconnect_read_char(callback)

    def select_ostream(self,n):
        self.widget.select_ostream(n)

    def deselect_ostream(self,n):
        self.widget.deselect_ostream(n)

    def prints(self,s):
        self.widget.prints(s)

    def print_status(self,room,status):
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

    def clear_screen(self):
        self.widget.clear()

    def set_font_style(self,s):
        self.widget.set_font_style(s)

    def show_upper_window(self,lines):
        self.widget.split_window(lines, self.zver)

    def set_window(self,w):
        self.widget.set_window(w)

    def set_cursor(self,y,x):
        self.widget.set_cursor(y, x)

    def set_colour(self,fg,bg):
        if fg == 1:
            self.widget.set_text_colour(self.def_fg)
        elif fg > 1 and fg < 13:
            self.widget.set_text_colour(fg)
        if bg == 1:
            self.widget.set_text_background_colour(self.def_bg)
        elif bg > 1 and bg < 13:
            self.widget.set_text_background_colour(bg)

    def selected_ostreams(self):
        return self.widget.selected_ostreams()

    def width(self):
        return self.widget.width

    def height(self):
        return self.widget.height

    def new_line(self):
        self.widget.new_line()

    def set_default_bg(self,bg):
        self.def_bg = bg

    def set_default_fg(self,fg):
        self.def_fg = fg

    def set_font(self,f):
        if f == 1 or f == 3:
            res = self.zfont
            self.zfont = f
            return res
        else:
            return 0

    def split_window(self,lines,version):
        self.widget.split_window(lines,version)

    def erase_window(self,w):
        pass
