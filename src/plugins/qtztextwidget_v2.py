# -*- coding: utf-8

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QFontInfo
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage
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
    cursor_char = chr(0x2017)
    #cursor_char = 0x2582
    input_buf = []
    just_scrolled = False
    reading_line = False
    reverse_video = False
    _cursor_visible = False
    _ostream = None
    _input_buffer_printing = False
    _input_cursor_pos = 0
    returnPressed = pyqtSignal(['QString'])
    keyPressed = pyqtSignal(int)
    pbuffer = [None]*8
    pbuffer_painter = [None]*8
    game_area = QImage(640, 480, QImage.Format_RGB32)
    game_area_painter = QPainter(game_area)
    chartimer = None
    linetimer = None
    brush = QBrush(Qt.SolidPattern)
    ztoq_color = dict({2:Qt.black,
                       3:Qt.red,
                       4:Qt.green,
                       5:Qt.yellow,
                       6:Qt.blue,
                       7:Qt.magenta,
                       8:Qt.cyan,
                       9:Qt.white,
                       10:Qt.lightGray,
                       11:Qt.gray,
                       12:Qt.darkGray})

    def __init__(self,parent = None,flags = Qt.Widget):
        super(ZTextWidget,self).__init__(parent,flags)
        sp = QSizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Fixed)
        sp.setVerticalPolicy(QSizePolicy.Fixed)
        self.setSizePolicy(sp)
        self.setFocusPolicy(Qt.StrongFocus)
        self.pbuffer[0] = QImage(640,480,QImage.Format_RGB32)
        self.pbuffer[0].fill(0)
        font = self.font()
        self.normal_font = font
        self.fixed_font = QFont(font)
        self.fixed_font.setStyleHint(QFont.Monospace)
        self.fixed_font.setFamily(self.fixed_font.defaultFamily())
        self.fixed_font.setPointSize(9)
        print(self.fixed_font.family())
        #self.setFont(self.normal_font)
        self.setFont(self.fixed_font)
        self.pbuffer_painter[0] = QPainter(self.pbuffer[0])
        self.pbuffer_painter[0].setFont(self.fixed_font)

        self.font_metrics = self.pbuffer_painter[0].fontMetrics()

        self.linesize = self.font_metrics.height()
        self.avgwidth = self.font_metrics.averageCharWidth()
        print(self.font_metrics.averageCharWidth(), self.linesize, self.avgwidth)
        print(self.font_metrics.height())
        self.width = (self.pbuffer[0].width() - 4) // self.font_metrics.averageCharWidth()
        self.height = self.pbuffer[0].height() // self.linesize

        self.pbuffer_painter[0].setFont(self.normal_font)
        self.set_text_colour(self.cur_fg, 0)
        self.set_text_background_colour(self.cur_bg, 0)

    def paintEvent(self,e):
        painter = QPainter(self)
        painter.drawImage(0,0,self.game_area)

    def update_game_area(self):
        for i in range(8):
            if (self.pbuffer[i] != None):
                self.game_area_painter.drawImage(0,0,self.pbuffer[i])
        self.update()

    def scroll(self,painter):
        part = self.pbuffer[0].copy(0,self.linesize,self.pbuffer[0].width(),self.pbuffer[0].height()-self.linesize)
        #print 'Part height:', part.height(), 'width:', part.width()
        self.pbuffer[0].fill(self.ztoq_color[self.cur_bg])
        #print 'pbuffer[0] height:', self.pbuffer[0].height(), 'width:', self.pbuffer[0].width()
        painter.drawImage(0,0,part)
        #print 'pbuffer[0] height:', self.pbuffer[0].height(), 'width:', self.pbuffer[0].width()
        if (self.reading_line):
            self.just_scrolled = True

    def sizeHint(self):
        size = QSize()
        size.setWidth(640)
        size.setHeight(480)
        return size

    def set_max_input(self,m):
        self.max_char = m

    def show_cursor(self,window):
        self.lastwindow = window
        #self._input_cursor_pos = 0
        #print self._input_cursor_pos
        self.insert_pos = window.cursor
        self.insert_real_pos = window.cursor_real_pos
        if (self._cursor_visible != True): # If the cursor is already visible avoid multiplying it...
            self.input_buf.insert(self._input_cursor_pos, self.cursor_char)
        self._cursor_visible = True
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
            e.accept()
            self.keyPressed.emit(131)
        elif e.key() == Qt.Key_Right:
            if self._input_cursor_pos<(len(self.input_buf)-1):
                c = self.input_buf.pop(self._input_cursor_pos)
                self._input_cursor_pos += 1
                self.input_buf.insert(self._input_cursor_pos, c)
                self.clean_input_buffer_from_screen()
                self.draw_input_buffer()
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
            if (self._cursor_visible == True):
                self.hide_cursor(self.lastwindow)
            if (self.reading_line == True):
                self.draw_input_buffer()
            text = ''
            for i in self.input_buf:
                text += i
            #print text
            self.draw_text('\n', 1, self.lastwindow)
            self.keyPressed.emit(13)
            self._input_cursor_pos = 0
            self.input_buf = []
            self.returnPressed.emit(text)
            e.accept()
        elif ((e.key() >= Qt.Key_F1) and (e.key() <= Qt.Key_F12)):
            e.accept()
            self.keyPressed.emit(133 + e.key() - Qt.Key_F1)
        elif e.key() == Qt.Key_Escape:
            e.accept()
            self.keyPressed.emit(27)
        elif (e.text()):
            if (self.reading_line) and (len(self.input_buf) < self.max_char+1):
                self.clean_input_buffer_from_screen()
                self.input_buf.insert(self._input_cursor_pos, str(e.text()))
                self._input_cursor_pos += 1
                self.draw_input_buffer()
            e.accept()
            t = ord(str(e.text()[0])) # TODO: Check if we can handle multiple events at once
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
        self.update_game_area()

    def set_text_colour(self,fg, win):
        self.cur_fg = fg
        if (self.pbuffer[win]):
            if (self.pbuffer_painter[win] == None):
                self.pbuffer_painter[win] = QPainter(self.pbuffer[win])
            painter = self.pbuffer_painter[win]
            painter.setPen(self.ztoq_color[self.cur_fg])

    def set_text_background_colour(self,bg, win):
        self.cur_bg = bg
        if (self.pbuffer[win]):
            if (self.pbuffer_painter[win] == None):
                self.pbuffer_painter[win] = QPainter(self.pbuffer[win])
            painter = self.pbuffer_painter[win]
            self.brush.setColor(self.ztoq_color[self.cur_bg])
            painter.setBackground(self.brush)

    def set_font_style(self,s,win):
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
        if (self.reverse_video == True):
            tmpbg = self.cur_bg
            self.set_text_background_colour(self.cur_fg,win)
            self.set_text_colour(tmpbg,win)
        self.reverse_video = False
        # And now check for extra style
        if ((self.cur_style & 1) == 1): # Reverse video
            self.reverse_video = True
            tmpbg = self.cur_bg
            self.set_text_background_colour(self.cur_fg,win)
            self.set_text_colour(tmpbg,win)
        if ((self.cur_style & 2) == 2): # Bold
            newfont.setBold(True)
        if ((self.cur_style & 4) == 4): # Italic
            newfont.setItalic(True)
        if ((self.cur_style & 8) == 8): # Fixed Pitch
            newfont.setFixedPitch(True)
        self.setFont(newfont)

    def read_line(self, window, callback, time, timeout_callback, reset):
        self.lastwindow = window
        #print reset
        if (reset == True):
            self.cur_pos = 0
        self.reading_line = True
        self.update_game_area()
        self.callback_object = callback
        self.returnPressed.connect(self.read_line_callback)
        if (self.linetimer == None):
            self.linetimer = QTimer()
            self.linetimer.setSingleShot(True)
        if (time != 0):
            self.timeout_callback_object = timeout_callback
            self.linetimer.timeout.connect(self.read_line_timeout_callback)
            self.linetimer.start(time * 100)

    def read_line_callback(self, string):
        if (self.linetimer != None):
            self.linetimer.stop()
        self.returnPressed.disconnect()
        self.callback_object(string)

    def read_line_timeout_callback(self):
        self.linetimer.timeout.disconnect()
        self.timeout_callback_object()

    def disconnect_read_line(self, callback):
        self.reading_line = False
        try:
            self.returnPressed.disconnect(callback)
        except:
            pass

    def read_char(self, window, callback, time, timeout_callback):
        self.update_game_area()
        self.lastwindow = window
        self.callback_object = callback
        self.keyPressed.connect(self.read_char_callback)
        #print 'Connect char'
        if (self.chartimer == None):
            self.chartimer = QTimer()
            self.chartimer.setSingleShot(True)
        if (time != 0):
            self.timeout_callback_object = timeout_callback
            self.chartimer.timeout.connect(self.read_char_timeout_callback)
            self.chartimer.start(time * 100)

    def read_char_callback(self, key):
        if (self.chartimer != None):
            self.chartimer.stop()
        self.keyPressed.disconnect()
        self.callback_object(key)

    def read_char_timeout_callback(self):
        self.chartimer.timeout.disconnect()
        self.timeout_callback_object()

    def disconnect_read_char(self, callback):
        try:
            self.keyPressed.disconnect(callback)
        except:
            pass
        #print 'Disconnect char'

    def prints(self, txt, window):
        txtlen = len(txt)
        if (txtlen == 1): # print_char got us here...
            self.draw_text(txt[0],1,window)
        else:
            lastspace = 0
            i = 0
            textbuffer = ''
            tblen = 0
            for w in txt:
                if (w == '\n' or w == self.cursor_char):
                    if (tblen>0): # If there is something to print
                        self.draw_text(textbuffer, tblen, window)
                        textbuffer = ''
                        tblen = 0
                    self.draw_text(w, 1, window)
                    if (w == '\n'): # \n is whitespace :-)
                        lastspace = i
                elif (w == ' '): # Space was found
                    if (lastspace == i-1): # Continuous spaces
                        textbuffer += w
                        tblen += 1
                    else:
                        self.draw_text(textbuffer, tblen, window)
                        self.draw_text(' ', 1, window)
                        textbuffer = ''
                        tblen = 0
                    lastspace = i
                else:
                    textbuffer += w
                    tblen += 1
                i += 1
            if (textbuffer != ''): # Buffer not empty
                self.draw_text(textbuffer, tblen, window)

    def draw_text(self, txt, txtlen, window):
        if self.pbuffer[window.id] is None:
            self.pbuffer[window.id] = QImage(640,480,QImage.Format_RGB32)
            self.pbuffer[window.id].fill(0)
        if ((txtlen>0) and not ((txt == self.cursor_char) and (self._cursor_visible == False))): # If there IS something to print
            if (self.pbuffer_painter[window.id] == None):
                self.brush.setColor(self.ztoq_color[self.cur_bg])
                self.pbuffer_painter[window.id] = QPainter(self.pbuffer[window.id])
                self.pbuffer_painter[window.id].setPen(self.ztoq_color[self.cur_fg])
                self.pbuffer_painter[window.id].setBackground(self.brush)

            painter = self.pbuffer_painter[window.id]

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
                rect = QRectF(window.cursor_real_pos[0], window.cursor_real_pos[1], self.pbuffer[window.id].width()-window.cursor_real_pos[0], self.linesize)

                painter.setFont(self.font())
                #painter.setRenderHint(QPainter.TextAntialiasing)
                if (self._input_buffer_printing == False):
                    painter.setBackgroundMode(Qt.OpaqueMode)
                else:
                    painter.setBackgroundMode(Qt.TransparentMode)
                bounding_rect = painter.boundingRect(rect,txt)
                if (rect.contains(bounding_rect)):
                    #print rect.x(), rect.y(), rect.width(),rect.height(), txt, bounding_rect
                    painter.drawText(bounding_rect, txt)
                    if txt != self.cursor_char:
                        window.set_cursor_position(window.cursor[0]+txtlen, window.cursor[1])
                        window.set_cursor_real_position(rect.x()+bounding_rect.width(), rect.y())
                else: # There is not enough space
                    print("Not enough space to print:", txt)
                    if window.id == 1 and (window.cursor[1] < window.line_count):
                        window.set_cursor_position(1, window.cursor[1]+1)
                        window.set_cursor_real_position(2, (window.cursor[1]+1)*(self.linesize))
                        self.draw_text(txt, txtlen, window)
                    if window.id == 0:
                        self.scroll(painter)
                        window.set_cursor_position(1, self.height)
                        window.set_cursor_real_position(2, self.height*(self.linesize-1))
                        rect.setX(2)
                        rect.setY(window.cursor_real_pos[1])
                        rect.setWidth(self.pbuffer[window.id].width()-window.cursor_real_pos[0])
                        rect.setHeight(self.linesize)
                        bounding_rect = painter.boundingRect(rect,txt)
                        painter.drawText(bounding_rect, txt)
                        if txt != self.cursor_char:
                            window.set_cursor_position(window.cursor[0]+txtlen, window.cursor[1])
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
        rect.setWidth(self.pbuffer[0].width()-self.lastwindow.cursor_real_pos[0])
        rect.setHeight(self.linesize)
        txtbuffer = ''
        for w in self.input_buf:
            txtbuffer += w
        if (self.pbuffer_painter[0] == None):
            self.pbuffer_painter[0] = QPainter(self.pbuffer[0])
        bounding_rect = self.pbuffer_painter[0].boundingRect(rect, txtbuffer)
        if (rect.contains(bounding_rect)): # string fits in this line
            self.pbuffer_painter[0].eraseRect(bounding_rect)
            #self.pbuffer_painter.drawRect(bounding_rect)
            #print 'Erasing rect', bounding_rect
        else:
            self.pbuffer_painter[0].eraseRect(rect)
            #print 'Erasing rect', rect
            # FIXME: clear next lines

    def clear(self):
        #print 'clearing...'
        self.game_area.fill(self.ztoq_color[self.cur_bg])
        for i in range(8):
            if (self.pbuffer[i] != None):
                self.pbuffer[i].fill(self.ztoq_color[self.cur_bg])

    def update_real_cursor_position(self, w):
        w.set_cursor_real_position(2+(w.cursor[0]-1)*self.avgwidth, (w.cursor[1]-1)*self.linesize)
        #print w.cursor, '->', w.cursor_real_pos

    def erase_window(self, w):
        if ((w.id >= 0) and (w.id < 8)):
            if (self.pbuffer_painter[w.id] == None):
                self.pbuffer_painter[w.id] = QPainter(self.pbuffer[w.id])
            if  not self.reverse_video:
                self.pbuffer_painter[w.id].setPen(self.ztoq_color[self.cur_fg])
                self.brush.setColor(self.ztoq_color[self.cur_bg])
            else:
                self.pbuffer_painter[w.id].setPen(self.ztoq_color[self.cur_bg])
                self.brush.setColor(self.ztoq_color[self.cur_fg])
            self.pbuffer_painter[w.id].setBackground(self.brush)
            self.pbuffer_painter[w.id].setBackgroundMode(Qt.OpaqueMode)
            if w.line_count > 0:
                self.pbuffer_painter[w.id].eraseRect(QRectF(0, 0, self.pbuffer[w.id].width(), w.line_count*self.linesize))
            else:
                self.pbuffer_painter[w.id].eraseRect(QRectF(0, 0, self.pbuffer[w.id].width(), 24*self.linesize)) # TODO: Fix hardcoded linecount
            #print 2, 0, self.pbuffer[w.id].width()-2, w.line_count*self.linesize
        else:
            traceback.print_stack()
            print('erase_window for window',w.id)
            sys.exit()

    def split_window(self, lines, ver):
        #print 'Lines:', lines
        # Copy window 1 to window 0 if it already exists
        if (self.pbuffer[1] != None):
            self.pbuffer_painter[0].drawImage(0,0,self.pbuffer[1])

        if (lines == 0): # Unsplit
            #self.pbuffer[1].fill(self.ztoq_color(self.cur_bg))
            #del self.pbuffer_painter[1]
            #del self.pbuffer[1]
            self.pbuffer_painter[1] = None
            self.pbuffer[1] = None
        else:
            if (self.pbuffer[1] != None): # Window needs resizing
                tmp = self.pbuffer[1]
                #del self.pbuffer_painter[1]
                self.pbuffer_painter[1] = None
                self.pbuffer[1] = self.pbuffer[1].copy(0,0,self.pbuffer[1].width(),lines*self.linesize)
                #del tmp
            else: # New window
                self.pbuffer[1] = QImage(self.pbuffer[0].width(),lines*self.linesize,QImage.Format_RGB32)
                self.pbuffer[1].fill(0)
            if ver == 3:
                self.pbuffer[1].fill(self.ztoq_color[self.cur_bg])

    def stop_line_timer(self):
        if (self.linetimer != None):
            self.linetimer.stop()

    def stop_char_timer(self):
        if (self.chartimer != None):
            self.chartimer.stop()

    def init0(self):
        self.pbuffer[0] = QImage(640,480,QImage.Format_RGB32)
        self.pbuffer[0].fill(0)

