# -*- coding: utf-8

from .ztext import *

__author__="oscar"
__date__ ="$28 Ιουλ 2009 3:33:47 μμ$"

class ZDictionary:
    dict = []
    separators = []
    word_length = 0
    data_length = 0

    def __init__(self, mem, header):
        zver = header.version
        addr = header.dictionary()
        n = mem[addr]
        if n > 0:
            for i in range(n):
                self.separators.append(chr(mem[addr + i + 1]))
        entry_length = mem[addr + 1 + n]
        entries = (mem[addr + 2 + n] << 8) + mem[addr + 3 + n]
        #print "Entries:", entries, " Entry length:", entry_length
        addr += 4 + n
        if zver < 4:
            self.word_length = 4
        else:
            self.word_length = 6
        j = 0
        while (j < entries):
            entry_addr = addr
            t = []
            for i in range(self.word_length):
                t.append(mem[addr + i])
            entry = decode_text(t, zver, mem, header.abbrev_table(), False, header.alphabet_table(), 0)
            #print "e[", j, "]=", entry
            self.data_length = entry_length - 4
            self.dict.append(entry)
            self.dict.append(entry_addr)
            addr += entry_length
            j += 1
        #print self.dict
        #print self.separators

    def find_word(self, w):
        #print w
        if w not in self.dict:
            return 0
        return self.dict[self.dict.index(w) + 1]
