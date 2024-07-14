# -*- coding: utf-8

from array import array
from io import BufferedReader
from lib.error import InvalidHighMemoryException
from lib.singleton import Singleton

__author__ = "Theofilos Intzoglou"
__date__ = "$17 Ιουν 2009 1:35:47 μμ$"


class ZMemory(metaclass=Singleton):
    mem = None
    static_beg = 0
    static_end = 0
    high_beg = 0
    high_end = 0

    def initialize(
        self, story_file: BufferedReader = None, max_length: int = None
    ) -> None:
        self.mem = array("B")
        if story_file:
            try:
                self.mem.fromfile(story_file, max_length)
            except EOFError:
                print(("file size:", story_file.tell()))
                need = max_length - story_file.tell()
                self.mem.extend([0] * need)
                # if ( need ) > 0:
                #    for i in xrange(need):
                #        self.mem.append(0)
            self.static_beg = 256 * self.mem[0x0E] + self.mem[0x0F]
            if story_file.tell() > 0xFFFF:
                self.static_end = 0xFFFF
            else:
                self.static_end = story_file.tell()
            self.high_beg = 256 * self.mem[0x04] + self.mem[0x05]
            self.high_end = story_file.tell()
            if self.high_beg < self.static_beg:
                raise InvalidHighMemoryException(
                    f"Invalid value for high memory start '{self.high_beg}'. Static memory begins at '{self.static_beg}'"
                )
        # for i in xrange(len(data)):
        #    self.mem.append(ord(data[i]));
        # print 'Static:',self.static_beg,'High:',self.high_beg

    def get_memory_bit(self, address: int, bit: int) -> int:
        """Read the value of a bit found at the address specified
        in the first argument

        Args:
            address (int): the address offset
            bit (int): the bit number (0-8)

        Returns:
            int: 0 or 1
        """
        mask = 0b1 << bit
        return int(bool(self.mem[address] & mask))

    def set_memory_bit(self, address: int, bit: int, value: int):
        """Set the value of a bit found at the address specified
        in the first argument

        Args:
            address (int): the address offset
            bit (int): the bit number (0-8)
            value (int): the value (0 or 1)
        """
        self.mem[address] &= 0xFF - (1 << bit)
        if value:
            self.mem[address] |= 1 << bit
