# -*- coding: utf-8

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtGui import QFontInfo
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QString
from PyQt4.QtCore import QChar
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QImage
from lib.window import ZWindow
from lib.stream import ZStream
import traceback
import sys

__author__="Theofilos Intzoglou"
__date__ ="$04 Ιουλ 2011 07:36:38 μμ$"

class ZTextWidget(QWidget):
    width = 80
    height = 24
    cur_fg = 10
    cur_bg = 2
    cur_style = 0
    max_char = 0
    start_pos = 0
    #cursor_char = 0x258f
    #cursor_char = 0x005f
    cursor_char = 0x2017
    #cursor_char = 0x2582
    input_buf = []
    just_scrolled = False
    reading_line = False
    _cursor_visible = False
    _ostream = None
    _input_buffer_printing = False
    returnPressed = pyqtSignal(QString)
    keyPressed = pyqtSignal(int)
    pbuffer = QImage(640,480,QImage.Format_RGB32)

    def __init__(self,parent = None,flags = Qt.Widget):
        super(ZTextWidget,self).__init__(parent,flags)
        sp = QSizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Fixed)
        sp.setVerticalPolicy(QSizePolicy.Fixed)
        self.setSizePolicy(sp)
        self.setFocusPolicy(Qt.StrongFocus)
        self.pbuffer.fill(0)
        font = self.font()
        font.setPointSize(12)
        self.normal_font = font
        self.fixed_font = QFont(font)
        self.fixed_font.setStyleHint(QFont.Monospace)
        self.fixed_font.setFamily(self.fixed_font.defaultFamily())
        self.fixed_font.setPointSize(12)
        print self.fixed_font.family()
        #self.setFont(self.normal_font)
        self.setFont(self.fixed_font)
        self.pbuffer_painter = QPainter(self.pbuffer)
        self.pbuffer_painter.setFont(self.fixed_font)

        self.font_metrics = self.pbuffer_painter.fontMetrics()

        self.linesize = self.font_metrics.height()+1
        self.avgwidth = self.font_metrics.averageCharWidth()
        print self.font_metrics.averageCharWidth(), self.linesize, self.avgwidth
        print self.font_metrics.height()
        self.width = (self.pbuffer.width() - 4) / self.font_metrics.averageCharWidth()
        self.height = self.pbuffer.height() / self.linesize

        self.pbuffer_painter.setFont(self.normal_font)

    def paintEvent(self,e):
        painter = QPainter(self)
        painter.drawImage(0,0,self.pbuffer)

    def scroll(self,painter):
        part = self.pbuffer.copy(0,self.linesize,self.pbuffer.width(),self.pbuffer.height()-self.linesize)
        #print 'Part height:', part.height(), 'width:', part.width()
        self.pbuffer.fill(self.ztoq_color(self.cur_bg))
        #print 'pbuffer height:', self.pbuffer.height(), 'width:', self.pbuffer.width()
        painter.drawImage(0,0,part)
        #print 'pbuffer height:', self.pbuffer.height(), 'width:', self.pbuffer.width()
        self.update()
        if (self.reading_line):
            self.just_scrolled = True

    def sizeHint(self):
        size = QSize()
        size.setWidth(640)
        size.setHeight(480)
        return size

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

    def set_max_input(self,m):
        self.max_char = m

    def show_cursor(self,window):
        self.lastwindow = window
        self._cursor_visible = True
        self._input_cursor_pos = 0
        self.insert_pos = window.cursor
        self.insert_real_pos = window.cursor_real_pos
        self.input_buf = [unichr(self.cursor_char)]
        self.clean_input_buffer_from_screen()
        self.draw_input_buffer()
        #self.draw_cursor(window,True)

    def hide_cursor(self,window):
        self._cursor_visible = False
        del self.input_buf[self._input_cursor_pos]
        #self.draw_cursor(window,False)

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Left:
            if self._input_cursor_pos>0:
                c = self.input_buf.pop(self._input_cursor_pos)
                self._input_cursor_pos -= 1
                self.input_buf.insert(self._input_cursor_pos, c)
                self.clean_input_buffer_from_screen()
                self.draw_input_buffer()
                self.update()
            e.accept()
            self.keyPressed.emit(131)
        elif e.key() == Qt.Key_Right:
            if self._input_cursor_pos<(len(self.input_buf)-1):
                c = self.input_buf.pop(self._input_cursor_pos)
                self._input_cursor_pos += 1
                self.input_buf.insert(self._input_cursor_pos, c)
                self.clean_input_buffer_from_screen()
                self.draw_input_buffer()
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
            if len(self.input_buf)>1: # If there IS something to delete
                self.clean_input_buffer_from_screen()
                del self.input_buf[self._input_cursor_pos-1]
                self._input_cursor_pos -= 1
                self.draw_input_buffer()
            # self.keyPressed.emit() # No keycode available for zscii
            e.accept()
        elif e.key() == Qt.Key_Delete:
            if self._input_cursor_pos < (len(self.input_buf) - 1):
                self.clean_input_buffer_from_screen()
                del self.input_buf[self._input_cursor_pos+1]
                self.draw_input_buffer()
            e.accept()
            self.keyPressed.emit(8)
        elif (e.key() == Qt.Key_Return) or (e.key() == Qt.Key_Enter):
            self.clean_input_buffer_from_screen()
            self.hide_cursor(self.lastwindow)
            self.draw_input_buffer()
            text = ''
            for i in self.input_buf:
                text += i
            print text
            self.draw_text('\n', self.lastwindow)
            self.keyPressed.emit(13)
            self.returnPressed.emit(text)
            self._input_cursor_pos = 0
            self.input_buf = [unichr(self.cursor_char)]
            e.accept()
        elif ((e.key() >= Qt.Key_F1) and (e.key() <= Qt.Key_F12)):
            e.accept()
            self.keyPressed.emit(133 + e.key() - Qt.Key_F1)
        elif e.key() == Qt.Key_Escape:
            e.accept()
            self.keyPressed.emit(27)
        elif e.text().isEmpty() == False:
            if (self.reading_line) and (len(self.input_buf) < self.max_char+1):
                self.clean_input_buffer_from_screen()
                self.input_buf.insert(self._input_cursor_pos, unicode(e.text()))
                self._input_cursor_pos += 1
                self.draw_input_buffer()
            e.accept()
            t = ord(str(e.text()))
            if ((t > 31) and (t < 127)) or ((t > 154) and (t <252)):
                self.keyPressed.emit(t)
        else:
            e.ignore()

    def draw_input_buffer(self):
        # Prepare for redraw by setting appropriate cursor position
        tmp_pos = self.lastwindow.cursor
        tmp_real_pos = self.lastwindow.cursor_real_pos
        self.lastwindow.set_cursor_position(self.insert_pos[0], self.insert_pos[1])
        self.lastwindow.set_cursor_real_position(self.insert_real_pos[0], self.insert_real_pos[1])
        self._input_buffer_printing = True
        self.prints(self.input_buf, self.lastwindow)
        self._input_buffer_printing = False
        if (self.just_scrolled): # A new line scroll // Is it really necessary?
            self.just_scrolled = False
            self.lastwindow.set_cursor_position(tmp_pos[0], tmp_pos[1])
            self.lastwindow.set_cursor_real_position(tmp_real_pos[0], tmp_real_pos[1])
        else:
            self.lastwindow.set_cursor_position(tmp_pos[0], tmp_pos[1])
            self.lastwindow.set_cursor_real_position(tmp_real_pos[0], tmp_real_pos[1])
        #self.draw_cursor(self.lastwindow, self._cursor_visible)
        #print self.input_buf, len(self.input_buf), self.max_char
        self.update()

    def set_text_colour(self,fg):
        self.cur_fg = fg

    def set_text_background_colour(self,bg):
        self.cur_bg = bg

    def set_font_style(self,s):
        if s == 0:
            self.cur_style = 0
        else:
            self.cur_style |= s
        # Now set the font accordingly
        newfont = self.font()
        # First reset the font
        newfont.setItalic(False)
        newfont.setFixedPitch(False)
        newfont.setBold(False)
        # And now check for extra style
        if ((self.cur_style & 2) == 2): # Bold
            newfont.setBold(True)
        if ((self.cur_style & 4) == 4): # Italic
            newfont.setItalic(True)
        if ((self.cur_style & 8) == 8): # Fixed Pitch
            newfont.setFixedPitch(True)
        self.setFont(newfont)

    def read_line(self, window, callback):
        self.lastwindow = window
        self.cur_pos = 0
        self.reading_line = True
        self.update()
        QObject.connect(self, SIGNAL("returnPressed(QString)"), callback)

    def disconnect_read_line(self, callback):
        self.reading_line = False
        QObject.disconnect(self, SIGNAL("returnPressed(QString)"), callback)

    def read_char(self, window, callback):
        self.update()
        self.lastwindow = window
        QObject.connect(self, SIGNAL("keyPressed(int)"), callback)
        print 'Connect char'

    def disconnect_read_char(self, callback):
        QObject.disconnect(self, SIGNAL("keyPressed(int)"), callback)
        print 'Disconnect char'

    def prints(self, txt, window):
        lastspace = 0
        i = 0
        textbuffer = ''
        for w in txt:
            if (w == '\n' or w == unichr(self.cursor_char)):
                if (len(textbuffer)>0): # If there is something to print
                    self.draw_text(textbuffer, window)
                    textbuffer = ''
                self.draw_text(w, window)
                if (w == '\n'): # \n is whitespace :-)
                    lastspace = i
            elif (w == ' '): # Space was found
                if (lastspace == i-1): # Continuous spaces
                    textbuffer += w
                else:
                    self.draw_text(textbuffer, window)
                    self.draw_text(' ', window)
                    textbuffer = ''
                lastspace = i
            else:
                textbuffer += w
            i += 1
        if (len(textbuffer)>0): # Buffer not empty
            self.draw_text(textbuffer, window)

    def draw_text(self, txt, window):
        if ((len(txt)>0) and not ((txt == unichr(self.cursor_char)) and (self._cursor_visible == False))): # If there IS something to print
            painter = self.pbuffer_painter

            # @type window ZWindow
            if (window.cursor == None):
                if (window.id == 0): # Main window
                    window.set_cursor_position(1, self.height)
                    window.set_cursor_real_position(2, self.height*(self.linesize-1))
                else:
                    window.set_cursor_position(1, 1)
                    window.set_cursor_real_position(2, self.linesize-1)

            if (txt=='\n'):
                if (window.cursor[1]==self.height):
                    if (window.scrolling):
                        self.scroll(painter)
                    window.set_cursor_position(1, window.cursor[1])
                    window.set_cursor_real_position(2, window.cursor_real_pos[1])
                else:
                    window.set_cursor_position(1, window.cursor[1]+1)
                    window.set_cursor_real_position(2, window.cursor_real_pos[1]+self.linesize)
            else:
                rect = QRectF()
                rect.setX(window.cursor_real_pos[0])
                rect.setY(window.cursor_real_pos[1])
                rect.setWidth(self.pbuffer.width()-window.cursor_real_pos[0])
                rect.setHeight(self.linesize)

                painter.setPen(self.ztoq_color(self.cur_fg))
                painter.setFont(self.font())
                painter.setRenderHint(QPainter.TextAntialiasing)
                painter.setBackground(QBrush(self.ztoq_color(self.cur_bg)))
                if (self._input_buffer_printing == False):
                    painter.setBackgroundMode(Qt.OpaqueMode)
                else:
                    painter.setBackgroundMode(Qt.TransparentMode)
                bounding_rect = painter.boundingRect(rect,txt)
                if (rect.contains(bounding_rect)):
                    #print rect.x(), rect.y(), rect.width(),rect.height(), txt, bounding_rect
                    painter.drawText(bounding_rect, txt)
                    if txt != unichr(self.cursor_char):
                        window.set_cursor_position(window.cursor[0]+len(txt), window.cursor[1])
                        window.set_cursor_real_position(rect.x()+bounding_rect.width(), rect.y())
                else: # There is not enough space
                    #print "Not enough space to print:", txt
                    self.scroll(painter)
                    window.set_cursor_position(1, self.height)
                    window.set_cursor_real_position(2, self.height*(self.linesize-1))
                    rect.setX(2)
                    rect.setY(window.cursor_real_pos[1])
                    rect.setWidth(self.pbuffer.width()-window.cursor_real_pos[0])
                    rect.setHeight(self.linesize)
                    bounding_rect = painter.boundingRect(rect,txt)
                    painter.drawText(bounding_rect, txt)
                    if txt != unichr(self.cursor_char):
                        window.set_cursor_position(window.cursor[0]+len(txt), window.cursor[1])
                        window.set_cursor_real_position(rect.x()+bounding_rect.width(), rect.y())

    def buffered_string(self, txt, window):
        # @type window ZWindow
        if (window.buffering):
            rect = QRect()
            rect.setX(window.cursor_real_pos[0])
            rect.setY(window.cursor_real_pos[1])
            rect.setWidth(window.width-window.cursor_real_pos[0])
            rect.setHeight(self.linesize)
            bounding_rect = painter.boundingRect(rect,txt)
            if (rect.contains(bounding_rect)): # string fits in this line
                return txt
        else:
            return txt

    def clean_input_buffer_from_screen(self):
        rect = QRectF()
        rect.setX(self.lastwindow.cursor_real_pos[0])
        rect.setY(self.lastwindow.cursor_real_pos[1])
        rect.setWidth(self.pbuffer.width()-self.lastwindow.cursor_real_pos[0])
        rect.setHeight(self.linesize)
        txtbuffer = ''
        for w in self.input_buf:
            txtbuffer += w
        bounding_rect = self.pbuffer_painter.boundingRect(rect, txtbuffer)
        if (rect.contains(bounding_rect)): # string fits in this line
            self.pbuffer_painter.eraseRect(bounding_rect)
            #self.pbuffer_painter.drawRect(bounding_rect)
            #print 'Erasing rect', bounding_rect
        else:
            self.pbuffer_painter.eraseRect(rect)
            #print 'Erasing rect', rect
            # FIXME: clear next lines

    def clear(self):
        self.pbuffer.fill(self.ztoq_color(self.cur_bg))

    def update_real_cursor_position(self, w):
        w.set_cursor_real_position(2+(w.cursor[0]-1)*self.avgwidth, w.cursor[1]*self.linesize)
        #print w.cursor, '->', w.cursor_real_pos

    def erase_window(self, w):
        if (w.id == 1):
            self.pbuffer_painter.eraseRect(QRectF(2, 0, self.pbuffer.width()-2, w.line_count*self.linesize))
            print 2, 0, self.pbuffer.width()-2, w.line_count*self.linesize
        else:
            traceback.print_stack()
            sys.exit()