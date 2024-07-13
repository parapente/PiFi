# -*- coding: utf-8

__author__ = "Theofilos Intzoglou"
__date__ = "$24 Ιουν 2009 2:39:50 πμ$"


from lib.memory import ZMemory
from lib.singleton import Singleton


class ZHeader(metaclass=Singleton):

    def __init__(self):
        mem = ZMemory().mem
        self.version = mem[0]

        # Flags 1 are going to be declared as properties later
        # except for those that don't ever change
        self.status_line_type = mem[0x01] & 0b10
        self.story_split_across_two_disks = mem[0x01] & 0b100
        self.release_number = 256*mem[0x02]+mem[0x03]
        # Initial value of the program counter
        self.pc = 256*mem[0x06]+mem[0x07]
        self.dictionary = 256*mem[0x08]+mem[0x09]
        self.obj_table = 256*mem[0x0a]+mem[0x0b]
        self.global_variables_table = 256*mem[0x0c]+mem[0x0d]
        self.static_memory_base = 256*mem[0x0e]+mem[0x0f]
        # Flags 2 are going to be declared as properties later
        self.abbrev_table = 256*mem[0x18]+mem[0x19]

        length = 256*mem[0x1a]+mem[0x1b]
        if length != 0:
            if self.version <= 3:
                self.length_of_file = length*2
            elif self.version < 6:
                self.length_of_file = length*4
            else:
                self.length_of_file = length*8
        else:
            self.length_of_file = len(mem)
        
        self.checksum = 256*mem[0x1c]+mem[0x1d]
        # Routines offset (divided by 8)
        self.routines = 256*mem[0x28]+mem[0x29]
        # Static strings offset (divided by 8)
        self.strings = 256*mem[0x2a]+mem[0x2b]
        self.terminating_characters_table = 256*mem[0x2e]+mem[0x2f]
        self.alphabet_table = 256*mem[0x34]+mem[0x35]
        self.header_ext_table = 256*mem[0x36]+mem[0x37]
        self.serial_number = ''.join([chr(x) for x in mem[0x12:0x18]])

    def _get_status_line_unavailable(self):
        return bool(ZMemory().get_memory_bit(0x01, 4))

    def _set_status_line_unavailable(self, unavailable: bool):
        ZMemory().set_memory_bit(0x01, 4, int(unavailable))

    def _get_screen_splitting_available(self):
        return bool(ZMemory().get_memory_bit(0x01, 5))
    
    def _set_screen_splitting_available(self, available: bool):
        ZMemory().set_memory_bit(0x01, 5, int(available))

    def _get_variable_pitch_font_as_default(self):
        return bool(ZMemory().get_memory_bit(0x01, 6))
    
    def _set_variable_pitch_font_as_default(self, is_default: bool):
        ZMemory().set_memory_bit(0x01, 6, int(is_default))

    def _get_colours_available(self):
        return bool(ZMemory().get_memory_bit(0x01, 0))
    
    def _set_colours_available(self, available: bool):
        ZMemory().set_memory_bit(0x01, 0, int(available))

    def _get_picture_displaying_available(self):
        return bool(ZMemory().get_memory_bit(0x01, 1))

    def _set_picture_displaying_available(self, available: bool):
        ZMemory().set_memory_bit(0x01, 1, int(available))

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

    def default_background_color(self):
        return self.header[0x2c]

    def default_foreground_color(self):
        return self.header[0x2d]

    def total_width(self):
        """ Total width in pixels of text sent to output stream 3 """
        return 256*self.header[0x30]+self.header[0x31]

    def standard_revision_number(self):
        return 256*self.header[0x32]+self.header[0x33]

    def print_all(self, plugin):
        plugin.debug_print("Abbrev table: {0}".format(self.abbrev_table), 2)
        plugin.debug_print("Alphabet table: {0}".format(
            self.alphabet_table), 2)
        plugin.debug_print("Characters table: {0}".format(
            self.terminating_characters_table), 2)
        plugin.debug_print("Dictionary: {0}".format(self.dictionary), 2)
        plugin.debug_print(
            "Global var table: {0}".format(self.global_variables_table), 2)
        plugin.debug_print("Header ext table: {0}".format(
            self.header_ext_table), 2)
        plugin.debug_print("Object table: {0}".format(self.obj_table), 2)
        plugin.debug_print(
            "Static strings offset: {0}".format(self.strings), 2)

    status_line_unavailable = property(
        fget=_get_status_line_unavailable,
        fset=_set_status_line_unavailable
    )
    screen_splitting_available = property(
        fget=_get_screen_splitting_available,
        fset=_set_screen_splitting_available
    )
    variable_pitch_font_as_default = property(
        fget=_get_variable_pitch_font_as_default,
        fset=_set_variable_pitch_font_as_default
    )
    colours_available = property(
        fget=_get_colours_available,
        fset=_set_colours_available
    )
    picture_displaying_available = property(
        fget=_get_picture_displaying_available,
        fset=_set_picture_displaying_available
    )
    