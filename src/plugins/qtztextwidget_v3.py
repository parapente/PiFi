# -*- coding: utf-8

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtGui import QFontInfo
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import QObject
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QTextCursor
from PyQt6.QtGui import QMouseEvent
from lib.window import ZWindow
from lib.stream import ZStream
import traceback
import sys

__author__ = "Theofilos Intzoglou"
__date__ = "$04 Ιουλ 2011 07:36:38 μμ$"


class ZTextWidget(QTextEdit):
    width = 80
    height = 24
    cur_fg = 10
    cur_bg = 2
    cur_style = 0
    max_char = 0
    start_pos = 0
    # cursor_char = 0x258f
    # cursor_char = 0x005f
    # cursor_char = unichr(0x2017)
    # cursor_char = 0x2582
    input_buf = []
    just_scrolled = False
    reading_line = False
    reverse_video = False
    _cursor_visible = False
    _output_stream = None
    _input_buffer_printing = False
    _input_cursor_pos = 0
    returnPressed = pyqtSignal(str)
    keyPressed = pyqtSignal(int)
    print_buffer = [None] * 8
    print_buffer_painter = [None] * 8
    char_timer = None
    line_timer = None
    brush = QBrush(Qt.BrushStyle.SolidPattern)
    ztoq_color = dict(
        {
            2: Qt.GlobalColor.black,
            3: Qt.GlobalColor.red,
            4: Qt.GlobalColor.green,
            5: Qt.GlobalColor.yellow,
            6: Qt.GlobalColor.blue,
            7: Qt.GlobalColor.magenta,
            8: Qt.GlobalColor.cyan,
            9: Qt.GlobalColor.white,
            10: Qt.GlobalColor.lightGray,
            11: Qt.GlobalColor.gray,
            12: Qt.GlobalColor.darkGray,
        }
    )

    def __init__(self, parent=None):
        super(ZTextWidget, self).__init__(parent)

        self.setMinimumWidth(640)
        self.setMinimumHeight(480)
        self.setAcceptRichText(False)

        # self.setFocusPolicy(Qt.StrongFocus)
        # self.pbuffer[0] = QImage(640,480,QImage.Format_RGB32)
        # self.print_buffer[0].fill(0)
        # self.setTextBackgroundColor(Qt.black)
        font = self.font()
        self.normal_font = font
        self.fixed_font = QFont(font)
        self.fixed_font.setStyleHint(QFont.StyleHint.Monospace)
        self.fixed_font.setFamily(self.fixed_font.defaultFamily())
        self.normal_font.setPointSize(14)
        self.fixed_font.setPointSize(14)
        print(self.fixed_font.family())
        self.setFont(self.normal_font)
        # self.setFont(self.fixed_font)

        self.font_metrics = self.fontMetrics()

        self.line_size = self.font_metrics.height()
        self.avg_width = self.font_metrics.averageCharWidth()
        print(self.line_size, self.avg_width)
        print(self.font_metrics.height())
        self.width = super(ZTextWidget, self).width() // self.avg_width
        self.height = super(ZTextWidget, self).height() // self.line_size
        print(self.width, self.height)

        # self.print_buffer_painter[0].setFont(self.normal_font)
        self.set_text_colour(self.cur_fg, 0)
        self.set_text_background_colour(self.cur_bg, 0)
        self.setStyleSheet("QTextEdit {background-color:black;color:grey}")

    def set_max_input(self, m):
        self.max_char = m

    def show_cursor(self, window: ZWindow):
        self.last_window = window
        # self._input_cursor_pos = 0
        # print self._input_cursor_pos
        # self.insert_pos = window.cursor
        # self.insert_real_pos = window.cursor_real_pos
        # if (self._cursor_visible != True): # If the cursor is already visible avoid multiplying it...
        #    self.input_buf.insert(self._input_cursor_pos, self.cursor_char)
        self.setCursorWidth(1)
        self._cursor_visible = True
        # self.clean_input_buffer_from_screen()
        # self.draw_input_buffer()
        # self.draw_cursor(window,True)

    def hide_cursor(self, window: ZWindow):
        self.setCursorWidth(0)
        self._cursor_visible = False
        # del self.input_buf[self._input_cursor_pos]
        # self.draw_cursor(window,False)

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Left:
            if self._input_cursor_pos > 0:
                # c = self.input_buf.pop(self._input_cursor_pos)
                self._input_cursor_pos -= 1
                self.moveCursor(QTextCursor.PreviousCharacter)
                # self.input_buf.insert(self._input_cursor_pos, c)
                # self.clean_input_buffer_from_screen()
                # self.draw_input_buffer()
            e.accept()
            self.keyPressed.emit(131)
        elif e.key() == Qt.Key.Key_Right:
            if self._input_cursor_pos < (len(self.input_buf)):
                # c = self.input_buf.pop(self._input_cursor_pos)
                self._input_cursor_pos += 1
                self.moveCursor(QTextCursor.MoveOperation.NextCharacter)
                # self.input_buf.insert(self._input_cursor_pos, c)
                # self.clean_input_buffer_from_screen()
                # self.draw_input_buffer()
            e.accept()
            self.keyPressed.emit(132)
        elif e.key() == Qt.Key.Key_Home:
            tc = self.textCursor()
            tc.movePosition(
                QTextCursor.MoveOperation.Left,
                QTextCursor.MoveMode.MoveAnchor,
                self._input_cursor_pos,
            )
            self.setTextCursor(tc)
            self._input_cursor_pos = 0
            e.accept()
            # self.keyPressed.emit() # No keycode available for zscii
        elif e.key() == Qt.Key.Key_End:
            tc = self.textCursor()
            tc.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.MoveAnchor,
                len(self.input_buf) - self._input_cursor_pos,
            )
            self.setTextCursor(tc)
            self._input_cursor_pos = len(self.input_buf)
            e.accept()
            # self.keyPressed.emit() # No keycode available for zscii
        # elif e.key() == Qt.Key_Up:
        ## TODO: Up in history
        # e.accept()
        # self.keyPressed.emit(129)
        # pass
        # elif e.key() == Qt.Key_Down:
        ## TODO: Down in history
        # e.accept()
        # self.keyPressed.emit(130)
        # pass
        elif e.key() == Qt.Key.Key_Backspace:
            # If there IS something to delete
            if len(self.input_buf) > 0 and (self._input_cursor_pos != 0):
                del self.input_buf[self._input_cursor_pos - 1]
                self._input_cursor_pos -= 1
                self.textCursor().deletePreviousChar()
            # self.keyPressed.emit() # No keycode available for zscii
            e.accept()
        elif e.key() == Qt.Key.Key_Delete:
            if self._input_cursor_pos < len(self.input_buf):
                del self.input_buf[self._input_cursor_pos]
                self.textCursor().deleteChar()
            e.accept()
            self.keyPressed.emit(8)
        elif (e.key() == Qt.Key.Key_Return) or (e.key() == Qt.Key.Key_Enter):
            # Move cursor to the end of the line to avoid transferring text to the new line
            tc = self.textCursor()
            tc.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.MoveAnchor,
                len(self.input_buf) - self._input_cursor_pos,
            )
            self.setTextCursor(tc)
            # self.clean_input_buffer_from_screen()
            if self._cursor_visible is True:
                self.hide_cursor(self.last_window)
            # if (self.reading_line == True):
            # self.draw_input_buffer()
            text = ""
            for i in self.input_buf:
                text += i
            print(text)
            self.insertPlainText("\n")
            # self.draw_text('\n', 1, self.lastwindow)
            self.keyPressed.emit(13)
            self._input_cursor_pos = 0
            self.input_buf = []
            self.returnPressed.emit(text)
            e.accept()
        elif (e.key() >= Qt.Key.Key_F1) and (e.key() <= Qt.Key.Key_F12):
            e.accept()
            self.keyPressed.emit(133 + e.key() - Qt.Key.Key_F1)
        elif e.key() == Qt.Key.Key_Escape:
            e.accept()
            self.keyPressed.emit(27)
        elif e.text():
            if (self.reading_line) and (len(self.input_buf) < self.max_char + 1):
                # self.clean_input_buffer_from_screen()
                self.input_buf.insert(self._input_cursor_pos, str(e.text()))
                self._input_cursor_pos += 1
                self.insertPlainText(str(e.text()))
                # self.draw_input_buffer()
            e.accept()
            # TODO: Check if we can handle multiple events at once
            t = ord(e.text())
            if ((t > 31) and (t < 127)) or ((t > 154) and (t < 252)):
                self.keyPressed.emit(t)
        else:
            e.ignore()

    def set_text_colour(self, fg, win):
        self.cur_fg = fg
        self.setTextColor(self.ztoq_color[self.cur_fg])

    def set_text_background_colour(self, bg, win):
        self.cur_bg = bg
        self.setTextBackgroundColor(self.ztoq_color[self.cur_bg])

    def set_font_style(self, s, win):
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
        if self.reverse_video == True:
            tmpbg = self.cur_bg
            self.set_text_background_colour(self.cur_fg, win)
            self.set_text_colour(tmpbg, win)
        self.reverse_video = False
        # And now check for extra style
        if (self.cur_style & 1) == 1:  # Reverse video
            self.reverse_video = True
            tmpbg = self.cur_bg
            self.set_text_background_colour(self.cur_fg, win)
            self.set_text_colour(tmpbg, win)
        if (self.cur_style & 2) == 2:  # Bold
            newfont.setBold(True)
        if (self.cur_style & 4) == 4:  # Italic
            newfont.setItalic(True)
        if (self.cur_style & 8) == 8:  # Fixed Pitch
            newfont.setFixedPitch(True)
        self.setFont(newfont)

    def read_line(self, window, callback, time, timeout_callback, reset):
        self.last_window = window
        # print reset
        if reset == True:
            self.cur_pos = 0
        self.reading_line = True
        # self.update_game_area()
        self.callback_object = callback
        self.returnPressed.connect(self.read_line_callback)
        if self.line_timer == None:
            self.line_timer = QTimer()
            self.line_timer.setSingleShot(True)
        if time != 0:
            self.timeout_callback_object = timeout_callback
            self.line_timer.timeout.connect(self.read_line_timeout_callback)
            self.line_timer.start(time * 100)

    def read_line_callback(self, string):
        if self.line_timer != None:
            self.line_timer.stop()
        # print('read_line_callback: returnPressed disconnect')
        # self.returnPressed.disconnect()
        self.callback_object(string)

    def read_line_timeout_callback(self):
        self.line_timer.timeout.disconnect()
        self.timeout_callback_object()

    def disconnect_read_line(self, callback):
        self.reading_line = False
        self.returnPressed.disconnect()
        # self.returnPressed.disconnect(callback)

    def read_char(self, window, callback, time, timeout_callback):
        self.last_window = window
        self.callback_object = callback
        self.keyPressed.connect(self.read_char_callback)
        # print 'Connect char'
        if self.char_timer == None:
            self.char_timer = QTimer()
            self.char_timer.setSingleShot(True)
        if time != 0:
            self.timeout_callback_object = timeout_callback
            self.char_timer.timeout.connect(self.read_char_timeout_callback)
            self.char_timer.start(time * 100)

    def read_char_callback(self, key):
        if self.char_timer != None:
            self.char_timer.stop()
        # self.keyPressed.disconnect()
        self.callback_object(key)

    def read_char_timeout_callback(self):
        self.char_timer.timeout.disconnect()
        self.timeout_callback_object()

    def disconnect_read_char(self, callback):
        self.keyPressed.disconnect()
        # self.keyPressed.disconnect(callback)
        # print 'Disconnect char'

    def print_string(self, txt, window):
        txtlen = len(txt)
        if txtlen == 1:  # print_char got us here...
            self.draw_text(txt[0], 1, window)
        else:
            lastspace = 0
            i = 0
            textbuffer = ""
            tblen = 0
            for w in txt:
                if w == "\n":
                    if tblen > 0:  # If there is something to print
                        self.draw_text(textbuffer, tblen, window)
                        textbuffer = ""
                        tblen = 0
                    self.draw_text(w, 1, window)
                    if w == "\n":  # \n is whitespace :-)
                        lastspace = i
                elif w == " ":  # Space was found
                    if lastspace == (i - 1):  # Continuous spaces
                        textbuffer += w
                        tblen += 1
                    else:
                        self.draw_text(textbuffer, tblen, window)
                        self.draw_text(" ", 1, window)
                        textbuffer = ""
                        tblen = 0
                    lastspace = i
                else:
                    textbuffer += w
                    tblen += 1
                i += 1
            if textbuffer != "":  # Buffer not empty
                self.draw_text(textbuffer, tblen, window)
        self.ensureCursorVisible()

    def draw_text(self, txt, txtlen, window):
        if (txtlen > 0) and (
            self._cursor_visible == False
        ):  # If there IS something to print
            # if (self.pbuffer_painter[window.id] == None):
            # self.brush.setColor(self.ztoq_color[self.cur_bg])
            # self.pbuffer_painter[window.id] = QPainter(self.pbuffer[window.id])
            # self.pbuffer_painter[window.id].setPen(self.ztoq_color[self.cur_fg])
            # self.pbuffer_painter[window.id].setBackground(self.brush)

            # painter = self.pbuffer_painter[window.id]

            # @type window ZWindow
            if window.cursor == None:
                if window.id == 0:  # Main window
                    window.set_cursor_position(1, self.height)
                    window.set_cursor_real_position(
                        2, self.height * (self.line_size - 1)
                    )
                else:
                    window.set_cursor_position(1, 1)
                    window.set_cursor_real_position(2, self.line_size - 1)

            if txt == "\n":
                if window.cursor[1] == self.height:
                    if window.scrolling:
                        self.insertPlainText(txt)
                        # self.scroll(painter)
                    window.set_cursor_position(1, window.cursor[1])
                    window.set_cursor_real_position(2, window.cursor_real_pos[1])
                else:
                    window.set_cursor_position(1, window.cursor[1] + 1)
                    window.set_cursor_real_position(
                        2, window.cursor_real_pos[1] + self.line_size
                    )
            else:
                self.insertPlainText(txt)
                # rect = QRectF(window.cursor_real_pos[0], window.cursor_real_pos[1], self.pbuffer[window.id].width()-window.cursor_real_pos[0], self.linesize)

                # painter.setFont(self.font())
                # painter.setRenderHint(QPainter.TextAntialiasing)
                # if (self._input_buffer_printing == False):
                # painter.setBackgroundMode(Qt.OpaqueMode)
                # else:
                # painter.setBackgroundMode(Qt.TransparentMode)
                # bounding_rect = painter.boundingRect(rect,txt)
                # if (rect.contains(bounding_rect)):
                # print rect.x(), rect.y(), rect.width(),rect.height(), txt, bounding_rect
                # painter.drawText(bounding_rect, txt)
                # if txt != self.cursor_char:
                # window.set_cursor_position(window.cursor[0]+txtlen, window.cursor[1])
                # window.set_cursor_real_position(rect.x()+bounding_rect.width(), rect.y())
                # else: # There is not enough space
                # print "Not enough space to print:", txt
                # self.scroll(painter)
                # window.set_cursor_position(1, self.height)
                # window.set_cursor_real_position(2, self.height*(self.linesize-1))
                # rect.setX(2)
                # rect.setY(window.cursor_real_pos[1])
                # rect.setWidth(self.pbuffer[window.id].width()-window.cursor_real_pos[0])
                # rect.setHeight(self.linesize)
                # bounding_rect = painter.boundingRect(rect,txt)
                # painter.drawText(bounding_rect, txt)
                # if txt != self.cursor_char:
                # window.set_cursor_position(window.cursor[0]+txtlen, window.cursor[1])
                # window.set_cursor_real_position(rect.x()+bounding_rect.width(), rect.y())

    # def buffered_string(self, txt, window):
    # @type window ZWindow
    # if (window.buffering):
    # rect = QRect()
    # rect.setX(window.cursor_real_pos[0])
    # rect.setY(window.cursor_real_pos[1])
    # rect.setWidth(window.width-window.cursor_real_pos[0])
    # rect.setHeight(self.linesize)
    # bounding_rect = painter.boundingRect(rect,txt)
    # if (rect.contains(bounding_rect)): # string fits in this line
    # return txt
    # else:
    # return txt

    # def clean_input_buffer_from_screen(self):
    # rect = QRectF()
    # rect.setX(self.lastwindow.cursor_real_pos[0])
    # rect.setY(self.lastwindow.cursor_real_pos[1])
    # rect.setWidth(self.pbuffer[0].width()-self.lastwindow.cursor_real_pos[0])
    # rect.setHeight(self.linesize)
    # txtbuffer = ''
    # for w in self.input_buf:
    # txtbuffer += w
    # bounding_rect = self.pbuffer_painter[0].boundingRect(rect, txtbuffer)
    # if (rect.contains(bounding_rect)): # string fits in this line
    # self.pbuffer_painter[0].eraseRect(bounding_rect)
    # self.pbuffer_painter.drawRect(bounding_rect)
    # print 'Erasing rect', bounding_rect
    # else:
    # self.pbuffer_painter[0].eraseRect(rect)
    # print 'Erasing rect', rect
    # FIXME: clear next lines

    # def clear(self):
    # print 'clearing...'
    # self.game_area.fill(self.ztoq_color[self.cur_bg])
    # for i in xrange(8):
    # if (self.pbuffer[i] != None):
    # self.pbuffer[i].fill(self.ztoq_color[self.cur_bg])

    # def update_real_cursor_position(self, w):
    # w.set_cursor_real_position(2+(w.cursor[0]-1)*self.avgwidth, (w.cursor[1]-1)*self.linesize)
    # print w.cursor, '->', w.cursor_real_pos

    # def erase_window(self, window: ZWindow):
    #     print('erase_window for window', window.id)
    #     if ((window.id >= 0) and (window.id < 8)):
    #         if (self.pbuffer_painter[window.id] is None):
    #             self.pbuffer_painter[window.id] = QPainter(
    #                 self.pbuffer[window.id])
    #         self.pbuffer_painter[window.id].setPen(
    #             self.ztoq_color[self.cur_fg])
    #         self.brush.setColor(self.ztoq_color[self.cur_bg])
    #         self.pbuffer_painter[window.id].setBackground(self.brush)
    #         self.pbuffer_painter[window.id].setBackgroundMode(Qt.OpaqueMode)
    #         self.pbuffer_painter[window.id].eraseRect(
    #             QRectF(0, 0, self.pbuffer[window.id].width(), window.line_count*self.linesize))
    #         print(2, 0, self.pbuffer[window.id].width() -
    #               2, window.line_count*self.linesize)
    #     else:
    #         traceback.print_stack()
    #         print('erase_window for window', window.id)
    #         sys.exit()

    def split_window(self, lines, ver):
        if lines == 0:  # Unsplit
            pass
        else:
            if ver == 3:
                pass

    def stop_line_timer(self):
        if self.line_timer:
            self.line_timer.stop()

    def stop_char_timer(self):
        if self.char_timer:
            self.char_timer.stop()

    def mousePressEvent(self, e):
        pass

    def mouseDoubleClickEvent(self, e):
        pass
