from sys import exit
from lib.ztext import decode_text, convert_from_zscii, encode_to_zscii, encode_text


class ZCpuVarHandlers:
    def _call(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        argv = ops[1 : self.numops]
        return_addr = self.mem[self.pc]
        self.pc = self.pc + 1
        self._routine(ops[0], argv, self.numops - 1, return_addr)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call {ops[0 : self.numops]}", 2
            )

    def _storew(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        addr = (ops[0] + (2 * ops[1])) % 65536
        self.mem[addr] = ops[2] >> 8
        self.mem[addr + 1] = ops[2] & 0xFF
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: storew {ops[0 : self.numops]}", 2
            )

    def _storeb(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        addr = (ops[0] + ops[1]) % 65536
        self.mem[addr] = ops[2] & 255
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: storeb {ops[0 : self.numops]}", 2
            )

    def _put_prop(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if ops[0] == 0:
            exit("Can't put prop to nothing!")
        d = self._find_object(ops[0])
        if self.zver < 4:
            prop_addr = self._get_prop_table_addr(d)
            prop = self._find_prop(prop_addr, ops[1])
            if prop == 0:
                print(("Property ", ops[1], " not found for object ", ops[0]))
                exit()
            else:
                if (self.mem[prop] // 32) == 0:
                    self.mem[prop + 1] = ops[2] & 0xFF
                else:
                    self.mem[prop + 1] = ops[2] >> 8
                    self.mem[prop + 2] = ops[2] & 0xFF
        else:
            prop_addr = self._get_prop_table_addr(d)
            prop = self._find_prop(prop_addr, ops[1])
            if prop == 0:
                print(("Property ", ops[1], " not found for object ", ops[0]))
                exit()
            else:
                if ((self.mem[prop] & 0x80) == 0) and (
                    (self.mem[prop] & 0x40) == 0
                ):
                    self.mem[prop + 1] = ops[2] & 0xFF
                elif (self.mem[prop] & 0x80) == 0:
                    self.mem[prop + 1] = ops[2] >> 8
                    self.mem[prop + 2] = ops[2] & 0xFF
                else:
                    self.mem[prop + 2] = ops[2] >> 8
                    self.mem[prop + 3] = ops[2] & 0xFF
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: put_prop {ops[0 : self.numops]}", 2
            )

    def _sread(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        self.intr = 1
        if self.numops >= 2:
            self.intr_data = list(ops[0 : self.numops])
        else:
            self.intr_data = [ops[0], 0]
        self.plugin.show_cursor()
        if self.zver < 4:
            self._show_status2()
            pass
        elif self.zver == 4:
            pass
        elif self.zver == 5:
            pass
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: sread {ops[0 : self.numops]}", 2
            )

    def _print_char(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        try:
            text = self.print_char_dict[ops[0]]
        except KeyError:
            text = convert_from_zscii(ops[0], 0)
            self.print_char_dict[ops[0]] = text
        self.output.print_string(text, ops[0 : self.numops])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: print_char {ops[0 : self.numops]}", 2
            )

    def _print_num(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if ops[0] > 0x7FFF:
            self.output.print_string(
                f"{ops[0] - 65536}", [ord(c) for c in f"{ops[0] - 65536}"]
            )
        else:
            self.output.print_string(f"{ops[0]}", [ord(c) for c in f"{ops[0]}"])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: print_num {ops[0 : self.numops]}", 2
            )

    def _random(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if ops[0] > 0x7FFF:
            self.random.set_seed(0x10000 - ops[0])
            r = 0
        elif ops[0] != 0:
            r = self.random.get_random(ops[0])
        else:
            self.random.set_seed(0)
            r = 0
        self._zstore(r, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: random {ops[0 : self.numops]}", 2
            )

    def _push(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        self.stack.push(ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: push {ops[0 : self.numops]}", 2
            )

    def _pull(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if self.zver != 6:
            n = self.stack.pop()
            if ops[0] == 0:
                self.stack.pop()
            self._zstore(n, ops[0])
            if self.plugin.level >= 2:
                self.plugin.debug_print(
                    f"{format(pc, 'X')}: pull {ops[0 : self.numops]}", 2
                )
        else:
            if self.numops == 0:
                n = self.stack.pop()
                variable = self.mem[self.pc]
                self._zstore(n, variable)
                self.pc += 1
            else:
                exit("pull: User stacks not implemented for V6!")
                if self.plugin.level >= 2:
                    self.plugin.debug_print(
                        f"{format(pc, 'X')}: pull {ops} -> {variable}", 2
                    )

    def _split_window(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        self.output.show_upper_window(ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: split_window {ops[0 : self.numops]}", 2
            )

    def _set_window(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        self.output.set_window(ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: set_window {ops[0 : self.numops]}", 2
            )

    def _call_vs2(self):
        pc = self.pc
        self._read_operands_var_2op2()
        ops = self.ops
        ret = self.mem[self.pc]
        self.pc += 1
        argv = ops[1 : self.numops]
        self._routine(ops[0], argv, self.numops - 1, ret)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call_vs2 {ops[0 : self.numops]}", 2
            )

    def _erase_window(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if ops[0] == 0xFFFF:
            self.output.clear_screen()
            self.output.set_window(0)
            self.plugin.window[0].cursor = None
            self.plugin.set_font_style(0)
            self.plugin.unsplit()
        elif ops[0] == 0xFFFE:
            pass
        else:
            self.plugin.erase_window(ops[0])
            if self.plugin.level >= 2:
                self.plugin.debug_print(
                    f"{format(pc, 'X')}: erase_window {ops[0 : self.numops]}", 2
                )

    def _erase_line(self):
        self.plugin.debug_print(": erase_line", 0)
        exit("Not implemented yet!")

    def _set_cursor(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        self.output.set_cursor(ops[1], ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: set_cursor {ops[0 : self.numops]}", 2
            )

    def _get_cursor(self):
        self.plugin.debug_print(": get_cursor", 0)
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        print("ops:", ops)
        exit("Not implemented yet!")

    def _set_text_style(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        self.output.set_font_style(ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: set_text_style {ops[0 : self.numops]}", 2
            )

    def _buffer_mode(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        self.output.set_buffering(ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: buffer_mode {ops[0 : self.numops]}", 2
            )

    def _output_stream(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if ops[0] != 0:
            if ops[0] == 3:
                table = ops[1]
            else:
                table = -1
            if ops[0] > 0x7FFF:
                self.output.deselect_stream(0x10000 - ops[0])
            else:
                self.output.select_stream(ops[0], table)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: output_stream {ops[0 : self.numops]}", 2
            )

    def _input_stream(self):
        self.plugin.debug_print(": input_stream", 0)
        exit("Not implemented yet!")

    def _sound_effect(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: sound_effect {ops[0 : self.numops]}", 2
            )
            self.plugin.debug_print("TODO:Sound effects", 2)

    def _read_char(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: read_char {ops[0 : self.numops]}", 2
            )
        if self.numops > 1:
            self.intr_data = [ops[1], ops[2]]
        else:
            self.intr_data = [0]
        self.intr = 2

    def _scan_table(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: scan_table {ops[0 : self.numops]}", 2
            )

        x = ops[0]
        table_addr = ops[1]
        length = ops[2]
        form = ops[3] if self.numops > 3 else 0x82

        is_word_search = (form & 0x80) != 0
        entry_size = form & 0x7F
        if entry_size == 0:
            entry_size = 2 if is_word_search else 1

        result = 0
        found = False

        for i in range(length):
            entry_addr = table_addr + i * entry_size

            if is_word_search:
                table_value = (self.mem[entry_addr] << 8) | self.mem[entry_addr + 1]
            else:
                table_value = self.mem[entry_addr]

            if table_value == x:
                result = entry_addr
                found = True
                break

        self._zstore(result, self.mem[self.pc])
        self.pc += 1
        jif, offset = self.branch(found)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: scan_table -> {result} [{jif}] {offset}", 2
            )

    def _not_var(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        r = ops[0] ^ 0xFFFF
        self._zstore(r, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: not_var {ops[0 : self.numops]}", 2
            )

    def _call_vn(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        argv = ops[1 : self.numops]
        self._routine(ops[0], argv, self.numops - 1, -1)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call_vn {ops[0 : self.numops]}", 2
            )

    def _call_vn2(self):
        pc = self.pc
        self._read_operands_var_2op2()
        ops = self.ops
        argv = ops[1 : self.numops]
        self._routine(ops[0], argv, self.numops - 1, -1)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call_vn2 {ops[0 : self.numops]}", 2
            )

    def _tokenize(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        n = self.numops
        self.intr = 4
        self.intr_data = [0, 0, 0, 0]
        self.intr_data[0] = ops[0]
        self.intr_data[1] = ops[1]
        if n >= 3:
            self.intr_data[2] = ops[2]
        if n == 4:
            self.intr_data[3] = ops[3]
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: tokenize {ops[0 : self.numops]}", 2
            )

    def _encode_text(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        addr, offset, length = ops[0], ops[2], ops[1]
        z_text = [x for x in self.mem[addr + offset : addr + offset + length]]
        encode_text(z_text)
        self.plugin.debug_print(": encode_text", 0)
        self.plugin.debug_print(
            f"{format(pc, 'X')}: tokenize {ops[0 : self.numops]}", 2
        )
        exit("Not tested yet!")

    def _copy_table(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: copy_table {ops[0 : self.numops]}", 2
            )

        first = ops[0]
        second = ops[1]
        size = self._s2i(ops[2])

        if second == 0:
            for i in range(abs(size)):
                self.mem[first + i] = 0
        elif size > 0:
            if second > first:
                for i in range(size - 1, -1, -1):
                    self.mem[second + i] = self.mem[first + i]
            else:
                for i in range(size):
                    self.mem[second + i] = self.mem[first + i]
        else:
            abs_size = abs(size)
            for i in range(abs_size):
                self.mem[second + i] = self.mem[first + i]

    def _print_table(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: print_table {ops[0 : self.numops]}", 2
            )

        text_addr = ops[0]
        width = ops[1]
        height = ops[2] if self.numops > 2 else 1
        skip = ops[3] if self.numops > 3 else 0

        for row in range(height):
            line_start = text_addr + row * (width + skip)
            for col in range(width):
                char_addr = line_start + col
                char_code = self.mem[char_addr]
                self.output.print_string(chr(char_code), [char_code])
            if row < height - 1:
                self.output.new_line()

    def _check_arg_count(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        n = self.numops
        noa = self.stack.pop_frame()
        self.stack.push_frame(noa)
        condition = ops[0] <= noa
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: check_arg_count {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )
