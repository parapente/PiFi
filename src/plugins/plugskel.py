# -*- coding: utf-8

from lib.window import ZWindow
from lib.stream import ZStream

__author__="Theofilos Intzoglou"
__date__ ="$9 Ιαν 2011 1:56:17 πμ$"

class PlugSkel(object):

    def __init__(self):
        self._ostream = [ZStream(), ZStream(), ZStream(), ZStream()]
        self._ostream[0].selected = True

    def prepare_gui(self):
        pass

    def set_debug_level(self,lvl):
        self.level = lvl

    def debugprint(self,msg,lvl):
        if (lvl <= self.level):
            print msg

    def set_zversion(self,zver):
        self.zver = zver
        if (zver<3):
            self.window = [ZWindow(0)]
        elif (zver==6):
            self.window = [ZWindow(0),ZWindow(1),ZWindow(2),ZWindow(3),
                           ZWindow(4),ZWindow(5),ZWindow(6),ZWindow(7)]
        else:
            self.window = [ZWindow(0),ZWindow(1)]
            # The upper window is a special type of window
            self.window[1].set_buffering(False)
            self.window[1].set_wrapping(False)
            self.window[1].set_scrolling(False)
        self.current_window = 0

    def exec_(self):
        pass

    def show_cursor(self):
        self.widget.show_cursor()

    def hide_cursor(self):
        self.widget.hide_cursor()

    def read_char(self, callback, time, timeout_callback):
        self.widget.read_char(self.window[self.current_window], callback, time, timeout_callback)

    def read_line(self, callback, time, timeout_callback, reset):
        self.rline = True
        self.widget.read_line(self.window[self.current_window], callback, time, timeout_callback, reset)

    def set_max_input(self,max_in):
        self.widget.set_max_input(max_in)

    def disconnect_input(self,callback):
        if self.rline:
            self.widget.disconnect_read_line(callback)
            self.rline = False
        else:
            self.widget.disconnect_read_char(callback)

    def prints(self,s):
        self.widget.prints(s)

    def print_status(self,room,status):
        self.widget.print_status(room,status)

    def clear_screen(self):
        self.widget.clear()

    def set_font_style(self,s):
        win = self.current_window
        self.widget.set_font_style(s,win)

    def show_upper_window(self,lines):
        self.split_window(lines, self.zver)

    def set_window(self,w):
        self.current_window = w
        if (self.zver != 6 and w == 1):
            self.window[1].set_cursor_position(1, 1)

    def set_cursor(self,x,y):
        if (self.current_window==1):
            self.window[1].set_cursor_position(x,y)

    def set_colour(self,fg,bg):
        win = self.current_window
        if fg == 1:
            self.widget.set_text_colour(self.def_fg, win)
        elif fg > 1 and fg < 13:
            self.widget.set_text_colour(fg, win)
        if bg == 1:
            self.widget.set_text_background_colour(self.def_bg, win)
        elif bg > 1 and bg < 13:
            self.widget.set_text_background_colour(bg, win)

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

    def selected_ostreams(self):
        s = []
        for i in xrange(4):
            if self._ostream[i].selected == True:
                s.append(i+1)
        return s

    def select_ostream(self,n):
        if n <> 0:
            self._ostream[n - 1].selected = True

    def deselect_ostream(self,n):
        self._ostream[n - 1].selected = False

    def update_screen_size(self):
        self.screen_size_callback(self.width(),self.height())
        print self.width(), self.height()

    def erase_window(self,w):
        self.widget.erase_window(self.window[w])

    def stop_line_timer(self):
        self.widget.stop_line_timer()

    def stop_char_timer(self):
        self.widget.stop_char_timer()

    def quit(self):
        pass