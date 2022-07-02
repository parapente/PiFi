# -*- coding: utf-8
import sys

__author__ = "Theofilos Intzoglou"
__date__ = "$1 Ιουλ 2009 5:20:39 μμ$"


class ZOutput:
    buffering = 1  # Buffering on
    version = 0
    plugin = None
    table_list = []
    table_list_len = 0
    mem = None

    def __init__(self, ver, mem, plugin):
        self.version = ver
        self.plugin = plugin
        self.mem = mem
        self.plugin.screen_size_callback = self.set_screen_size

    def select_stream(self, n, table):
        self.plugin.select_ostream(n)
        if table != -1:
            # We keep 2 ints for every ostream 3 (addr,offset)
            if self.table_list_len < 33:
                self.table_list.append(table)
                self.table_list.append(0)
                self.table_list_len += 2
            else:
                sys.exit("Output stream 3 is selected too many times!")

    def deselect_stream(self, n):
        if n == 3:
            tl = self.table_list
            tbl = self.table_list_len
            addr = tl[tbl - 2]
            numbytes = tl[tbl - 1]
            self.mem[addr] = numbytes >> 8
            self.mem[addr + 1] = numbytes & 0xff
            del tl[tbl - 1]
            del tl[tbl - 2]
            self.table_list_len -= 2
            if self.table_list_len == 0:
                self.plugin.deselect_ostream(n)
        else:
            self.plugin.deselect_ostream(n)

    def set_buffering(self, c):
        """Sets output buffering to on or off (1 or 0)"""
        # TODO: Implement proper buffering!
        if (self.version > 3):  # In V1-3 buffering is always on
            self.buffering = c

    def prints(self, s):
        # TODO: Buffering
        # print "Output streams:", self.plugin.selected_ostreams()
        if 3 in self.plugin.selected_ostreams():
            tbl = self.table_list_len
            tl = self.table_list
            addr = tl[tbl - 2]
            addr += 2
            l = len(s)
            chars = tl[tbl - 1]
            addr += chars
            tl[tbl - 1] = chars + l
            mem = self.mem
            # print 'Printing in memory {',addr,'} -- "', s,'"'
            x = addr
            for i in map(ord, s):
                if i == 10:
                    mem[x] = 13
                else:
                    mem[x] = i
                x += 1
        else:
            self.plugin.prints(s)

    def print_status(self, room, status):
        self.plugin.print_status(room, status)

    def printkey(self, key):
        # TODO: Implement printkey properly!
        if self.stream[4].on == 1:
            print(key)

    def print_input(self, s):
        if self.stream[1].selected == True:
            # TODO: Buffering
            print(s)
        if (self.stream[2].selected == True and self.stream[2].filename == None):
            # TODO: Do something to get the filename
            pass
        else:
            f.write(s)

    def clear_screen(self):
        self.plugin.clear_screen()

    def set_font_style(self, s):
        self.plugin.set_font_style(s)

    def show_upper_window(self, lines):
        self.plugin.show_upper_window(lines)

    def set_window(self, w):
        self.plugin.set_window(w)

    def set_cursor(self, y, x):
        self.plugin.set_cursor(y, x)

    def set_colour(self, fg, bg):
        self.plugin.set_colour(fg, bg)

    def new_line(self):
        self.plugin.new_line()

    def set_font(self, f):
        return self.plugin.set_font(f)

    def set_screen_size(self, w, h):
        if (self.version > 4):
            self.mem[0x22] = w // 256
            self.mem[0x23] = w % 256
            self.mem[0x24] = h // 256
            self.mem[0x25] = h % 256

        # The above is necessary because we can store only one byte
        if (h > 255):
            h = 255
        if (w > 255):
            w = 255
        self.mem[0x20] = h
        self.mem[0x21] = w
