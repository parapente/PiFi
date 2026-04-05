# To change this template, choose Tools | Templates
# and open the template in the editor.

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QBrush
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import QObject
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import QTimer
from lib.stream import ZStream
import sys


class ZTextWidget(QWidget):
    returnPressed = pyqtSignal(str)
    keyPressed = pyqtSignal(int)

    def __init__(self, parent=None, flags=Qt.WindowType.Widget):
        super(ZTextWidget, self).__init__(parent, flags)
        self.upper_buf = []
        self.upper_buf_height = 0
        self.upper_win_cursor = []
        self.lower_win_cursor = 1
        self.fixed_font = None
        self.fixed_font_metrics = None
        self.fixed_font_width = 0
        self.fixed_font_height = 0
        self.buf = []
        self.zwidth = 80
        self.zheight = 26
        self.cur_win = 0
        self.cur_fg = 10
        self.cur_bg = 2
        self.cur_style = 0
        self.max_char = 0
        self.start_pos = 0
        self.top_pos = 0
        self.cur_pos = 0
        self.input_buf = []
        self._cursor_visible = False
        self._output_stream = None
        self.chartimer = None
        self.linetimer = None
        sp = QSizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        sp.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        self.set_fixed_font("DeJa Vu Sans Mono", 9)
        self.setSizePolicy(sp)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._output_stream = [ZStream(), ZStream(), ZStream(), ZStream()]
        self._output_stream[0].selected = True
        for i in range(self.zwidth * self.zheight * 4):
            self.buf.append(0)

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.fillRect(
            0,
            0,
            self.zwidth * self.fixed_font_width + 2,
            self.zheight * self.fixed_font_height,
            Qt.GlobalColor.black,
        )
        painter.setPen(Qt.GlobalColor.gray)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setFont(self.fixed_font)
        # Print main window
        l = self.zheight
        while l > 0:
            c = 1
            while c <= self.zwidth:
                y = self.fixed_font_metrics.ascent() + (l - 1) * self.fixed_font_height
                x = 1 + ((c - 1) * self.fixed_font_width)
                # print "**",l,"**",c
                if self.buf[(((self.zheight - l) * self.zwidth) + c - 1) * 4] == 0:
                    painter.setPen(self.ztoq_color(self.cur_fg))
                else:
                    painter.setPen(
                        self.ztoq_color(
                            self.buf[(((self.zheight - l) * self.zwidth) + c - 1) * 4]
                        )
                    )
                if (
                    self.buf[((((self.zheight - l) * self.zwidth) + c - 1) * 4) + 1]
                    == 0
                ):
                    painter.setBackground(QBrush(self.ztoq_color(self.cur_bg)))
                else:
                    painter.setBackground(
                        QBrush(
                            self.ztoq_color(
                                self.buf[
                                    ((((self.zheight - l) * self.zwidth) + c - 1) * 4)
                                    + 1
                                ]
                            )
                        )
                    )
                # Set appropriate font style
                if (
                    self.buf[((((self.zheight - l) * self.zwidth) + c - 1) * 4) + 2]
                    == 0
                ):
                    f = painter.font()
                    f.setBold(False)
                    f.setItalic(False)
                    painter.setFont(f)
                if (
                    self.buf[((((self.zheight - l) * self.zwidth) + c - 1) * 4) + 2] & 1
                ):  # Reverse video
                    painter.setPen(
                        self.ztoq_color(
                            self.buf[
                                ((((self.zheight - l) * self.zwidth) + c - 1) * 4) + 1
                            ]
                        )
                    )
                    painter.setBackground(
                        QBrush(
                            self.ztoq_color(
                                self.buf[
                                    (((self.zheight - l) * self.zwidth) + c - 1) * 4
                                ]
                            )
                        )
                    )
                if (
                    self.buf[((((self.zheight - l) * self.zwidth) + c - 1) * 4) + 2] & 2
                ):  # Bold
                    f = painter.font()
                    f.setBold(True)
                    painter.setFont(f)
                if (
                    self.buf[((((self.zheight - l) * self.zwidth) + c - 1) * 4) + 2] & 4
                ):  # Italic
                    f = painter.font()
                    f.setItalic(True)
                    painter.setFont(f)
                if (
                    self.buf[((((self.zheight - l) * self.zwidth) + c - 1) * 4) + 3]
                    != 0
                ):
                    painter.drawText(
                        x,
                        y,
                        self.buf[
                            ((((self.zheight - l) * self.zwidth) + c - 1) * 4) + 3
                        ],
                    )
                c += 1
            l -= 1
            c = 1
        # Print upper window
        if self.upper_buf != []:
            l = 1
            while l <= self.upper_buf_height:
                c = 1
                while c <= self.zwidth:
                    y = (
                        self.fixed_font_metrics.ascent()
                        + (l - 1) * self.fixed_font_height
                    )
                    x = 1 + ((c - 1) * self.fixed_font_width)
                    # print "**",l,"**",c
                    if self.upper_buf[((((l - 1) * self.zwidth) + c - 1) * 4) + 3] != 0:
                        painter.setPen(
                            self.ztoq_color(
                                self.upper_buf[(((l - 1) * self.zwidth) + c - 1) * 4]
                            )
                        )
                        painter.setBackground(
                            QBrush(
                                self.ztoq_color(
                                    self.upper_buf[
                                        ((((l - 1) * self.zwidth) + c - 1) * 4) + 1
                                    ]
                                )
                            )
                        )
                        # Set appropriate font style
                        if (
                            self.upper_buf[((((l - 1) * self.zwidth) + c - 1) * 4) + 2]
                            == 0
                        ):
                            f = painter.font()
                            f.setBold(False)
                            f.setItalic(False)
                            painter.setFont(f)
                        # Reverse video
                        if (
                            self.upper_buf[((((l - 1) * self.zwidth) + c - 1) * 4) + 2]
                            & 1
                        ):
                            painter.setPen(
                                self.ztoq_color(
                                    self.upper_buf[
                                        ((((l - 1) * self.zwidth) + c - 1) * 4) + 1
                                    ]
                                )
                            )
                            painter.setBackground(
                                QBrush(
                                    self.ztoq_color(
                                        self.upper_buf[
                                            (((l - 1) * self.zwidth) + c - 1) * 4
                                        ]
                                    )
                                )
                            )
                        if (
                            self.upper_buf[((((l - 1) * self.zwidth) + c - 1) * 4) + 2]
                            & 2
                        ):  # Bold
                            f = painter.font()
                            f.setBold(True)
                            painter.setFont(f)
                        # Italic
                        if (
                            self.upper_buf[((((l - 1) * self.zwidth) + c - 1) * 4) + 2]
                            & 4
                        ):
                            f = painter.font()
                            f.setItalic(True)
                            painter.setFont(f)
                        painter.drawText(
                            x,
                            y,
                            self.upper_buf[((((l - 1) * self.zwidth) + c - 1) * 4) + 3],
                        )
                    c += 1
                l += 1
        # Print cursor if visible
        if self._cursor_visible:
            self.display_cursor()

    def sizeHint(self):
        size = QSize()
        size.setWidth(self.zwidth * self.fixed_font_width + 2)
        size.setHeight(self.zheight * self.fixed_font_height)
        return size

    def set_fixed_font(self, name, size):
        self.fixed_font = QFont(name, size)
        self.fixed_font.setFixedPitch(True)
        self.fixed_font.setKerning(False)
        self.fixed_font_metrics = QFontMetrics(self.fixed_font)
        self.fixed_font_width = self.fixed_font_metrics.averageCharWidth()
        self.fixed_font_height = self.fixed_font_metrics.height()
        # print self.fixed_font_width, self.fixed_font_height

    def ztoq_color(self, c):
        if c == 2:
            return Qt.GlobalColor.black
        elif c == 3:
            return Qt.GlobalColor.red
        elif c == 4:
            return Qt.GlobalColor.green
        elif c == 5:
            return Qt.GlobalColor.yellow
        elif c == 6:
            return Qt.GlobalColor.blue
        elif c == 7:
            return Qt.GlobalColor.magenta
        elif c == 8:
            return Qt.GlobalColor.cyan
        elif c == 9:
            return Qt.GlobalColor.white
        elif c == 10:
            return Qt.GlobalColor.lightGray
        elif c == 11:
            return Qt.GlobalColor.gray
        elif c == 12:
            return Qt.GlobalColor.darkGray

    def set_cursor(self, x, y):
        self.upper_win_cursor = [y, x]

    def set_window(self, w):
        print(f"DEBUG set_window: w={w}, cur_win was {self.cur_win}")
        if w < 2:
            self.cur_win = w
        else:
            sys.exit(f"Unknown window {w}?!?")

    def print_string(self, txt):
        print(f"DEBUG print_string: txt='{txt}'")
        if self._output_stream[0].selected:
            if self.cur_win == 0:  # Lower win
                # TODO: Buffering
                c = self.lower_win_cursor
                i = 0
                total = len(txt)
                # print "Total -", total
                while i < total:
                    s = ""
                    while (i < total) and (txt[i] != "\n") and (c <= self.zwidth):
                        s += txt[i]
                        i += 1
                        c += 1
                    self.print_line(s)
                    # print "--> [i, c, total]", i, c, total, " ++ ", s
                    if c > self.zwidth:
                        self.insert_new_line()
                        self.lower_win_cursor = 1
                        c = 1
                    elif (i < total) and (txt[i] == "\n"):
                        self.insert_new_line()
                        self.lower_win_cursor = 1
                        c = 1
                        i += 1
                    # elif (i == total) and (txt[i-1] <> '\n'):
                    else:
                        self.lower_win_cursor += len(s)
            else:
                i = self.upper_win_cursor[0]
                j = 0
                l = self.upper_win_cursor[1]
                while (i <= self.zwidth) and (j < len(txt)):
                    if l > self.upper_buf_height:
                        print(
                            "Upper buffer overflow! I cannot print more lines in upper window! Please split the window again with more lines for upper window!"
                        )
                        print(
                            f"DEBUG split_window: lines={self.upper_buf_height}, zwidth={self.zwidth}, zheight={self.zheight}, upper_buf len={len(self.upper_buf)} l={l} i={i} j={j}"
                        )
                        return
                    if txt[j] != "\n":
                        self.upper_buf[(((l - 1) * self.zwidth) + (i - 1)) * 4] = (
                            self.cur_fg
                        )
                        self.upper_buf[
                            ((((l - 1) * self.zwidth) + (i - 1)) * 4) + 1
                        ] = self.cur_bg
                        self.upper_buf[
                            ((((l - 1) * self.zwidth) + (i - 1)) * 4) + 2
                        ] = self.cur_style
                        self.upper_buf[
                            ((((l - 1) * self.zwidth) + (i - 1)) * 4) + 3
                        ] = txt[j]
                        i += 1
                        j += 1
                    else:
                        self.upper_win_cursor = [1, l + 1]
                        i = 1
                        l += 1
                        j += 1
                self.upper_win_cursor[0] += j
            self.update()

    def print_line(self, txt):
        col = self.lower_win_cursor
        # print "Column:", col, txt
        if self.cur_win == 0:  # Lower win
            for i in range(len(txt)):
                self.buf[(col - 1 + i) * 4] = self.cur_fg
                self.buf[((col - 1 + i) * 4) + 1] = self.cur_bg
                self.buf[((col - 1 + i) * 4) + 2] = self.cur_style
                self.buf[((col - 1 + i) * 4) + 3] = txt[i]

    def print_char(self, c):
        col = self.lower_win_cursor
        if self.cur_win == 0:  # Lower win
            if c != "\n":
                self.buf[(col - 1) * 4] = self.cur_fg
                self.buf[((col - 1) * 4) + 1] = self.cur_bg
                self.buf[((col - 1) * 4) + 2] = self.cur_style
                self.buf[((col - 1) * 4) + 3] = c
                self.lower_win_cursor += 1
            if self.lower_win_cursor > self.zwidth:  # If we exceed screen width
                # print "I insert a newline"
                self.insert_new_line()
                self.lower_win_cursor = 1
            elif c == "\n":
                self.insert_new_line()
                self.lower_win_cursor = 1
        self.update()

    def set_max_input(self, m):
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
        y = self.fixed_font_metrics.ascent() + (
            (self.zheight - 1) * self.fixed_font_height
        )
        x = 1 + ((col - 1) * self.fixed_font_width)
        painter.setPen(self.ztoq_color(self.cur_fg))
        painter.setBackground(QBrush(self.ztoq_color(self.cur_bg)))
        painter.drawText(x, y, chr(0x2581))

    def keyPressEvent(self, a0):
        if a0 is None:
            return

        if a0.key() == Qt.Key.Key_Left:
            if self.cur_pos > self.start_pos:
                self.cur_pos -= 1
                self.update()
            a0.accept()
            self.keyPressed.emit(131)
        elif a0.key() == Qt.Key.Key_Right:
            if self.cur_pos < self.top_pos:
                self.cur_pos += 1
                self.update()
            a0.accept()
            self.keyPressed.emit(132)
        elif a0.key() == Qt.Key.Key_Up:
            # TODO: Up in history
            a0.accept()
            self.keyPressed.emit(129)
            pass
        elif a0.key() == Qt.Key.Key_Down:
            # TODO: Down in history
            a0.accept()
            self.keyPressed.emit(130)
            pass
        elif a0.key() == Qt.Key.Key_Backspace:
            if self.cur_pos > self.start_pos:
                self.cur_pos -= 1
                self.top_pos -= 1
                col = self.cur_pos - 1
                for i in range(4):
                    self.buf[col * 4 + i] = 0
                del self.input_buf[self.cur_pos - self.start_pos]
                # print self.input_buf
                self.lower_win_cursor -= 1
                self.update()
            # self.keyPressed.emit() # No keycode available for zscii
            a0.accept()
        elif a0.key() == Qt.Key.Key_Delete:
            # TODO: Fix it!
            if self.cur_pos < self.top_pos:
                self.top_pos -= 1
                col = self.cur_pos - 1
                for i in range(4):
                    self.buf[col * 4 + i] = 0
                del self.input_buf[self.cur_pos - self.start_pos]
                self.lower_win_cursor -= 1
                self.update()
            a0.accept()
            self.keyPressed.emit(8)
        elif (a0.key() == Qt.Key.Key_Return) or (a0.key() == Qt.Key.Key_Enter):
            # TODO: Learn how to properly convert a list of chars to a string. There MUST be another way! >:-S
            text = ""
            for i in range(len(self.input_buf)):
                text += self.input_buf[i]
            # print text
            self.print_char("\n")
            self.hide_cursor()
            self.keyPressed.emit(13)
            self.returnPressed.emit(text)
            a0.accept()
        elif (a0.key() >= Qt.Key.Key_F1) and (a0.key() <= Qt.Key.Key_F12):
            a0.accept()
            self.keyPressed.emit(133 + a0.key() - Qt.Key.Key_F1)
        elif a0.key() == Qt.Key.Key_Escape:
            a0.accept()
            self.keyPressed.emit(27)
        elif len(a0.text()) > 0:
            # print self.cur_pos, self.start_pos, self.max_char
            if (self.cur_pos - self.start_pos) < self.max_char:
                self.cur_pos += 1
                self.top_pos += 1
                if (self.cur_pos - self.start_pos) <= len(self.input_buf):
                    self.input_buf.insert(
                        self.cur_pos - self.start_pos - 1, str(a0.text())
                    )
                    # print "CurPos:", self.cur_pos
                    col = self.cur_pos - 2
                    self.buf[col * 4 + 3] = str(a0.text())
                    self.buf[col * 4 + 2] = 0
                    self.buf[col * 4 + 1] = self.cur_bg
                    self.buf[col * 4] = self.cur_fg
                    self.lower_win_cursor += 1
                else:
                    self.input_buf.append(str(a0.text()))
                    self.print_char(a0.text())
                # print self.input_buf
                self.update()
            a0.accept()
            t = ord(str(a0.text()))
            if ((t > 31) and (t < 127)) or ((t > 154) and (t < 252)):
                self.keyPressed.emit(t)
        else:
            a0.ignore()

    def set_text_colour(self, fg):
        self.cur_fg = fg

    def set_text_background_colour(self, bg):
        self.cur_bg = bg

    def set_font_style(self, s):
        if s == 0:
            self.cur_style = 0
        else:
            self.cur_style |= s

    def clear(self):
        for i in range(self.zwidth * self.zheight * 4):
            self.buf[i] = 0
        self.upper_buf = []
        self.upper_buf_height = 0
        self.upper_win_cursor = []  # Upper win cursor x,y
        self.lower_win_cursor = 1  # Lower win cursor x (y cannot be changed!)
        self.cur_win = 0  # Default win is the lower (1 is for upper win)

    def split_window(self, lines, ver):
        print(
            f"DEBUG split_window: lines={lines}, ver={ver}, old upper_buf_height={self.upper_buf_height}, upper_buf len={len(self.upper_buf)}"
        )
        if (
            self.upper_buf_height > lines
        ):  # New upper win is smaller. I should copy the rest of the buffer to main buffer
            # print "Copying..."
            l = lines + 1
            while l <= self.upper_buf_height:
                for i in range(self.zwidth * 4):
                    self.buf[(((self.zheight - l + 1) * self.zwidth) * 4) + i] = (
                        self.upper_buf[(((l - 1) * self.zwidth) * 4) + i]
                    )
                l += 1
        self.upper_buf_height = lines
        if (self.upper_buf == []) or (ver == 3):
            # It isn't necessary to occupy that much memory but it helps to be prepared! :-P
            for i in range(self.upper_buf_height * self.zwidth * 4):
                self.upper_buf.append(0)
        if (self.upper_win_cursor == []) or (self.upper_win_cursor[1] > lines):
            self.upper_win_cursor = [1, 1]

    def select_output_stream(self, n):
        if n != 0:
            self._output_stream[n - 1].selected = True

    def deselect_output_stream(self, n):
        self._output_stream[n - 1].selected = False

    def insert_new_line(self):
        # print "New line"
        # TODO: Not just insert new lines but also remove old unwanted ones
        for i in range(self.zwidth * 4):
            self.buf.insert(0, 0)

    def read_line(self, callback):
        self.returnPressed.connect(callback)

    def disconnect_read_line(self, callback):
        self.returnPressed.disconnect(callback)

    def read_char(self, callback):
        self.keyPressed.connect(callback)
        print("Connect char")

    def disconnect_read_char(self, callback):
        self.keyPressed.disconnect(callback)
        print("Disconnect char")

    def selected_output_streams(self):
        s = []
        for i in range(4):
            if self._output_stream[i].selected == True:
                s.append(i + 1)
        return s

    def new_line(self):
        if self._output_stream[0].selected:
            if self.cur_win == 0:  # Lower win
                self.insert_new_line()
                self.lower_win_cursor = 1
            else:  # Upper win
                l = self.upper_win_cursor[1]
                self.upper_win_cursor = [1, l + 1]

    def stop_line_timer(self):
        if self.linetimer is not None:
            self.linetimer.stop()

    def stop_char_timer(self):
        if self.chartimer is not None:
            self.chartimer.stop()
