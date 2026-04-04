from lib.ztext import decode_text


class ZCpu0OpHandlers:
    def _rtrue(self):
        pc = self.pc
        self._return(1)
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: rtrue", 2)

    def _rfalse(self):
        pc = self.pc
        self._return(0)
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: rfalse", 2)

    def _print(self):
        pc = self.pc
        uaddr = self.pc + 1
        try:
            i, text = self.print_dict[uaddr]
        except KeyError:
            buf = []
            eot = False
            i = 0
            while not eot:
                if (self.mem[uaddr + i] & 128) == 128:
                    eot = True
                buf.append(self.mem[uaddr + i])
                buf.append(self.mem[uaddr + i + 1])
                i += 2
            text = decode_text(buf)
            self.print_dict[uaddr] = [i, text]
        self.pc += i + 1
        self.output.print_string(text, [])
        if self.plugin.level >= 2:
            self.plugin.debug_print(f'{format(pc, "X")}: print "{text}"', 2)

    def _print_ret(self):
        pc = self.pc
        uaddr = self.pc + 1
        buf = []
        eot = False
        i = 0
        while not eot:
            if (self.mem[uaddr + i] & 128) == 128:
                eot = True
            buf.append(self.mem[uaddr + i])
            buf.append(self.mem[uaddr + i + 1])
            i += 2
        text = decode_text(buf)
        self.output.print_string(text + "\n", [])
        self.pc += i + 1
        self._return(1)
        if self.plugin.level >= 2:
            self.plugin.debug_print(f'{format(pc, "X")}: print_ret "{text}"', 2)

    def _nop(self):
        pc = self.pc
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: nop", 2)

    def _save(self):
        pc = self.pc
        self.pc += 1
        self.intr = 5
        self.plugin.debug_print(f"{format(pc, 'X')}: save", 2)

    def _restore(self):
        pc = self.pc
        self.pc += 1
        self.intr = 6
        self.plugin.debug_print(f"{format(pc, 'X')}: restore", 2)

    def _restart(self):
        pc = self.pc
        self.intr = 3
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: restart", 2)

    def _ret_popped(self):
        pc = self.pc
        data = self.stack.pop()
        self._return(data)
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: ret_popped", 2)

    def _pop(self):
        pc = self.pc
        if self.zver < 5:
            self._pop_impl(pc)
        else:
            self._pop_impl(pc)

    def _quit(self):
        pc = self.pc
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: quit", 2)
        self.output.print_string("[Press any key to quit]", [])
        self.intr = 69

    def _new_line(self):
        pc = self.pc
        self.output.new_line()
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: new_line", 2)

    def _show_status(self):
        pc = self.pc
        self._show_status2()
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: show_status", 2)

    def _verify(self):
        pc = self.pc
        self.pc += 1
        self.file.seek(0x40)
        file_length = self.header.length_of_file
        data_length = file_length - 0x40
        data = self.file.read(data_length)

        chksum = sum(data) % 0x10000

        condition = chksum == self.header.checksum
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: verify {jif}, {offset}", 2)

    def _piracy(self):
        pc = self.pc
        self.pc += 1
        jif, offset = self.branch(True)
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: piracy {jif}, {offset}", 2)
