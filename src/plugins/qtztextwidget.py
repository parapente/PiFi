# -*- coding: utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QString
from PyQt4.QtCore import pyqtSignal
from lib.stream import ZStream

__author__="Theofilos Intzoglou"
__date__ ="$15 Αυγ 2009 10:46:38 μμ$"

class ZTextWidget(QWidget):
    upper_buf = []
    upper_buf_height = 0
    upper_win_cursor = [] # Upper win cursor x,y
    lower_win_cursor = 1 # Lower win cursor x (y cannot be changed!)
    fixed_font = None
    fixed_font_metrics = None
    fixed_font_width = 0
    fixed_font_height = 0
    buf = []
    width = 80
    height = 26
    cur_win = 0 # Default win is the lower (1 is for upper win)
    cur_fg = 10
    cur_bg = 2
    cur_style = 0
    max_char = 0
    start_pos = 0
    top_pos = 0
    cur_pos = 0
    input_buf = []
    _cursor_visible = False
    _ostream = None
    returnPressed = pyqtSignal(QString)
    keyPressed = pyqtSignal(int)

    def __init__(self,parent = None,flags = Qt.Widget):
        super(ZTextWidget,self).__init__(parent,flags)
        sp = QSizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Fixed)
        sp.setVerticalPolicy(QSizePolicy.Fixed)
        self.set_fixed_font("DeJa Vu Sans Mono", 9)
        self.setSizePolicy(sp)
        self.setFocusPolicy(Qt.StrongFocus)
        self._ostream = [ZStream(), ZStream(), ZStream(), ZStream()]
        self._ostream[0].selected = True
        for i in range(self.width *  self.height * 4):
            self.buf.append(0)

    def paintEvent(self,e):
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width * self.fixed_font_width + 2, self.height * self.fixed_font_height, Qt.black)
        painter.setPen(Qt.gray)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setFont(self.fixed_font)
        painter.setBackgroundMode(Qt.OpaqueMode)
        # Print main window
        l = self.height
        while (l > 0):
            c = 1
            while (c <= self.width):
                y = self.fixed_font_metrics.ascent() + (l - 1) * self.fixed_font_height
                x = 1 + ((c - 1) * self.fixed_font_width)
                #print "**",l,"**",c
                if self.buf[(((self.height - l) * self.width) + c - 1) * 4] == 0:
                    painter.setPen(self.ztoq_color(self.cur_fg))
                else:
                    painter.setPen(self.ztoq_color(self.buf[(((self.height - l) * self.width) + c - 1) * 4]))
                if self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 1] == 0:
                    painter.setBackground(QBrush(self.ztoq_color(self.cur_bg)))
                else:
                    painter.setBackground(QBrush(self.ztoq_color(self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 1])))
                # Set appropriate font style
                if self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 2] == 0:
                    f = painter.font()
                    f.setBold(False)
                    f.setItalic(False)
                    painter.setFont(f)
                if self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 2] & 1: # Reverse video
                    painter.setPen(self.ztoq_color(self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 1]))
                    painter.setBackground(QBrush(self.ztoq_color(self.buf[(((self.height - l) * self.width) + c - 1) * 4])))
                if self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 2] & 2: # Bold
                    f = painter.font()
                    f.setBold(True)
                    painter.setFont(f)
                if self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 2] & 4: # Italic
                    f = painter.font()
                    f.setItalic(True)
                    painter.setFont(f)
                if self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 3] <> 0:
                    painter.drawText(x,y,self.buf[((((self.height - l) * self.width) + c - 1) * 4) + 3])
                c += 1
            l -= 1
            c = 1
        # Print upper window
        if self.upper_buf <> []:
            l = 1
            while (l <= self.upper_buf_height):
                c = 1
                while (c <= self.width):
                    y = self.fixed_font_metrics.ascent() + (l - 1) * self.fixed_font_height
                    x = 1 + ((c - 1) * self.fixed_font_width)
                    #print "**",l,"**",c
                    if self.upper_buf[((((l - 1) * self.width) + c - 1) * 4) + 3] <> 0:
                        painter.setPen(self.ztoq_color(self.upper_buf[(((l - 1) * self.width) + c - 1) * 4]))
                        painter.setBackground(QBrush(self.ztoq_color(self.upper_buf[((((l - 1) * self.width) + c - 1) * 4) + 1])))
                        # Set appropriate font style
                        if self.upper_buf[((((l - 1) * self.width) + c - 1) * 4) + 2] == 0:
                            f = painter.font()
                            f.setBold(False)
                            f.setItalic(False)
                            painter.setFont(f)
                        if self.upper_buf[((((l - 1) * self.width) + c - 1) * 4) + 2] & 1: # Reverse video
                            painter.setPen(self.ztoq_color(self.upper_buf[((((l - 1) * self.width) + c - 1) * 4) + 1]))
                            painter.setBackground(QBrush(self.ztoq_color(self.upper_buf[(((l - 1) * self.width) + c - 1) * 4])))
                        if self.upper_buf[((((l - 1) * self.width) + c - 1) * 4) + 2] & 2: # Bold
                            f = painter.font()
                            f.setBold(True)
                            painter.setFont(f)
                        if self.upper_buf[((((l - 1) * self.width) + c - 1) * 4) + 2] & 4: # Italic
                            f = painter.font()
                            f.setItalic(True)
                            painter.setFont(f)
                        painter.drawText(x,y,self.upper_buf[((((l - 1) * self.width) + c - 1) * 4) + 3])
                    c += 1
                l += 1
        # Print cursor if visible
        if self._cursor_visible:
            self.display_cursor()

    def sizeHint(self):
        size = QSize()
        size.setWidth(self.width * self.fixed_font_width + 2)
        size.setHeight(self.height * self.fixed_font_height)
        return size

    def set_fixed_font(self,name,size):
        self.fixed_font = QFont(name, size)
        self.fixed_font.setFixedPitch(True)
        self.fixed_font.setKerning(False)
        self.fixed_font_metrics = QFontMetrics(self.fixed_font)
        self.fixed_font_width = self.fixed_font_metrics.averageCharWidth()
        self.fixed_font_height = self.fixed_font_metrics.height()
        #print self.fixed_font_width, self.fixed_font_height

    def ztoq_color(self,c):
        if c == 2:
            return Qt.black
        elif c == 3:
            return Qt.red
        elif c == 4:
            return Qt.green
        elif c == 5:
            return Qt.yellow
        elif c == 6:
            return Qt.blue
        elif c == 7:
            return Qt.magenta
        elif c == 8:
            return Qt.cyan
        elif c == 9:
            return Qt.white
        elif c == 10:
            return Qt.lightGray
        elif c == 11:
            return Qt.gray
        elif c == 12:
            return Qt.darkGray

    def set_cursor(self,x,y):
        self.upper_win_cursor = [x,y]

    def set_window(self,w):
        if w < 2:
            self.cur_win = w
        else:
            sys.exit("Unknown window {0}!?!".args(w))

    def prints(self,str):
        if self._ostream[0].selected:
            if self.cur_win == 0: # Lower win
                # TODO: Buffering
                c = self.lower_win_cursor
                i = 0
                total = len(str)
                #print "Total -", total
                while (i < total):
                    s = ""
                    while (i < total) and (str[i] <> '\n') and (c <= self.width):
                        s += str[i]
                        i += 1
                        c += 1
                    self.print_line(s)
                    #print "--> [i, c, total]", i, c, total, " ++ ", s
                    if c > self.width:
                        self.insert_new_line()
                        self.lower_win_cursor = 1
                        c = 1
                    elif (i < total) and (str[i] == '\n'):
                        self.insert_new_line()
                        self.lower_win_cursor = 1
                        c = 1
                        i += 1
                    #elif (i == total) and (str[i-1] <> '\n'):
                    else:
                        self.lower_win_cursor += len(s)
            else:
                i = self.upper_win_cursor[0]
                j = 0
                l = self.upper_win_cursor[1]
                #print "-", i, l, "-", str
                #print "len upperbuf=", len(self.upper_buf)
                while (i <= self.width) and (j < len(str)):
                    if str[j] <> '\n':
                        self.upper_buf[(((l - 1) * self.width) + (i - 1)) * 4] = self.cur_fg
                        self.upper_buf[((((l - 1) * self.width) + (i - 1)) * 4) + 1] = self.cur_bg
                        self.upper_buf[((((l - 1) * self.width) + (i - 1)) * 4) + 2] = self.cur_style
                        self.upper_buf[((((l - 1) * self.width) + (i - 1)) * 4) + 3] = str[j]
                        i += 1
                        j += 1
                    else:
                        self.upper_win_cursor = [1,l + 1]
                        i = 1
                        l += 1
                        j += 1
                self.upper_win_cursor[0] += j
            self.update()

    def print_line(self,str):
        col = self.lower_win_cursor
        #print "Column:", col, str
        if self.cur_win == 0: # Lower win
            for i in range(len(str)):
                self.buf[(col - 1 + i) * 4] = self.cur_fg
                self.buf[((col - 1 + i) * 4) + 1] = self.cur_bg
                self.buf[((col - 1 + i) * 4) + 2] = self.cur_style
                self.buf[((col - 1 + i) * 4) + 3] = str[i]

    def print_char(self,c):
        col = self.lower_win_cursor
        if self.cur_win == 0: # Lower win
            if c <> '\n':
                self.buf[(col - 1) * 4] = self.cur_fg
                self.buf[((col - 1) * 4) + 1] = self.cur_bg
                self.buf[((col - 1) * 4) + 2] = self.cur_style
                self.buf[((col - 1) * 4) + 3] = c
                self.lower_win_cursor += 1
            if self.lower_win_cursor > self.width: # If we exceed screen width
                #print "I insert a newline"
                self.insert_new_line()
                self.lower_win_cursor = 1
            elif c == '\n':
                self.insert_new_line()
                self.lower_win_cursor = 1
        self.update()

    def set_max_input(self,m):
        self.max_char = m

    def show_cursor(self):
        self.cur_pos = self.lower_win_cursor
        self.top_pos = self.cur_pos
        self.start_pos = self.cur_pos
        self.input_buf = []
        self._cursor_visible = True
        self.update()

    def hide_cursor(self):
        self._cursor_visible = False
        self.update()

    def display_cursor(self):
        painter = QPainter(self)
        col = self.cur_pos
        y = self.fixed_font_metrics.ascent() + ((self.height - 1) * self.fixed_font_height)
        x = 1 + ((col - 1) * self.fixed_font_width)
        painter.setPen(self.ztoq_color(self.cur_fg))
        painter.setBackground(QBrush(self.ztoq_color(self.cur_bg)))
        painter.drawText(x,y,unichr(0x2581))

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Left:
            if self.cur_pos > self.start_pos:
                self.cur_pos -= 1
                self.update()
            e.accept()
            self.keyPressed.emit(131)
        elif e.key() == Qt.Key_Right:
            if self.cur_pos < self.top_pos:
                self.cur_pos += 1
                self.update()
            e.accept()
            self.keyPressed.emit(132)
        elif e.key() == Qt.Key_Up:
            # TODO: Up in history
            e.accept()
            self.keyPressed.emit(129)
            pass
        elif e.key() == Qt.Key_Down:
            # TODO: Down in history
            e.accept()
            self.keyPressed.emit(130)
            pass
        elif e.key() == Qt.Key_Backspace:
            if self.cur_pos > self.start_pos:
                self.cur_pos -= 1
                self.top_pos -= 1
                col = self.cur_pos - 1
                for i in range(4):
                    self.buf[col * 4 + i] = 0
                del self.input_buf[self.cur_pos - self.start_pos]
                #print self.input_buf
                self.lower_win_cursor -= 1
                self.update()
            # self.keyPressed.emit() # No keycode available for zscii
            e.accept()
        elif e.key() == Qt.Key_Delete:
            # TODO: Fix it!
            if self.cur_pos < self.top_pos:
                self.top_pos -= 1
                col = self.cur_pos - 1
                for i in range(4):
                    self.buf[col * 4 + i] = 0
                del self.input_buf[self.cur_pos - self.start_pos]
                self.lower_win_cursor -= 1
                self.update()
            e.accept()
            self.keyPressed.emit(8)
        elif (e.key() == Qt.Key_Return) or (e.key() == Qt.Key_Enter):
            # TODO: Learn how to properly convert a list of chars to a string. There MUST be another way! >:-S
            text = ""
            for i in range(len(self.input_buf)):
                text += self.input_buf[i]
            #print text
            self.print_char('\n')
            self.hide_cursor()
            self.keyPressed.emit(13)
            self.returnPressed.emit(text)
            e.accept()
        elif ((e.key() >= Qt.Key_F1) and (e.key() <= Qt.Key_F12)):
            e.accept()
            self.keyPressed.emit(133 + e.key() - Qt.Key_F1)
        elif e.key() == Qt.Key_Escape:
            e.accept()
            self.keyPressed.emit(27)
        elif e.text().isEmpty() == False:
            #print self.cur_pos, self.start_pos, self.max_char
            if (self.cur_pos - self.start_pos) < self.max_char:
                self.cur_pos += 1
                self.top_pos += 1
                if (self.cur_pos - self.start_pos) <= len(self.input_buf):
                    self.input_buf.insert(self.cur_pos - self.start_pos - 1, unicode(e.text()))
                    #print "CurPos:", self.cur_pos
                    col = self.cur_pos - 2
                    self.buf[col * 4 + 3] = unicode(e.text())
                    self.buf[col * 4 + 2] = 0
                    self.buf[col * 4 + 1] = self.cur_bg
                    self.buf[col * 4] = self.cur_fg
                    self.lower_win_cursor += 1
                else:
                    self.input_buf.append(unicode(e.text()))
                    self.print_char(e.text())
                #print self.input_buf
                self.update()
            e.accept()
            t = ord(str(e.text()))
            if ((t > 31) and (t < 127)) or ((t > 154) and (t <252)):
                self.keyPressed.emit(t)
        else:
            e.ignore()

    def set_text_colour(self,fg):
        self.cur_fg = fg

    def set_text_background_colour(self,bg):
        self.cur_bg = bg

    def set_font_style(self,s):
        if s == 0:
            self.cur_style = 0
        else:
            self.cur_style |= s

    def clear(self):
        for i in range(self.width *  self.height * 4):
            self.buf[i] = 0
        self.upper_buf = []
        self.upper_buf_height = 0
        self.upper_win_cursor = [] # Upper win cursor x,y
        self.lower_win_cursor = 1 # Lower win cursor x (y cannot be changed!)
        self.cur_win = 0 # Default win is the lower (1 is for upper win)

    def split_window(self,lines,ver):
        if self.upper_buf_height > lines: # New upper win is smaller. I should copy the rest of the buffer to main buffer
            #print "Copying..."
            l = lines + 1
            while l <= self.upper_buf_height:
                for i in range(self.width * 4):
                    self.buf[(((self.height - l + 1) * self.width) * 4) + i] = self.upper_buf[(((l - 1) * self.width) * 4) + i]
                l += 1
        self.upper_buf_height = lines
        if (self.upper_buf == []) or (ver == 3):
            for i in range(self.upper_buf_height*self.width*4): # It isn't necessary to occupy that much memory but it helps to be prepared! :-P
                self.upper_buf.append(0)
        if (self.upper_win_cursor == []) or (self.upper_win_cursor[1] > lines):
            self.upper_win_cursor = [1,1]

    def select_ostream(self,n):
        if n <> 0:
            self._ostream[n - 1].selected = True

    def deselect_ostream(self,n):
        self._ostream[n - 1].selected = False

    def insert_new_line(self):
        #print "New line"
        # TODO: Not just insert new lines but also remove old unwanted ones
        for i in range(self.width * 4):
            self.buf.insert(0, 0)

    def read_line(self, callback):
        QObject.connect(self, SIGNAL("returnPressed(QString)"), callback)

    def disconnect_read_line(self, callback):
        QObject.disconnect(self, SIGNAL("returnPressed(QString)"), callback)

    def read_char(self, callback):
        QObject.connect(self, SIGNAL("keyPressed(int)"), callback)
        print 'Connect char'

    def disconnect_read_char(self, callback):
        QObject.disconnect(self, SIGNAL("keyPressed(int)"), callback)
        print 'Disconnect char'

    def selected_ostreams(self):
        s = []
        for i in range(4):
            if self._ostream[i].selected == True:
                s.append(i+1)
        return s

    def new_line(self):
        if self._ostream[0].selected:
            if self.cur_win == 0: # Lower win
                self.insert_new_line()
                self.lower_win_cursor = 1
            else: # Upper win
                l = self.upper_win_cursor[1]
                self.upper_win_cursor = [1,l + 1]
