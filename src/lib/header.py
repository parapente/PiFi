# -*- coding: utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "Theofilos Intzoglou"
__date__ = "$24 Ιουν 2009 2:39:50 πμ$"


class ZHeader:
    header = None

    def __init__(self, h):
        self.header = h
        self.global_table = 256*h[0x0c]+h[0x0d]
        self.version = h[0]
        length = 256*self.header[0x1a]+self.header[0x1b]
        if length != 0:
            if self.version <= 3:
                self.length_of_file = length*2
            elif self.version < 6:
                self.length_of_file = length*4
            else:
                self.length_of_file = length*8
        else:
            self.length_of_file = len(h)

    # def version(self):
    #    """ Version of story file """
    #    return self.header[0]

    def release_number(self):
        """ Release Number """
        return 256*self.header[0x02]+self.header[0x03]

    def pc(self):
        """ Program Counter """
        return 256*self.header[0x06]+self.header[0x07]

    def dictionary(self):
        """ Location of dictionary """
        return 256*self.header[0x08]+self.header[0x09]

    def obj_table(self):
        """ Location of the object table """
        return 256*self.header[0x0a]+self.header[0x0b]

    # def global_table(self):
        """ Location of the global variables table """
    #    return 256*self.header[0x0c]+self.header[0x0d]

    def serial_number(self):
        """ Serial Number """
        return ''.join([chr(x) for x in self.header[0x12:0x18]])

    def abbrev_table(self):
        """ Location of the abbreviations table """
        return 256*self.header[0x18]+self.header[0x19]

    # def length_of_file(self):
    #    length = 256*self.header[0x1a]+self.header[0x1b]
    #    if length <> 0:
    #        if self.version <= 3:
    #            return length*2
    #        elif self.version < 6:
    #            return length*4
    #        else:
    #            return length*8
    #    else:
    #        return len(self.header)

    def checksum(self):
        """ Return the checksum stored in the file """
        return 256*self.header[0x1c]+self.header[0x1d]

    def interpreter_number(self):
        return self.header[0x1e]

    def interpreter_version(self):
        return self.header[0x1f]

    def screen_height_in_lines(self):
        return self.header[0x20]

    def screen_width_in_chars(self):
        return self.header[0x21]

    def screen_width_in_units(self):
        return 256*self.header[0x22]+self.header[0x23]

    def screen_height_in_units(self):
        return 256*self.header[0x24]+self.header[0x25]

    def font_width(self):
        """ Font width in units (defined as width of '0') """
        if self.version == 5:
            return self.header[0x26]
        else:
            return self.header[0x27]

    def font_height(self):
        """ Font height in units """
        if self.version == 5:
            return self.header[0x27]
        else:
            return self.header[0x26]

    def routines(self):
        """ Returns the routines offset in memory """
        return 256*self.header[0x28]+self.header[0x29]

    def strings(self):
        """ Returns the static strings offset in memory """
        return 256*self.header[0x2a]+self.header[0x2b]

    def default_background_color(self):
        return self.header[0x2c]

    def default_foreground_color(self):
        return self.header[0x2d]

    def characters_table(self):
        """ Address of terminating characters table """
        return 256*self.header[0x2e]+self.header[0x2f]

    def total_width(self):
        """ Total width in pixels of text sent to output stream 3 """
        return 256*self.header[0x30]+self.header[0x31]

    def standard_revision_number(self):
        return 256*self.header[0x32]+self.header[0x33]

    def alphabet_table(self):
        """ Returns the alphabet table address or 0 for default """
        return 256*self.header[0x34]+self.header[0x35]

    def header_ext_table(self):
        """ Returns the address of header extension table """
        return 256*self.header[0x36]+self.header[0x37]

    def score_game(self):
        """ Returns 0 if it is a score game, 1 if it is a timed game """
        return ((self.header[0x1] & 2) >> 1)

    def print_all(self, plugin):
        plugin.debugprint("Abbrev table: {0}".format(self.abbrev_table()), 2)
        plugin.debugprint("Alphabet table: {0}".format(
            self.alphabet_table()), 2)
        plugin.debugprint("Characters table: {0}".format(
            self.characters_table()), 2)
        plugin.debugprint("Dictionary: {0}".format(self.dictionary()), 2)
        plugin.debugprint("Global var table: {0}".format(self.global_table), 2)
        plugin.debugprint("Header ext table: {0}".format(
            self.header_ext_table()), 2)
        plugin.debugprint("Object table: {0}".format(self.obj_table()), 2)
        plugin.debugprint(
            "Static strings offset: {0}".format(self.strings()), 2)
