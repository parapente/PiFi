# -*- coding: utf-8

from .memory import ZMemory
from .cpu import ZCpu
from .header import ZHeader
from .input import ZInput
from .output import ZOutput
from .ztext import *
from .dictionary import ZDictionary
import sys
from threading import Lock

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
    mutex = Lock()

    def __init__(self,w):
        self.plugin = w

    def boot(self):
        if self.header.version == 6:
            self.cpu.start6()
        self.cpu.start()
        self.handle_intr()

    def handle_intr(self):
        if self.cpu.intr == 1: # Input interrupt to read a line of text
            if (len(self.cpu.intr_data)>2):
                self.input.read_line(self.mem.mem[self.cpu.intr_data[0]], self.get_text, self.cpu.intr_data[2], self.intr_line_routine)
            else:
                self.input.read_line(self.mem.mem[self.cpu.intr_data[0]], self.get_text, 0, self.intr_line_routine)
        elif self.cpu.intr == 2: # Input interrupt to read a character
            self.input.read_char(self.get_char, self.cpu.intr_data[0], self.intr_char_routine)
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
        elif self.cpu.intr == 5: # Save state interrupt
            self.plugin.prints('Enter filename:')
            self.mutex.acquire()
            self.input.read_line(100, self.save_state, 0, None)
            #self.mutex.acquire() # We should wait here for the result of save_state
            #self.mutex.release()
            #self.cpu.intr = 0
            #self.cpu.start()
            #self.handle_intr()
        elif self.cpu.intr == 6: # Load state interrupt
            pass
        elif self.cpu.intr == 10: # Return from routine, back to sread
            self.mutex.release()
            if (self.cpu.last_return == 1): # Routine returned true, we must bail out
                self.get_text('',True)
            else: # Continue waiting for input
                self.input.read_line(self.mem.mem[self.cpu.intr_data[0]], self.get_text, self.cpu.intr_data[2], self.intr_line_routine, False)
        elif self.cpu.intr == 20: # Return from routine, back to read_char
            self.mutex.release()
            if (self.cpu.last_return == 1): # Routine returned true, we must bail out
                self.cpu.intr = 2
                self.get_char(0)
            else: # Continue waiting for input
                self.input.read_char(self.get_char, self.cpu.intr_data[0], self.intr_char_routine)
        elif self.cpu.intr == 69: # Quit
            self.input.read_char(self.get_char, 0, self.intr_char_routine)

    def intr_char_routine(self):
        self.mutex.acquire()
        self.plugin.debugprint("@@@@@@@@@@ start @@@@@@@@@@@@@@@@", 2)
        self.input.disconnect_input(self.get_char)
        self.cpu.intr = 0
        self.cpu._routine(self.cpu.intr_data[1],[],0,-1,20)
        self.cpu.start()
        self.plugin.debugprint("@@@@@@@@@@@ end @@@@@@@@@@@@@@@@@", 2)
        self.handle_intr()

    def intr_line_routine(self):
        self.mutex.acquire()
        self.plugin.debugprint("@@@@@@@@@@ start @@@@@@@@@@@@@@@@", 2)
        self.input.disconnect_input(self.get_text)
        self.cpu.intr = 0
        self.cpu._routine(self.cpu.intr_data[3],[],0,-1,10)
        self.cpu.start()
        self.plugin.debugprint("@@@@@@@@@@@ end @@@@@@@@@@@@@@@@@", 2)
        self.handle_intr()

    def get_text(self,text,interrupted=False):
        self.input.stop_line_timer()
        self.input.disconnect_input(self.get_text)
        self.mutex.acquire()
        #self.input.hide_cursor()
        #print('get_text:', text, interrupted)
        if (interrupted == False): # We got here because user pressed enter
            self.plugin.debugprint("Enter!", 2)
            paddr = self.cpu.intr_data[1]
            taddr = self.cpu.intr_data[0]
            self.plugin.debugprint("gt -> '"+text+"'", 2)
            if self.zver < 5:
                i = 0
                for i in range(len(text)):
                    if (i == (len(text) - 1)) and text[i] == '\n':
                        self.mem.mem[taddr + 1 + i] = 0
                    else:
                        self.mem.mem[taddr + 1 + i] = ord(str(text[i]))
                i += 1
                self.mem.mem[taddr + 1 + i] = 0
                self.lex(taddr,paddr,0,0)
            else:
                if taddr != 0:
                    skip = self.mem.mem[taddr + 1]
                    for i in range(len(text)):
                        self.mem.mem[taddr + 2 + i + skip] = ord(str(text[i]))
                    self.mem.mem[taddr + 1] = len(text) + skip
                    self.lex(taddr,paddr,0,0)
                    if self.zver > 4:
                        self.cpu.got_char(10)
        else:
            #print 'input was interrupted'
            if self.zver > 4:
                self.cpu.got_char(0)
        self.cpu.intr = 0
        self.mutex.release()
        self.cpu.start()
        self.handle_intr()

    def lex(self,text,parse,dictionary,flag):
        if dictionary != 0 or flag != 0:
            sys.exit("LEX: Not supported yet!")
        txt = ""
        if self.zver < 5:
            i = 0
            while self.mem.mem[text + 1 + i ] != 0:
                txt += chr(self.mem.mem[text + 1 + i])
                i += 1
        else:
            for i in range(self.mem.mem[text + 1]):
                txt += chr(self.mem.mem[text + 2 + i])
        l = len(txt)
        self.plugin.debugprint("txt='"+txt+"' Len:"+str(l), 2)
        words = []
        w = ""
        i = 0
        while (i < l):
            while (i < l) and ((txt[i] not in self.dict.separators) and (txt[i] != " ")):
                w += txt[i]
                i += 1
            if (w != "") and (w != " "):
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
            self.plugin.debugprint(w1+"- len -"+str(len(w1)), 2)
            if self.cpu.intr_data[1] != 0: # No parsing is required
                # Find the data for the record
                addr = self.dict.find_word(w1)
                l = len(words[i])
                pos = words[i + 1]
                self.plugin.debugprint("word:"+w1+"Addr:"+str(addr)+"Pos:"+str(pos), 2)
                # Write the record in parse buffer
                self.mem.mem[parse] = addr >> 8
                self.mem.mem[parse + 1] = addr & 0xff
                self.mem.mem[parse + 2] = l
                self.mem.mem[parse + 3] = pos
                parse += 4
            i += 2

    def get_char(self,char):
        self.input.stop_char_timer()
        self.input.disconnect_input(self.get_char)
        self.mutex.acquire()
        self.plugin.debugprint("Character read!", 2)
        if (self.cpu.intr == 2):
            self.cpu.got_char(char)
            self.cpu.intr = 0
            self.mutex.release()
            self.cpu.start()
            self.handle_intr()
        else:
            self.plugin.quit()
            #sys.exit('Quit')

    def save_state(self, filename):
        print("Here!")
        # Test if file already exists
        try:
            self.savefile = open(filename)
            # File exists! Ask if user wants to overwrite file.
            self.plugin.prints('Overwrite?(Y/N)')
            self.input.read_char(self.overwrite_yn)
        except IOError:
            # File doesn't exist
            try:
                self.savefile = open(filename,'wb')
                self.do_save_state()
            except IOError as cannot_save_file:
                (errno,strerror) = cannot_save_file.args
                print("I/O error ({0}): {1}".format(errno,strerror))
                self.plugin.prints('Save failed!\n')
                self.mutex.release()
                self.save_state_return_fail()

    def overwrite_yn(self,key):
        if key == 'y' or key == 'Y':
            self.do_save_state()
        elif key == 'n' or key == 'N':
            self.save_state_return_fail()
        else:
            self.input.read_char(self.overwrite_yn)

    def do_save_state(self):
        self.savefile.write('FORM\x00\x00\x00\x00IFZS')
        savefile_size = 4

        membuff = self.mem.mem[:self.mem.static_beg]
        print(membuff)
        self.file.seek(0)
        filebuff = list(self.file.read(self.mem.static_beg))
        print(filebuff)

        #Save Story File info ('IFhd') - MUST be first
        self.savefile.write('IFhd\x00\x00\x00\x0d')
        ifhd = []
        ifhd += [membuff[2], membuff[3]]
        for i in range(6):
            ifhd += [membuff[18+i]]
        ifhd += [membuff[0x1c], membuff[0x1d]]
        ifhd += [(self.cpu.pc >> 16) & 255, (self.cpu.pc >> 8) & 255, self.cpu.pc & 255, 0]
        tmp = array('B')
        tmp.fromlist(ifhd)
        self.savefile.write(tmp)
        savefile_size += 22

        # Save dynamic memory ('CMem')
        diffbuff = [0] * self.mem.static_beg
        for i in range(self.mem.static_beg):
            if (membuff[i] == ord(filebuff[i])):
                diffbuff[i] = 0
            else:
                diffbuff[i] = membuff[i]
        rlebuff = []
        self.rle_encode(diffbuff, rlebuff)
        self.savefile.write('CMem')
        tmp = array('B')
        tmpsize = len(rlebuff)
        sizebyte4 = tmpsize & 255
        sizebyte3 = (tmpsize >> 8) & 255
        sizebyte2 = (tmpsize >> 16) & 255
        sizebyte1 = 0
        tmp.fromlist([sizebyte1, sizebyte2, sizebyte3, sizebyte4]+rlebuff)
        self.savefile.write(tmp)
        if ((tmpsize % 2) == 1):
            self.savefile.write('\x00');
            savefile_size += 8 + len(rlebuff) + 1
        else:
            savefile_size += 8 + len(rlebuff)

        # Save stack ('Stks')
        self.savefile.write('Stks')

        # To get a complete stack dump we need to push local data to stack
        self.cpu.stack.push_local_vars()
        self.cpu.stack.push_eval_stack()
        self.cpu.stack.push_frame(0)
        self.cpu.stack.push_frame(0)

        savefile_size += 4
        stks_size = 0
        stks = [0, 0, 0, 0]
        stack = self.cpu.stack
        frames = stack.framespos // 4
        for i in range(frames):
            # Get necessary data from stack
            localvars = stack.frames[i*4]
            evalstack = stack.frames[i*4+1]
            if (i == 0): # Fix: In v6 this shouldn't be all zeroes
                pc, res, intr_on_return, intr_data = [0, 0, 0, 0]
                lenargv = 0
            else:
                pc, res, intr_on_return, intr_data = stack.frames[(i-1)*4+2]
                lenargv = stack.frames[(i-1)*4+3]

            # Prepare the data
            pcbyte3 = pc & 255
            pcbyte2 = (pc >> 8) & 255
            pcbyte1 = (pc >> 16) & 255
            stks += [pcbyte1, pcbyte2, pcbyte3]
            stks_size += 3

            flags = len(localvars)
            if (res == -1):
                flags |= 16
            stks += [flags]
            if (res != -1):
                stks += [res]
            else:
                stks += [0]
            args = 0
            for j in range(lenargv):
                args = args << 1
                args += 1
            stks += [args]
            stks_size += 3
            evalstacklen = len(evalstack)
            stks += [(evalstacklen >> 8) & 255, evalstacklen & 255]
            stks_size += 2

            print('Local vars:',len(localvars))
            for j in range(len(localvars)):
                stks += [(localvars[j] >> 8) & 255, localvars[j] & 255]
                stks_size += 2
            print('Evalstack:',len(evalstack))
            for j in range(len(evalstack)):
                stks += [(evalstack[j] >> 8) & 255, evalstack[j] & 255]
                stks_size += 2

            stkslenbyte4 = stks_size & 255
            stkslenbyte3 = (stks_size >> 8) & 255
            stkslenbyte2 = (stks_size >> 16) & 255
            stkslenbyte1 = (stks_size >> 24) & 255
            stks[0] = stkslenbyte1
            stks[1] = stkslenbyte2
            stks[2] = stkslenbyte3
            stks[3] = stkslenbyte4

        tmp = array('B')
        tmp.fromlist(stks)
        savefile_size += len(stks)
        self.savefile.write(tmp)

        #Complete the FORM chunk with the data length
        self.savefile.seek(4)
        tmp = array('B')
        tmp.fromlist([(savefile_size >> 24) & 255, (savefile_size >> 16) & 255, (savefile_size >> 8) & 255, savefile_size & 255])
        self.savefile.write(tmp)

        self.savefile.close()

        # Drop temporary frames. Not needed any more
        self.cpu.stack.pop_frame()
        self.cpu.stack.pop_frame()
        self.cpu.stack.pop_frame()
        self.cpu.stack.pop_frame()

        if (self.zver >= 4):
            self.cpu._zstore(1,self.cpu.pc)
            self.cpu.pc += 1
            self.cpu.start()
            self.handle_intr()
        else:
            self.cpu.branch(True)
            self.cpu.start()
            self.handle_intr()

    def save_state_return_fail(self):
        if (self.zver >= 5):
            self.cpu._zstore(0,self.cpu.pc)
            self.cpu.pc += 1
            self.cpu.start()
        else:
            self.cpu.branch(False)
            self.cpu.start()

    def rle_encode(self, buffer, rle):
        bufferlen = len(buffer)
        i = 0
        seqzeros = 0
        lastbyte = -1
        while (i<bufferlen):
            if (buffer[i] == 0):
                if (lastbyte != 0):
                    rle.append(buffer[i])
                    lastbyte = 0
                    seqzeros = 1
                else:
                    seqzeros += 1
            else:
                if (lastbyte == 0):
                    seqzeros -= 1
                    remain = seqzeros % 256
                    times = seqzeros // 256
                    if (times == 0):
                        rle.append(remain)
                    else:
                        while (times>0):
                            rle.append(255)
                            if (times != 1 or (times == 1 and remain != 0)):
                                rle.append(0)
                            times -= 1
                        if (remain!=0):
                            rle.append(remain)
                rle.append(buffer[i])
                lastbyte = buffer[i]
            i += 1
        if (lastbyte == 0):
            rle.pop()


    def load_story(self,f):
        # @type f file
        # Read the first byte of the file to determine the version of the story
        self.file = f
        b = ord(f.read(1))
        if (b < 4):
            max_length = 128 * 1024
        elif (b < 6):
            max_length = 256 * 1024
        elif (b == 6 or b == 7 or b == 8):
            max_length = 512 * 1024
        else:
            print('Not a valid story file')
            sys.exit(10)

        # Now that we checked the file size we rewind the file and read the data into memory
        f.seek(0)
        self.mem = ZMemory(f,max_length)
        self.header = ZHeader(self.mem.mem)
        self.header.print_all(self.plugin)
        self.input = ZInput(self.plugin)
        self.zver = self.header.version
        self.output = ZOutput(self.zver, self.mem.mem, self.plugin)
        self.cpu = ZCpu(self.mem.mem,self.header,self.output,self.plugin)
        self.cpu.file = f
        self.dict = ZDictionary(self.mem.mem, self.header)
        self.plugin.debugprint('Version of story file: {0}'.format(self.zver), 1)
        self.plugin.debugprint('Length of file: {0}'.format(self.header.length_of_file), 1)
        self.plugin.debugprint('Static memory begins at: {0}'.format(self.mem.static_beg), 1)

    def init(self):
        # Set the default options
        if self.zver > 3:
            # Interpreter number and version
            self.mem.mem[0x1e] = 1
            self.mem.mem[0x1f] = 0x41 # revision A
            # Width and height of window
            self.plugin.update_screen_size()

        # Standard revision number
        self.mem.mem[0x32] = 1

        if self.zver > 4:
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
            self.mem.mem[0x1] = 0x9d

        if self.zver > 4:
            # Default background color
            self.mem.mem[0x2c] = 2
            # Default foreground color
            self.mem.mem[0x2d] = 9
        self.plugin.set_default_bg(2)
        self.plugin.set_default_fg(9)

