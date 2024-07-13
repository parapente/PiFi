# -*- coding: utf-8

from array import array
import sys

from lib.singleton import Singleton

__author__ = "Theofilos Intzoglou"
__date__ = "$17 Ιουν 2009 1:35:47 μμ$"


class ZMemory(metaclass=Singleton):
    mem = None
    static_beg = 0
    static_end = 0
    high_beg = 0
    high_end = 0

    def initialize(self, f: str = None, max_length: int = None) -> None:
        self.mem = array('B')
        if f:
            try:
                self.mem.fromfile(f, max_length)
            except EOFError:
                print(('file size:', f.tell()))
                need = max_length - f.tell()
                self.mem.extend([0]*need)
                # if ( need ) > 0:
                #    for i in xrange(need):
                #        self.mem.append(0)
            self.static_beg = 256*self.mem[0x0e]+self.mem[0x0f]
            self.high_beg = 256*self.mem[0x04]+self.mem[0x05]
        # for i in xrange(len(data)):
        #    self.mem.append(ord(data[i]));
        # print 'Static:',self.static_beg,'High:',self.high_beg
        # TODO: Find static_end

    def read(self, offset: int) -> int:
        """Function to be used with z-code to read a byte from specific offset"""
        if offset >= 0:
            if offset < self.static_beg:
                part = 1
            elif offset < self.static_end:
                part = 2
            else:
                part = 3
        else:
            print("Memory:read:Error! Negative offset!")
            sys.exit(1)

        if part == 1 or part == 2:
            return self.mem[offset]
        else:
            print("Memory:read:Error! Trying to access high memory!")
            sys.exit(1)

    def write(self, offset: int, data: int) -> None:
        """Function to be used with z-code to write to specific offset a byte"""
        if offset >= 0:
            if offset < self.static_beg:
                part = 1
            elif offset < self.static_end:
                part = 2
            else:
                part = 3
        else:
            print("Memory:write:Error! Negative offset!")
            sys.exit(1)

        if part == 1:
            self.mem[offset] = data
        elif part == 2:
            print("Memory:write:Error! Static memory is read only!")
            sys.exit(2)
        else:
            print("Memory:write:Error! Trying to access high memory!")
            sys.exit(1)

    def p_read(self, offset: int) -> int:
        """Generic function for reading bytes from Z memory"""
        if offset < 0:
            print("Memory:p_read:Error! Negative offset!")
            sys.exit(1)
        else:
            return self.mem[offset]

    def p_write(self, offset: int, data: int) -> None:
        """Generic function for writing bytes to Z memory"""
        if offset < 0:
            print("Memory:p_write:Error! Negative offset!")
            sys.exit(1)
        else:
            self.mem[offset] = data

    def get_memory_bit(self, address: int, bit: int):
        mask = 0b1 << bit
        return self.mem[address] & mask

    def set_memory_bit(self, address: int, bit: int, value: int):
        self.mem[address] &= 0xff - (1 << bit)
        if (value):
            self.mem[address] |= 1 << bit