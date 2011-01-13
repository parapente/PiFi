# -*- coding: utf-8

from memory import ZMemory
from cpu import ZCpu
from header import ZHeader
from input import ZInput
from output import ZOutput
from ztext import *
from dictionary import ZDictionary
import sys

__author__="Theofilos Intzoglou"
__date__ ="$1 Ιουλ 2009 4:39:00 μμ$"

class ZMachine:
    mem = None
    header = None
    cpu = None
    plugin = None
    input = None
    output = None
    dict = None
    zver = None
    file = None

    def __init__(self,w):
        self.plugin = w

    def boot(self):
        self.cpu.start()
        self.handle_intr()

    def handle_intr(self):
        if self.cpu.intr == 1: # Input interrupt to read a line of text
            self.input.read_line(self.mem.mem[self.cpu.intr_data[0]], self.get_text)
        elif self.cpu.intr == 2: # Input interrupt to read a character
            self.input.read_char(self.get_char)
        elif self.cpu.intr == 3: # Reset interrupt
            self.file.seek(0)
            self.output.clear_screen()
            self.load_story(self.file)
            self.boot()
        elif self.cpu.intr == 4: # Tokenise interrupt
            self.lex(self.cpu.intr_data[0],self.cpu.intr_data[1],self.cpu.intr_data[2],self.cpu.intr_data[3])
            self.cpu.intr = 0
            self.cpu.start()
            self.handle_intr()

    def get_text(self,text):
        self.plugin.debugprint("Enter!", 2)
        self.input.disconnect_input(self.get_text)
        self.input.hide_cursor()
        paddr = self.cpu.intr_data[1]
        taddr = self.cpu.intr_data[0]
        self.plugin.debugprint("gt -> '"+text+"'", 2)
        if self.zver < 5:
            for i in range(len(text)):
                if (i == (len(text) - 1)) and text[i] == '\n':
                    self.mem.mem[taddr + 1 + i] = 0
                else:
                    self.mem.mem[taddr + 1 + i] = ord(str(text[i]))
            i += 1
            self.mem.mem[taddr + 1 + i] = 0
        else:
            for i in range(len(text)):
                self.mem.mem[taddr + 2 + i] = ord(str(text[i]))
            self.mem.mem[taddr + 1] = len(text)
        self.lex(taddr,paddr,0,0)
        self.cpu.intr = 0
        if self.zver > 4:
            self.cpu.got_char(10)
        self.cpu.start()
        self.handle_intr()

    def lex(self,text,parse,dict,flag):
        if dict <> 0 or flag <> 0:
            sys.exit("LEX: Not supported yet!")
        txt = ""
        if self.zver < 5:
            i = 0
            while self.mem.mem[text + 1 + i ] <> 0:
                txt += unichr(self.mem.mem[text + 1 + i])
                i += 1
        else:
            for i in range(self.mem.mem[text + 1]):
                txt += unichr(self.mem.mem[text + 2 + i])
        l = len(txt)
        self.plugin.debugprint("txt='"+txt+"' Len:"+l, 2)
        words = []
        w = ""
        i = 0
        while (i < l):
            while (i < l) and ((txt[i] not in self.dict.separators) and (txt[i] <> " ")):
                w += txt[i]
                i += 1
            if (w <> "") and (w <> " "):
                pos = i - len(w)
                words.append(str(w))
                if self.zver < 5:
                    words.append(pos + 1)
                else:
                    words.append(pos + 2)
            if (i < l) and (txt[i] in self.dict.separators):
                words.append(str(txt[i]))
                if self.zver < 5:
                    words.append(i + 1)
                else:
                    words.append(i + 2)
                i += 1
            if (i < l) and (txt[i] == " "):
                i += 1
            w = ""
        self.mem.mem[parse + 1] = len(words) // 2
        parse += 2
        i = 0
        while i < len(words):
            w1 = ""
            # If the word is too large we need to cut it down
            if len(words[i]) > (self.dict.word_length * 3 / 2):
                for j in range(self.dict.word_length * 3 / 2):
                    w1 += words[i][j]
            else:
                w1 = words[i]
            self.plugin.debugprint(w1+"- len -"+len(w1), 2)
            if self.cpu.intr_data[1] <> 0: # No parsing is required
                # Find the data for the record
                addr = self.dict.find_word(w1)
                l = len(words[i])
                pos = words[i + 1]
                self.plugin.debugprint("word:"+w1+"Addr:"+addr+"Pos:"+pos, 2)
                # Write the record in parse buffer
                self.mem.mem[parse] = addr >> 8
                self.mem.mem[parse + 1] = addr & 0xff
                self.mem.mem[parse + 2] = l
                self.mem.mem[parse + 3] = pos
                parse += 4
            i += 2

    def get_char(self,char):
        self.input.disconnect_input(self.get_char)
        self.plugin.debugprint("Character read!", 2)
        self.cpu.got_char(char)
        self.cpu.intr = 0
        self.cpu.start()
        self.handle_intr()

    def load_story(self,f):
        # @type f file
        # Read the first byte of the file to determine the version of the story
        self.file = f
        b = ord(f.read(1))
        if (b < 4):
            max_length = 128 * 1024
        elif (b < 6):
            max_length = 256 * 1024
        elif (b == 6 or b == 8):
            max_length = 512 * 1024
        elif (b == 7):
            max_length = 320 * 1024
        else:
            print 'Not a valid story file'
            sys.exit(10)

        # Now that we checked the file size we rewind the file and read the data into memory
        f.seek(0)
        data = f.read(max_length)
        self.mem = ZMemory(data,max_length)
        self.header = ZHeader(self.mem.mem)
        self.header.print_all(self.plugin)
        self.input = ZInput(self.plugin)
        self.zver = self.header.version()
        self.output = ZOutput(self.zver, self.mem.mem, self.plugin)
        self.cpu = ZCpu(self.mem.mem,self.header,self.output,self.plugin)
        self.cpu.file = f
        self.dict = ZDictionary(self.mem.mem, self.header)
        self.plugin.debugprint('Version of story file: {0}'.format(self.zver), 1)
        self.plugin.debugprint('Length of file: {0}'.format(self.header.length_of_file()), 1)

    def init(self):
        # Set the default options
        # Interpreter number and version
        self.mem.mem[0x1e] = 1
        if self.zver <> 6:
            self.mem.mem[0x1f] = ord('A')
        else:
            self.mem.mem[0x1f] = 1
        # Width and height of window
        self.mem.mem[0x20] = self.plugin.height()
        self.mem.mem[0x21] = self.plugin.width()
        # Width and height of window in units
        self.mem.mem[0x22] = 0
        self.mem.mem[0x23] = self.mem.mem[0x21]
        self.mem.mem[0x24] = 0
        self.mem.mem[0x25] = self.mem.mem[0x20]
        # Standard revision number
        self.mem.mem[0x32] = 1
        # Font width in units
        self.mem.mem[0x26] = 1
        # Font height in units
        self.mem.mem[0x27] = 1
        # Default supported options
        if self.zver < 4:
            # Split window is available
            self.mem.mem[0x1] = 0x20
        else:
            # Color, Bold, Italic, Fixed is available
            self.mem.mem[0x1] = 0x1d
        # Default background color
        self.mem.mem[0x2c] = 2
        # Default foreground color
        self.mem.mem[0x2d] = 9
        self.plugin.set_default_bg(2)
        self.plugin.set_default_fg(9)
