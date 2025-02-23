# -*- coding: utf-8

__author__ = "Theofilos Intzoglou"
__date__ = "$24 Ιουν 2009 2:39:50 πμ$"


from functools import cache
from typing import cast
from lib.container.container import Container
from lib.error import InvalidArgumentException
from lib.memory import ZMemory


class ZHeader:
    def __init__(self):
        self.container = Container()
        self.memory = cast(ZMemory, self.container.resolve("ZMemory"))
        mem = self.memory.mem
        self.version = mem[0]

        # Flags 1 are going to be declared as properties later
        # except for those that don't ever change
        self.status_line_type = mem[0x01] & 0b10
        self.story_split_across_two_disks = mem[0x01] & 0b100
        self.release_number = 256 * mem[0x02] + mem[0x03]
        # Initial value of the program counter
        self.pc = 256 * mem[0x06] + mem[0x07]
        self.dictionary = 256 * mem[0x08] + mem[0x09]
        self.obj_table = 256 * mem[0x0A] + mem[0x0B]
        self.global_variables_table = 256 * mem[0x0C] + mem[0x0D]
        self.static_memory_base = 256 * mem[0x0E] + mem[0x0F]
        # Flags 2 are going to be declared as properties later
        self.abbrev_table = 256 * mem[0x18] + mem[0x19]

        length = 256 * mem[0x1A] + mem[0x1B]
        if length != 0:
            if self.version <= 3:
                self.length_of_file = length * 2
            elif self.version < 6:
                self.length_of_file = length * 4
            else:
                self.length_of_file = length * 8
        else:
            self.length_of_file = len(mem)

        self.checksum = 256 * mem[0x1C] + mem[0x1D]
        # Routines offset (divided by 8)
        self.routines = 256 * mem[0x28] + mem[0x29]
        # Static strings offset (divided by 8)
        self.strings = 256 * mem[0x2A] + mem[0x2B]
        self.terminating_characters_table = 256 * mem[0x2E] + mem[0x2F]
        self.alphabet_table = 256 * mem[0x34] + mem[0x35]
        self.header_ext_table = 256 * mem[0x36] + mem[0x37]
        self.serial_number = "".join([chr(x) for x in mem[0x12:0x18]])

    @property
    @cache
    def unicode_table(self):
        mem = self.memory.mem

        if self.version < 5:
            return 0

        if self.header_ext_num_words >= 3:
            return mem[self.header_ext_table + 6] * 256 + mem[self.header_ext_table + 7]

        return 0

    @property
    @cache
    def header_ext_num_words(self):
        mem = self.memory.mem

        if self.version < 5:
            return 0

        if self.header_ext_table:
            return mem[self.header_ext_table] * 256 + mem[self.header_ext_table + 1]

        return 0

    @property
    def status_line_unavailable(self):
        return bool(self.memory.get_memory_bit(0x01, 4))

    @status_line_unavailable.setter
    def status_line_unavailable(self, unavailable: bool):
        self.memory.set_memory_bit(0x01, 4, int(unavailable))

    @property
    def screen_splitting_available(self):
        return bool(self.memory.get_memory_bit(0x01, 5))

    @screen_splitting_available.setter
    def screen_splitting_available(self, available: bool):
        self.memory.set_memory_bit(0x01, 5, int(available))

    @property
    def variable_pitch_font_as_default(self):
        return bool(self.memory.get_memory_bit(0x01, 6))

    @variable_pitch_font_as_default.setter
    def variable_pitch_font_as_default(self, is_default: bool):
        self.memory.set_memory_bit(0x01, 6, int(is_default))

    @property
    def colours_available(self):
        return bool(self.memory.get_memory_bit(0x01, 0))

    @colours_available.setter
    def colours_available(self, available: bool):
        self.memory.set_memory_bit(0x01, 0, int(available))

    @property
    def picture_displaying_available(self):
        return bool(self.memory.get_memory_bit(0x01, 1))

    @picture_displaying_available.setter
    def picture_displaying_available(self, available: bool):
        self.memory.set_memory_bit(0x01, 1, int(available))

    @property
    def boldface_available(self):
        return bool(self.memory.get_memory_bit(0x01, 2))

    @boldface_available.setter
    def boldface_available(self, available: bool):
        self.memory.set_memory_bit(0x01, 2, int(available))

    @property
    def italic_available(self):
        return bool(self.memory.get_memory_bit(0x01, 3))

    @italic_available.setter
    def italic_available(self, available: bool):
        self.memory.set_memory_bit(0x01, 3, int(available))

    @property
    def fixed_space_font_available(self):
        return bool(self.memory.get_memory_bit(0x01, 4))

    @fixed_space_font_available.setter
    def fixed_space_font_available(self, available: bool):
        self.memory.set_memory_bit(0x01, 4, int(available))

    @property
    def sound_effects_available(self):
        return bool(self.memory.get_memory_bit(0x01, 5))

    @sound_effects_available.setter
    def sound_effects_available(self, available: bool):
        self.memory.set_memory_bit(0x01, 5, int(available))

    @property
    def timed_input_available(self):
        return bool(self.memory.get_memory_bit(0x01, 7))

    @timed_input_available.setter
    def timed_input_available(self, available: bool):
        self.memory.set_memory_bit(0x01, 7, int(available))

    @property
    def transcripting_is_on(self):
        return bool(self.memory.get_memory_bit(0x10, 0))

    @transcripting_is_on.setter
    def transcripting_is_on(self, enabled: bool):
        self.memory.set_memory_bit(0x10, 0, int(enabled))

    @property
    def game_forces_fixed_pitch_font(self):
        return bool(self.memory.get_memory_bit(0x10, 1))

    @game_forces_fixed_pitch_font.setter
    def game_forces_fixed_pitch_font(self, forces: bool):
        self.memory.set_memory_bit(0x10, 1, int(forces))

    @property
    def request_status_redraw(self):
        return bool(self.memory.get_memory_bit(0x10, 2))

    @request_status_redraw.setter
    def request_status_redraw(self, requested: bool):
        self.memory.set_memory_bit(0x10, 2, int(requested))

    @property
    def game_wants_pictures(self):
        return bool(self.memory.get_memory_bit(0x10, 3))

    @game_wants_pictures.setter
    def game_wants_pictures(self, enabled: bool):
        self.memory.set_memory_bit(0x10, 3, int(enabled))

    @property
    def game_wants_undo(self):
        return bool(self.memory.get_memory_bit(0x10, 4))

    @game_wants_undo.setter
    def game_wants_undo(self, enabled: bool):
        self.memory.set_memory_bit(0x10, 4, int(enabled))

    @property
    def game_wants_mouse(self):
        return bool(self.memory.get_memory_bit(0x10, 5))

    @game_wants_mouse.setter
    def game_wants_mouse(self, enabled: bool):
        self.memory.set_memory_bit(0x10, 5, int(enabled))

    @property
    def game_wants_colours(self):
        return bool(self.memory.get_memory_bit(0x10, 6))

    @game_wants_colours.setter
    def game_wants_colours(self, enabled: bool):
        self.memory.set_memory_bit(0x10, 6, int(enabled))

    @property
    def game_wants_sound_effects(self):
        return bool(self.memory.get_memory_bit(0x10, 7))

    @game_wants_sound_effects.setter
    def game_wants_sound_effects(self, enabled: bool):
        self.memory.set_memory_bit(0x10, 7, int(enabled))

    @property
    def game_wants_menus(self):
        return bool(self.memory.get_memory_bit(0x10, 8))

    @game_wants_menus.setter
    def game_wants_menus(self, enabled: bool):
        self.memory.set_memory_bit(0x10, 8, int(enabled))

    @property
    def interpreter_number(self):
        return self.memory.mem[0x1E]

    @interpreter_number.setter
    def interpreter_number(self, number: int):
        if number > 11 or number < 0:
            raise InvalidArgumentException(f"Invalid interpreter number '{number}'")
        self.memory.mem[0x1E] = number

    @property
    def interpreter_version(self):
        return self.memory.mem[0x1F]

    @interpreter_version.setter
    def interpreter_version(self, version: int):
        if version < 0 or version > 255:
            raise InvalidArgumentException(
                f"Invalid interpreter version '{version}'. It should be a single byte number."
            )
        self.memory.mem[0x1F] = version

    @property
    def screen_height_in_lines(self):
        """Screen height (lines): 255 means "infinite" """
        return self.memory.mem[0x20]

    @screen_height_in_lines.setter
    def screen_height_in_lines(self, lines: int):
        if lines < 0 or lines > 255:
            raise InvalidArgumentException(
                f"Invalid value for height in lines '{lines}'. Should be between 0 and 254 or 255 for infinite."
            )
        self.memory.mem[0x20] = lines

    @property
    def screen_width_in_chars(self):
        return self.memory.mem[0x21]

    @screen_width_in_chars.setter
    def screen_width_in_chars(self, chars: int):
        if chars < 0 or chars > 255:
            raise InvalidArgumentException(
                f"Invalid value for width in chars '{chars}'. Should be netween 0 and 255."
            )
        self.memory.mem[0x21] = chars

    @property
    def screen_width_in_units(self):
        mem = self.memory.mem
        return 256 * mem[0x22] + mem[0x23]

    @screen_width_in_units.setter
    def screen_width_in_units(self, units: int):
        if units < 0 or units > 65535:
            raise InvalidArgumentException(
                f"Invalid value for width in units '{units}'. Should be between 0 and 65535."
            )
        mem = self.memory.mem
        mem[0x22] = units // 256
        mem[0x23] = units % 256

    @property
    def screen_height_in_units(self):
        mem = self.memory.mem
        return 256 * mem[0x24] + mem[0x25]

    @screen_height_in_units.setter
    def screen_height_in_units(self, units: int):
        if units < 0 or units > 65535:
            raise InvalidArgumentException(
                f"Invalid value for height in units '{units}'. Should be between 0 and 65535."
            )
        mem = self.memory.mem
        mem[0x24] = units // 256
        mem[0x25] = units % 256

    @property
    def font_width(self):
        """Font width in units (defined as width of '0')"""
        mem = self.memory.mem
        if self.version == 5:
            return mem[0x26]
        else:
            return mem[0x27]

    @font_width.setter
    def font_width(self, units: int):
        if units < 0 or units > 255:
            raise InvalidArgumentException(
                f"Invalid value for font width in units '{units}'. Should be between 0 and 255."
            )
        mem = self.memory.mem
        if self.version == 5:
            mem[0x26] = units
        else:
            mem[0x27] = units

    @property
    def font_height(self):
        """Font height in units"""
        mem = self.memory.mem
        if self.version == 5:
            return mem[0x27]
        else:
            return mem[0x26]

    @font_height.setter
    def font_height(self, units: int):
        if units < 0 or units > 255:
            raise InvalidArgumentException(
                f"Invalid value for font height in units '{units}'. Should be between 0 and 255."
            )
        mem = self.memory.mem
        if self.version == 5:
            mem[0x27] = units
        else:
            mem[0x26] = units

    @property
    def default_background_colour(self):
        return self.memory.mem[0x2C]

    @default_background_colour.setter
    def default_background_colour(self, colour: int):
        if colour < 0 or colour > 255:
            raise InvalidArgumentException(
                f"Invalid value for default background colour '{colour}'. Should be between 0 and 255."
            )
        self.memory.mem[0x2C] = colour

    @property
    def default_foreground_colour(self):
        return self.memory.mem[0x2D]

    @default_foreground_colour.setter
    def default_foreground_colour(self, colour: int):
        if colour < 0 or colour > 255:
            raise InvalidArgumentException(
                f"Invalid value for default foreground colour '{colour}'. Should be between 0 and 255."
            )
        self.memory.mem[0x2D] = colour

    @property
    def total_width(self):
        """Total width in pixels of text sent to output stream 3"""
        mem = self.memory.mem
        return 256 * mem[0x30] + mem[0x31]

    @total_width.setter
    def total_width(self, width: int):
        if width < 0 or width > 65535:
            raise InvalidArgumentException(
                f"Invalid value for total width '{width}'. Should be between 0 and 65535."
            )
        mem = self.memory.mem
        mem[0x30] = width // 256
        mem[0x31] = width % 256

    @property
    def standard_revision_number(self):
        mem = self.memory.mem
        return 256 * mem[0x32] + mem[0x33]

    @standard_revision_number.setter
    def standard_revision_number(self, revision: int):
        if revision < 0 or revision > 65535:
            raise InvalidArgumentException(
                f"Invalid value for standard revision number '{revision}'. Should be between 0 and 65535."
            )
        mem = self.memory.mem
        mem[0x32] = revision // 256
        mem[0x33] = revision % 256

    def print_all(self, plugin):
        plugin.debug_print(f"Abbrev table: {self.abbrev_table}", 2)
        plugin.debug_print(f"Alphabet table: {self.alphabet_table}", 2)
        plugin.debug_print(f"Characters table: {self.terminating_characters_table}", 2)
        plugin.debug_print(f"Dictionary: {self.dictionary}", 2)
        plugin.debug_print(f"Global var table: {self.global_variables_table}", 2)
        plugin.debug_print(f"Header ext table: {self.header_ext_table}", 2)
        plugin.debug_print(f"Object table: {self.obj_table}", 2)
        plugin.debug_print(f"Static strings offset: {self.strings}", 2)
