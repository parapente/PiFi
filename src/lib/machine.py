# -*- coding: utf-8

from array import array
from io import BufferedReader
from typing import cast
from lib.container.container import Container
from lib.cpu import ZCpu
from lib.dictionary import ZDictionary
from lib.header import ZHeader
from lib.input import ZInput
from lib.memory import ZMemory
from lib.output import ZOutput
from plugins.plugskel import PluginSkeleton
from sys import exit
from threading import Lock

__author__ = "Theofilos Intzoglou"
__date__ = "$1 Ιουλ 2009 4:39:00 μμ$"


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
    container = Container()

    def attachPlugin(self, plugin: PluginSkeleton):
        self.plugin = plugin

    def boot(self):
        if self.header.version == 6:
            self.cpu.start6()
        self.cpu.start()
        self.handle_intr()

    def handle_intr(self):
        if self.cpu.intr == 1:  # Input interrupt to read a line of text
            if len(self.cpu.intr_data) > 2:
                self.input.read_line(
                    self.mem.mem[self.cpu.intr_data[0]],
                    self.get_text,
                    self.cpu.intr_data[2],
                    self.intr_line_routine,
                )
            else:
                self.input.read_line(
                    self.mem.mem[self.cpu.intr_data[0]],
                    self.get_text,
                    0,
                    self.intr_line_routine,
                )
        elif self.cpu.intr == 2:  # Input interrupt to read a character
            self.input.read_char(
                self.get_char, self.cpu.intr_data[0], self.intr_char_routine
            )
        elif self.cpu.intr == 3:  # Reset interrupt
            self.file.seek(0)
            self.output.clear_screen()
            self.load_story(self.file)
            self.boot()
        elif self.cpu.intr == 4:  # Tokenise interrupt
            self.lex(
                self.cpu.intr_data[0],
                self.cpu.intr_data[1],
                self.cpu.intr_data[2],
                self.cpu.intr_data[3],
            )
            self.cpu.intr = 0
            self.cpu.start()
            self.handle_intr()
        elif self.cpu.intr == 5:  # Save state interrupt
            self.plugin.print_string("Enter filename:")
            self.mutex.acquire()
            self.input.read_line(100, self.save_state, 0, None)
            # self.mutex.acquire() # We should wait here for the result of save_state
            # self.mutex.release()
            # self.cpu.intr = 0
            # self.cpu.start()
            # self.handle_intr()
        elif self.cpu.intr == 6:  # Load state interrupt
            self.plugin.print_string("Enter filename:")
            self.mutex.acquire()
            self.input.read_line(100, self.restore_state, 0, None)
        elif self.cpu.intr == 10:  # Return from routine, back to sread
            self.mutex.release()
            if self.cpu.last_return == 1:  # Routine returned true, we must bail out
                self.get_text("", True)
            else:  # Continue waiting for input
                self.input.read_line(
                    self.mem.mem[self.cpu.intr_data[0]],
                    self.get_text,
                    self.cpu.intr_data[2],
                    self.intr_line_routine,
                    False,
                )
        elif self.cpu.intr == 20:  # Return from routine, back to read_char
            self.mutex.release()
            if self.cpu.last_return == 1:  # Routine returned true, we must bail out
                self.cpu.intr = 2
                self.get_char(0)
            else:  # Continue waiting for input
                self.input.read_char(
                    self.get_char, self.cpu.intr_data[0], self.intr_char_routine
                )
        elif self.cpu.intr == 69:  # Quit
            self.input.read_char(self.get_char, 0, self.intr_char_routine)

    def intr_char_routine(self):
        self.mutex.acquire()
        self.plugin.debug_print("@@@@@@@@@@ start @@@@@@@@@@@@@@@@", 2)
        self.input.disconnect_input(self.get_char)
        self.cpu.intr = 0
        self.cpu._routine(self.cpu.intr_data[1], [], 0, -1, 20)
        self.cpu.start()
        self.plugin.debug_print("@@@@@@@@@@@ end @@@@@@@@@@@@@@@@@", 2)
        self.handle_intr()

    def intr_line_routine(self):
        self.mutex.acquire()
        self.plugin.debug_print("@@@@@@@@@@ start @@@@@@@@@@@@@@@@", 2)
        self.input.disconnect_input(self.get_text)
        self.cpu.intr = 0
        self.cpu._routine(self.cpu.intr_data[3], [], 0, -1, 10)
        self.cpu.start()
        self.plugin.debug_print("@@@@@@@@@@@ end @@@@@@@@@@@@@@@@@", 2)
        self.handle_intr()

    def get_text(self, text: str, interrupted: bool = False):
        self.input.stop_line_timer()
        self.input.disconnect_input(self.get_text)
        self.mutex.acquire()
        # self.input.hide_cursor()
        # print('get_text:', text, interrupted)
        if not interrupted:  # We got here because user pressed enter
            self.plugin.debug_print("Enter!", 2)
            paddr = self.cpu.intr_data[1]
            taddr = self.cpu.intr_data[0]
            self.plugin.debug_print("gt -> '" + text + "'", 2)
            if self.zver < 5:
                i = 0
                for i in range(len(text)):
                    if (i == (len(text) - 1)) and text[i] == "\n":
                        self.mem.mem[taddr + 1 + i] = 0
                    else:
                        self.mem.mem[taddr + 1 + i] = ord(str(text[i]))
                i += 1
                self.mem.mem[taddr + 1 + i] = 0
                self.lex(taddr, paddr, 0, 0)
            else:
                if taddr != 0:
                    skip = self.mem.mem[taddr + 1]
                    for i in range(len(text)):
                        self.mem.mem[taddr + 2 + i + skip] = ord(str(text[i]))
                    self.mem.mem[taddr + 1] = len(text) + skip
                    self.lex(taddr, paddr, 0, 0)
                    if self.zver > 4:
                        self.cpu.got_char(10)
        else:
            # print 'input was interrupted'
            if self.zver > 4:
                self.cpu.got_char(0)
        self.cpu.intr = 0
        self.mutex.release()
        self.cpu.start()
        self.handle_intr()

    def lex(self, text: int, parse: int, dictionary: int, flag: int):
        if dictionary != 0 or flag != 0:
            exit("LEX: Not supported yet!")
        txt = ""
        if self.zver < 5:
            i = 0
            while self.mem.mem[text + 1 + i] != 0:
                txt += chr(self.mem.mem[text + 1 + i])
                i += 1
        else:
            for i in range(self.mem.mem[text + 1]):
                txt += chr(self.mem.mem[text + 2 + i])
        l = len(txt)
        self.plugin.debug_print("txt='" + txt + "' Len:" + str(l), 2)
        words = []
        w = ""
        i = 0
        while i < l:
            while (i < l) and (
                (txt[i] not in self.dict.separators) and (txt[i] != " ")
            ):
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
            if len(words[i]) > (self.dict.word_length * 3 // 2):
                for j in range(self.dict.word_length * 3 // 2):
                    w1 += words[i][j]
            else:
                w1 = words[i]
            self.plugin.debug_print(w1 + "- len -" + str(len(w1)), 2)
            if self.cpu.intr_data[1] != 0:  # No parsing is required
                # Find the data for the record
                addr = self.dict.find_word(w1)
                l = len(words[i])
                pos = words[i + 1]
                self.plugin.debug_print(
                    "word:" + w1 + "Addr:" + str(addr) + "Pos:" + str(pos), 2
                )
                # Write the record in parse buffer
                self.mem.mem[parse] = addr >> 8
                self.mem.mem[parse + 1] = addr & 0xFF
                self.mem.mem[parse + 2] = l
                self.mem.mem[parse + 3] = pos
                parse += 4
            i += 2

    def get_char(self, char: int):
        self.input.stop_char_timer()
        self.input.disconnect_input(self.get_char)
        self.mutex.acquire()
        self.plugin.debug_print("Character read!", 2)
        if self.cpu.intr == 2:
            self.cpu.got_char(char)
            self.cpu.intr = 0
            self.mutex.release()
            self.cpu.start()
            self.handle_intr()
        else:
            self.plugin.quit()
            # exit('Quit')

    def save_state(self, filename: str):
        print("Here!")
        # Test if file already exists
        try:
            self.savefile = open(filename)
            # File exists! Ask if user wants to overwrite file.
            self.plugin.print_string("Overwrite?(Y/N)")
            self.input.read_char(self.overwrite_yn)
        except IOError:
            # File doesn't exist
            try:
                self.savefile = open(filename, "wb")
                self.do_save_state()
            except IOError as cannot_save_file:
                (errno, strerror) = cannot_save_file.args
                print("I/O error ({0}): {1}".format(errno, strerror))
                self.plugin.print_string("Save failed!\n")
                self.mutex.release()
                self.save_state_return_fail()

    def restore_state(self, filename: str):
        print("Here!")
        # Test if file already exists
        try:
            self.savefile = open(filename, "rb")
            # Save header bits to be used after restore
            bits = self.header.header[0x10] & 3
            self.do_restore_state()
            self.header.header[0x10] = self.header.header[0x10] | bits
        except IOError as cannot_restore_file:
            (errno, strerror) = cannot_restore_file.args
            print("I/O error ({0}): {1}".format(errno, strerror))
            self.plugin.print_string("Restore failed!\n")
            self.mutex.release()
            self.restore_state_return_fail()

    def overwrite_yn(self, key: str):
        if key == "y" or key == "Y":
            fname = self.savefile.name
            self.savefile.close()
            try:
                self.savefile = open(fname, "wb")
                self.do_save_state()
            except IOError as cannot_save_file:
                (errno, strerror) = cannot_save_file.args
                print("I/O error ({0}): {1}".format(errno, strerror))
                self.plugin.print_string("Save failed!\n")
                self.mutex.release()
                self.save_state_return_fail()
        elif key == "n" or key == "N":
            self.save_state_return_fail()
        else:
            self.input.read_char(self.overwrite_yn)

    def do_restore_state(self):
        # Read at most 1MB of savefile (can it be larger than that?)
        filebuf = list(self.savefile.read(1024 * 1024))
        if (
            "".join([chr(x) for x in filebuf[:4]]) == "FORM"
            and "".join([chr(x) for x in filebuf[8:12]]) == "IFZS"
        ):
            self.plugin.debug_print("File looks like a savefile.", 1)
        savesize = (
            (filebuf[4] << 24) + (filebuf[5] << 16) + (filebuf[6] << 8) + filebuf[7] + 8
        )
        self.plugin.debug_print("Filesize: " + str(savesize), 1)
        self.plugin.debug_print("filebuf size: " + str(len(filebuf)), 1)

        pos = 12
        self.file.seek(0)
        gamefilebuf = list(self.file.read(self.mem.static_beg))
        while pos < savesize:
            nextID = "".join([chr(x) for x in filebuf[pos : pos + 4]])
            self.plugin.debug_print("Found chunk ID: " + nextID, 1)
            pos += 4
            if nextID == "CMem":
                chunk_length = (
                    (filebuf[pos] << 24)
                    + (filebuf[pos + 1] << 16)
                    + (filebuf[pos + 2] << 8)
                    + filebuf[pos + 3]
                )
                pos += 4
                fbpos = 0
                mempos = 0
                while fbpos < chunk_length:
                    if filebuf[pos + fbpos] != 0:
                        self.mem.mem[mempos] = filebuf[pos + fbpos]
                        fbpos += 1
                        mempos += 1
                    else:
                        fbpos += 1
                        zerocount = filebuf[pos + fbpos]
                        fbpos += 1
                        for x in gamefilebuf[mempos : mempos + zerocount]:
                            self.mem.mem[mempos] = x
                            mempos += 1
                if mempos < self.mem.static_beg:
                    for x in gamefilebuf[mempos : self.mem.static_beg]:
                        self.mem.mem[mempos] = x
                        mempos += 1
                elif mempos > self.mem.static_beg:
                    self.plugin.print_string(
                        "Savefile overwrites part of static memory. Halting..."
                    )
                    exit("Static memory overwritten!")
                if (chunk_length % 2) == 1:
                    pos += chunk_length + 1
                else:
                    pos += chunk_length
            elif nextID == "UMem":
                chunk_length = (
                    (filebuf[pos] << 24)
                    + (filebuf[pos + 1] << 16)
                    + (filebuf[pos + 2] << 8)
                    + filebuf[pos + 3]
                )
                pos += 4
                if (
                    chunk_length < self.mem.static_beg
                    or chunk_length > self.mem.static_beg
                ):
                    self.plugin.print_string(
                        "Saved UMem size not matching dynamic memory. Restore failed"
                    )
                    return
                i = 0
                for x in filebuf[pos : pos + chunk_length]:
                    self.mem.mem[i] = x
                if (chunk_length % 2) == 1:
                    pos += chunk_length + 1
                else:
                    pos += chunk_length
            elif nextID == "Stks":
                chunk_length = (
                    (filebuf[pos] << 24)
                    + (filebuf[pos + 1] << 16)
                    + (filebuf[pos + 2] << 8)
                    + filebuf[pos + 3]
                )
                pos += 4
                chunk_pos = pos
                while chunk_pos < (pos + chunk_length):
                    ret_pc = (
                        (filebuf[chunk_pos] << 16)
                        + (filebuf[chunk_pos + 1] << 8)
                        + filebuf[chunk_pos + 2]
                    )
                    chunk_pos += 3
                    p_flag = filebuf[chunk_pos] & 16
                    num_locals = filebuf[chunk_pos] & 15
                    var_num_to_store_result = filebuf[chunk_pos + 1]
                    arguments_supplied = filebuf[chunk_pos + 2] & 127
                    chunk_pos += 3
                    eval_stack_size = (filebuf[chunk_pos] << 8) + filebuf[chunk_pos + 1]
                    chunk_pos += 2
                    for i in range(num_locals):
                        # TODO: read locals
                        chunk_pos += 2
                    for i in range(eval_stack_size):
                        # TODO: read stack
                        chunk_pos += 2
                if (chunk_length % 2) == 1:
                    pos += chunk_length + 1
                else:
                    pos += chunk_length
            elif nextID == "IntD":
                chunk_length = (
                    (filebuf[pos] << 24)
                    + (filebuf[pos + 1] << 16)
                    + (filebuf[pos + 2] << 8)
                    + filebuf[pos + 3]
                )
                pos += 4
                # Ignore for now
                if (chunk_length % 2) == 1:
                    pos += chunk_length + 1
                else:
                    pos += chunk_length
            elif nextID == "IFhd":
                chunk_length = (
                    (filebuf[pos] << 24)
                    + (filebuf[pos + 1] << 16)
                    + (filebuf[pos + 2] << 8)
                    + filebuf[pos + 3]
                )
                pos += 4
                self.plugin.debug_print("Chunk len: " + str(chunk_length), 1)
                if chunk_length != 13:
                    self.plugin.print_string("Wrong size of chunk. Not restoring\n")
                    return

                release_number = (filebuf[pos] << 8) + filebuf[pos + 1]
                if release_number != self.header.release_number:
                    self.plugin.debug_print(
                        str(release_number) + " - " + str(self.header.release_number),
                        1,
                    )
                    self.plugin.print_string("Different release number. Not restoring")
                    return

                serial_num = "".join([chr(x) for x in filebuf[pos + 2 : pos + 8]])
                if serial_num != self.header.serial_number:
                    self.plugin.debug_print(
                        serial_num + " - " + self.header.serial_number, 1
                    )
                    self.plugin.print_string("Different serial number. Not restoring")
                    return

                checksum = (filebuf[pos + 8] << 8) + filebuf[pos + 9]
                if checksum != self.header.checksum:
                    # TODO: If header checksum is zero we should cacl checksum
                    self.plugin.debug_print(
                        str(checksum) + " - " + str(self.header.checksum), 1
                    )
                    self.plugin.print_string("Different checksum. Not restoring")
                    return

                self.plugin.debug_print("Savefile is for this game. Continue...", 1)
                if (chunk_length % 2) == 1:
                    pos += chunk_length + 1
                else:
                    pos += chunk_length
                self.plugin.debug_print(str(filebuf[pos]), 1)
            elif nextID == "AUTH":
                chunk_length = (
                    (filebuf[pos] << 24)
                    + (filebuf[pos + 1] << 16)
                    + (filebuf[pos + 2] << 8)
                    + filebuf[pos + 3]
                )
                # Ignore for now
                pos += 4
                if (chunk_length % 2) == 1:
                    pos += chunk_length + 1
                else:
                    pos += chunk_length
            elif nextID == "(c) ":
                chunk_length = (
                    (filebuf[pos] << 24)
                    + (filebuf[pos + 1] << 16)
                    + (filebuf[pos + 2] << 8)
                    + filebuf[pos + 3]
                )
                # Ignore for now
                pos += 4
                if (chunk_length % 2) == 1:
                    pos += chunk_length + 1
                else:
                    pos += chunk_length
            elif nextID == "ANNO":
                chunk_length = (
                    (filebuf[pos] << 24)
                    + (filebuf[pos + 1] << 16)
                    + (filebuf[pos + 2] << 8)
                    + filebuf[pos + 3]
                )
                # Ignore for now
                pos += 4
                if (chunk_length % 2) == 1:
                    pos += chunk_length + 1
                else:
                    pos += chunk_length
        # exit("Exit")

        # FIX: You should restart to the point where the save was created
        # The following are unnecessary
        if self.zver >= 4:
            self.cpu._zstore(1, self.cpu.pc)
            self.cpu.pc += 1
            self.cpu.start()
            self.handle_intr()
        else:
            self.cpu.branch(False)
            self.cpu.start()
            self.handle_intr()

    def do_save_state(self):
        self.savefile.write("FORM\x00\x00\x00\x00IFZS".encode())
        savefile_size = 4

        membuff = self.mem.mem[: self.mem.static_beg]
        print(membuff)
        self.file.seek(0)
        filebuff = list(self.file.read(self.mem.static_beg))
        print(filebuff)

        # Save Story File info ('IFhd') - MUST be first
        self.savefile.write("IFhd\x00\x00\x00\x0d".encode())
        ifhd = []
        ifhd += [membuff[2], membuff[3]]
        for i in range(6):
            ifhd += [membuff[18 + i]]
        # TODO: Checksum must be calculated if not available
        ifhd += [membuff[0x1C], membuff[0x1D]]
        ifhd += [
            (self.cpu.pc >> 16) & 255,
            (self.cpu.pc >> 8) & 255,
            self.cpu.pc & 255,
            0,
        ]
        tmp = array("B")
        tmp.fromlist(ifhd)
        self.savefile.write(tmp)
        savefile_size += 22

        # Save dynamic memory ('CMem')
        diffbuff = [0] * self.mem.static_beg
        for i in range(self.mem.static_beg):
            diffbuff[i] = membuff[i] ^ filebuff[i]
        rlebuff = []
        self.rle_encode(diffbuff, rlebuff)
        self.savefile.write("CMem".encode())
        tmp = array("B")
        tmpsize = len(rlebuff)
        sizebyte4 = tmpsize & 255
        sizebyte3 = (tmpsize >> 8) & 255
        sizebyte2 = (tmpsize >> 16) & 255
        sizebyte1 = 0
        tmp.fromlist([sizebyte1, sizebyte2, sizebyte3, sizebyte4] + rlebuff)
        self.savefile.write(tmp)
        if (tmpsize % 2) == 1:
            self.savefile.write("\x00".encode())
            savefile_size += 8 + len(rlebuff) + 1
        else:
            savefile_size += 8 + len(rlebuff)

        # Save stack ('Stks')
        self.savefile.write("Stks".encode())

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
            localvars = stack.frames[i * 4]
            evalstack = stack.frames[i * 4 + 1]
            if i == 0:  # Fix: In v6 this shouldn't be all zeroes
                pc, res, intr_on_return, intr_data = [0, 0, 0, 0]
                lenargv = 0
            else:
                pc, res, intr_on_return, intr_data = stack.frames[(i - 1) * 4 + 2]
                lenargv = stack.frames[(i - 1) * 4 + 3]

            # Prepare the data
            pcbyte3 = pc & 255
            pcbyte2 = (pc >> 8) & 255
            pcbyte1 = (pc >> 16) & 255
            stks += [pcbyte1, pcbyte2, pcbyte3]
            stks_size += 3

            flags = len(localvars)
            if res == -1:
                flags |= 16
            stks += [flags]
            if res != -1:
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

            print("Local vars:", len(localvars))
            for j in range(len(localvars)):
                print(f"var{j}:", localvars[j])
                stks += [(localvars[j] >> 8) & 255, localvars[j] & 255]
                stks_size += 2
            print("Evalstack:", len(evalstack))
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

        tmp = array("B")
        tmp.fromlist(stks)
        savefile_size += len(stks)
        self.savefile.write(tmp)

        # Complete the FORM chunk with the data length
        self.savefile.seek(4)
        tmp = array("B")
        tmp.fromlist(
            [
                (savefile_size >> 24) & 255,
                (savefile_size >> 16) & 255,
                (savefile_size >> 8) & 255,
                savefile_size & 255,
            ]
        )
        self.savefile.write(tmp)

        self.savefile.close()

        # Drop temporary frames. Not needed any more
        self.cpu.stack.pop_frame()
        self.cpu.stack.pop_frame()
        self.cpu.stack.pop_frame()
        self.cpu.stack.pop_frame()

        if self.zver >= 4:
            self.cpu._zstore(1, self.cpu.pc)
            self.cpu.pc += 1
            self.cpu.start()
            self.handle_intr()
        else:
            self.cpu.branch(True)
            self.cpu.start()
            self.handle_intr()

    def save_state_return_fail(self):
        if self.zver >= 5:
            self.cpu._zstore(0, self.cpu.pc)
            self.cpu.pc += 1
            self.cpu.start()
        else:
            self.cpu.branch(False)
            self.cpu.start()

    def restore_state_return_fail(self):
        self.cpu.intr = 0
        if self.zver >= 5:
            self.cpu._zstore(0, self.cpu.pc)
            self.cpu.pc += 1
            self.cpu.start()
        else:
            self.cpu.branch(False)
            self.cpu.start()

    def rle_encode(self, buffer: list, rle: list):
        bufferlen = len(buffer)
        i = 0
        seqzeros = 0
        lastbyte = -1
        while i < bufferlen:
            if buffer[i] == 0:
                if lastbyte != 0:
                    rle.append(buffer[i])
                    lastbyte = 0
                    seqzeros = 1
                else:
                    seqzeros += 1
            else:
                if lastbyte == 0:
                    seqzeros -= 1
                    remain = seqzeros % 256
                    times = seqzeros // 256
                    if times == 0:
                        rle.append(remain)
                    else:
                        while times > 0:
                            rle.append(255)
                            if times != 1 or (times == 1 and remain != 0):
                                rle.append(0)
                            times -= 1
                        if remain != 0:
                            rle.append(remain)
                rle.append(buffer[i])
                lastbyte = buffer[i]
            i += 1
        if lastbyte == 0:
            rle.pop()

    def load_story(self, story_file: BufferedReader):
        # @type story_file file
        # Read the first byte of the file to determine the version of the story
        self.file = story_file
        version_byte = story_file.read(1)
        if len(version_byte):
            b = ord(version_byte)
            if b < 4:
                max_length = 128 * 1024
            elif b < 6:
                max_length = 256 * 1024
            elif b == 6 or b == 7 or b == 8:
                max_length = 512 * 1024
            else:
                print("Not a valid story file")
                exit(10)
        else:
            print("Empty file or otherwise inaccessible file")
            exit(10)

        # Now that we checked the file size we rewind the file and read the data into memory
        story_file.seek(0)
        self.mem = cast(ZMemory, self.container.resolve("ZMemory"))
        self.mem.initialize(story_file, max_length)
        self.header = cast(ZHeader, self.container.resolve("ZHeader"))
        self.header.print_all(self.plugin)
        self.input = cast(ZInput, self.container.resolve("ZInput", self.plugin))
        self.zver = self.header.version
        self.output = cast(
            ZOutput, self.container.resolve("ZOutput", self.zver, self.plugin)
        )
        self.cpu = cast(ZCpu, self.container.resolve("ZCpu", self.output, self.plugin))
        self.cpu.file = story_file
        self.dict = cast(ZDictionary, self.container.resolve("ZDictionary"))
        self.plugin.debug_print("Version of story file: {0}".format(self.zver), 1)
        self.plugin.debug_print(
            "Length of file: {0}".format(self.header.length_of_file), 1
        )
        self.plugin.debug_print(
            "Static memory begins at: {0}".format(self.mem.static_beg), 1
        )

    def init(self):
        # Set the default options
        header = cast(ZHeader, self.container.resolve("ZHeader"))
        if self.zver > 3:
            # Interpreter number and version
            header.interpreter_number = 1
            header.interpreter_version = 0x41  # revision A
            # Width and height of window
            self.plugin.update_screen_size()

            header.status_line_unavailable = False
            header.variable_pitch_font_as_default = True

        # Standard revision number
        header.standard_revision_number = 1

        if self.zver > 4:
            # Font width in units
            header.font_width = 1
            # Font height in units
            header.font_height = 1

        # Default supported options
        if self.zver < 4:
            # Split window is available
            header.screen_splitting_available = True
        else:
            # Color, Bold, Italic, Fixed is available
            header.colours_available = True
            header.boldface_available = True
            header.italic_available = True
            header.fixed_space_font_available = True
            # So is timed input
            header.timed_input_available = True
            # Pictures and sound effects are not available yet (v6)
            header.picture_displaying_available = False
            header.sound_effects_available = False

        if self.zver > 4:
            # Default background color
            header.default_background_colour = 2
            # Default foreground color
            header.default_foreground_colour = 9
        self.plugin.set_default_bg(2)
        self.plugin.set_default_fg(9)

        header.transcripting_is_on = False
