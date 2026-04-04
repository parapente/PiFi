from lib.ztext import decode_text, encode_to_zscii


class ZCpu1OpHandlers:
    def _jz(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        jif, offset = self.branch(ops[0] == 0)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: jz {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _get_sibling(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        return_var = self.mem[self.pc]
        self.pc += 1
        obj = self._find_object(ops[0])
        sibl = self._get_obj_sibling(obj)
        condition = sibl != 0
        jif, offset = self.branch(condition)
        self._zstore(sibl, return_var)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: get_sibling {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _get_child(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        return_var = self.mem[self.pc]
        self.pc += 1
        obj = self._find_object(ops[0])
        child = self._get_obj_child(obj)
        condition = child != 0
        jif, offset = self.branch(condition)
        self._zstore(child, return_var)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: get_child {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _get_parent(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        obj = self._find_object(ops[0])
        parent = self._get_obj_parent(obj)
        self._zstore(parent, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: get_parent {ops[0 : self.numops]}", 2
            )

    def _get_prop_len(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        if ops[0] == 0:
            print("get_prop_len: Can't get property of nothing!")
            self._zstore(0, self.mem[self.pc])
        else:
            ops[0] = ops[0] - 1
            nob = self._get_prop_size_from_addr(ops[0])
            self._zstore(nob, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: get_prop_len {ops[0 : self.numops]}", 2
            )

    def _inc(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        self._inc2(ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: inc {ops[0 : self.numops]}", 2)

    def _dec(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        self._dec2(ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: dec {ops[0 : self.numops]}", 2)

    def _print_addr(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        uaddr = ops[0]
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
        self.output.print_string(text, ops[0 : self.numops])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: print_addr {ops[0 : self.numops]}", 2
            )

    def _call_1s(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        argv = []
        return_addr = self.mem[self.pc]
        self.pc += 1
        self._routine(ops[0], argv, 0, return_addr)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call_1s {ops[0 : self.numops]}", 2
            )

    def _remove_obj(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: remove_obj {ops[0 : self.numops]}", 2
            )
        if ops[0] == 0:
            return
        obj = self._find_object(ops[0])
        if self.zver < 4:
            f = self._find_object(self.mem[obj + 4])
            if self.mem[f + 6] == ops[0]:
                self.mem[f + 6] = self.mem[obj + 5]
            else:
                t = self._find_object(self.mem[f + 6])
                while self.mem[t + 5] != ops[0]:
                    t = self._find_object(self.mem[t + 5])
                self.mem[t + 5] = self.mem[obj + 5]
            self.mem[obj + 4] = 0
            self.mem[obj + 5] = 0
        else:
            fn = (self.mem[obj + 6] << 8) + self.mem[obj + 7]
            if fn != 0:
                f = self._find_object(fn)
                cn = (self.mem[f + 10] << 8) + self.mem[f + 11]
                if cn == ops[0]:
                    self.mem[f + 10] = self.mem[obj + 8]
                    self.mem[f + 11] = self.mem[obj + 9]
                else:
                    t = self._find_object(cn)
                    sn = (self.mem[t + 8] << 8) + self.mem[t + 9]
                    while sn != ops[0]:
                        t = self._find_object(sn)
                        sn = (self.mem[t + 8] << 8) + self.mem[t + 9]
                    self.mem[t + 8] = self.mem[obj + 8]
                    self.mem[t + 9] = self.mem[obj + 9]
            self.mem[obj + 6] = 0
            self.mem[obj + 7] = 0
            self.mem[obj + 8] = 0
            self.mem[obj + 9] = 0

    def _print_obj(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        if (
            (ops[0] < 1)
            or ((self.zver < 4) and (ops[0] > 255))
            or ((self.zver > 3) and (ops[0] > 65535))
        ):
            exit("Invalid object number")
        obj = self._find_object(ops[0])
        addr = self._get_prop_table_addr(obj)
        length = self.mem[addr]
        buf = []
        i = 1
        while i < (2 * length):
            buf.append(self.mem[addr + i])
            buf.append(self.mem[addr + i + 1])
            i += 2
        text = decode_text(buf)
        self.output.print_string(text, ops[0 : self.numops])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: print_obj {ops[0 : self.numops]}", 2
            )

    def _ret(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        self._return(ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: ret {ops[0 : self.numops]}", 2)

    def _jump(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        offset = ops[0] - 2
        if offset > 0x7FFF:
            offset = offset - 0x10000
        self.pc = self.pc + offset
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: jump {ops[0 : self.numops]}", 2
            )

    def _print_paddr(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        uaddr = self._unpack_addr(ops[0])

        mem = self.mem
        buf = []
        eot = False
        i = 0
        while not eot:
            if (mem[uaddr + i] & 128) == 128:
                eot = True
            buf.extend([mem[uaddr + i], mem[uaddr + i + 1]])
            i += 2
        text = decode_text(buf)
        self.output.print_string(text, encode_to_zscii(text))
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: print_paddr {ops[0 : self.numops]}", 2
            )

    def _load(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        if ops[0] == 0:
            data = self.stack.pop()
            self.stack.push(data)
        elif ops[0] < 16:
            data = self.stack.local_vars[ops[0] - 1]
        elif ops[0] < 256:
            data = self.mem[self.header.global_variables_table + (ops[0] - 16) * 2] << 8
            data += self.mem[self.header.global_variables_table + (ops[0] - 16) * 2 + 1]
        else:
            exit("No such variable!!!")
        self._zstore(data, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: load {ops[0 : self.numops]}", 2
            )

    def _not(self):
        pc = self.pc
        self._read_operands_short_1op()
        ops = self.ops
        if self.zver >= 5:
            self._not_impl(pc, ops)
        else:
            r = ops[0] ^ 0xFFFF
            self._zstore(r, self.mem[self.pc])
            self.pc += 1
            if self.plugin.level >= 2:
                self.plugin.debug_print(
                    f"{format(pc, 'X')}: not {ops[0 : self.numops]}", 2
                )

    def _call_1n(self, pc: int, ops: list):
        argv = []
        addr = ops[0]
        return_addr = -1
        self._routine(addr, argv, 0, return_addr)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call_1n {ops[0 : self.numops]}", 2
            )
