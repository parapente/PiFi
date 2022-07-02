# -*- coding: utf-8

__author__ = "Theofilos Intzoglou"
__date__ = "$2 Ιουλ 2011 10:14:46 μμ$"


class ZWindow:
    cursor = None
    line_count = 0

    def __init__(self, wid):
        self.wrapping = True
        self.scrolling = True
        self.text_to_output2 = False
        self.buffering = True
        self.id = wid

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_size(self, width, height):
        self.width = width
        self.height = height

    def set_cursor_position(self, x, y):
        self.cursor = [x, y]

    def set_cursor_real_position(self, x, y):
        self.cursor_real_pos = [x, y]

    def set_wrapping(self, setting):
        self.wrapping = setting

    def set_scrolling(self, setting):
        self.scrolling = setting

    def set_text_to_output2(self, setting):
        self.text_to_output2 = setting

    def set_buffering(self, setting):
        self.buffering = setting

    def set_left_margin(self, x):
        self.left_margin = x

    def set_right_margin(self, x):
        self.right_margin = x

    def set_newline_interrupt_routine(self, addr):
        self.newline_interrupt_routine = addr

    def set_interrupt_countdown(self, count):
        self.interrupt_countdown = count

    def set_text_style(self, style):
        self.text_style = style

    def set_background_colour(self, colour):
        self.background_colour = colour

    def set_foreground_colour(self, colour):
        self.foreground_colour = colour

    def set_font_number(self, number):
        self.font = number

    def set_font_size(self, size):
        self.fontsize = size

    def set_line_count(self, count):
        self.line_count = count
