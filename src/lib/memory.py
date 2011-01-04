# -*- coding: utf-8
# To change this template, choose Tools | Templates
# and open the template in the editor.

from array import array
import sys

__author__="oscar"
__date__ ="$17 Ιουν 2009 1:35:47 μμ$"

class ZMemory:
    mem = None;
    static_beg = 0;
    static_end = 0;
    high_beg = 0;
    high_end = 0;
    def __init__(self,data,max_length):
        self.mem = array('B');
        for i in range(len(data)):
            self.mem.append(ord(data[i]));
        if ( max_length - len(data) ) <> 0:
            for i in range(max_length-len(data)):
                self.mem.append(0)
        self.static_beg = 256*self.mem[0x0e]+self.mem[0x0f];
        self.high_beg = 256*self.mem[0x04]+self.mem[0x05];
        print 'Static:',self.static_beg,'High:',self.high_beg
        # TODO: Find static_end

    def read(self,offset):
        """Function to be used with z-code to read a byte from specific offset"""
        if offset >= 0:
            if offset < self.static_beg:
                part = 1;
            elif offset < self.static_end:
                part = 2;
            else:
                part = 3;
        else:
            print "Memory:read:Error! Negative offset!";
            sys.exit(1);

        if part == 1 or part == 2:
            return self.mem[offset];
        else:
            print "Memory:read:Error! Trying to access high memory!";
            sys.exit(1);

    def write(self,offset,data):
        """Function to be used with z-code to write to specific offset a byte"""
        if offset >= 0:
            if offset < self.static_beg:
                part = 1;
            elif offset < self.static_end:
                part = 2;
            else:
                part = 3;
        else:
            print "Memory:write:Error! Negative offset!";
            sys.exit(1);

        if part == 1:
            self.mem[offset] = data;
        elif part == 2:
            print "Memory:write:Error! Static memory is read only!"
            sys.exit(2);
        else:
            print "Memory:write:Error! Trying to access high memory!";
            sys.exit(1);

    def p_read(self,offset):
        """Generic function for reading bytes from Z memory"""
        if offset < 0:
            print "Memory:p_read:Error! Negative offset!";
            sys.exit(1);
        else:
            return self.mem[offset];

    def p_write(self,offset,data):
        """Generic function for writing bytes to Z memory"""
        if offset < 0:
            print "Memory:p_write:Error! Negative offset!";
            sys.exit(1);
        else:
            self.mem[offset] = data;