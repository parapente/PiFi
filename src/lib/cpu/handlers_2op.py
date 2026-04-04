class ZCpu2OpHandlers:
    def _je(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        condition = False
        n = self.numops
        if n >= 2:
            j = 2
            condition = ops[0] == ops[1]
            while j < n:
                condition = condition or (ops[0] == ops[j])
                j += 1
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: je {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _jl(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        condition = ((ops[0] & 0x8000) > (ops[1] & 0x8000)) or (
            ((ops[0] & 0x8000) == (ops[1] & 0x8000)) and (ops[0] < ops[1])
        )
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: jl {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _jg(self):
        mem = self.mem
        if mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        pc = self.pc
        ops = self.ops
        condition = ((ops[0] & 0x8000) < (ops[1] & 0x8000)) or (
            ((ops[0] & 0x8000) == (ops[1] & 0x8000)) and (ops[0] > ops[1])
        )
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: jg {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _dec_chk(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        val = self._s2i(self._dec2(ops[0]))
        condition = val < self._s2i(ops[1])
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: dec_chk {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _inc_chk(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        val = self._s2i(self._inc2(ops[0]))
        condition = val > self._s2i(ops[1])
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: inc_chk {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _jin(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        obj = self._find_object(ops[0])
        b = self._get_obj_parent(obj)
        condition = b == ops[1]
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: jin {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _test(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        condition = (ops[0] & ops[1]) == ops[1]
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: test {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _or(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        res = ops[0] | ops[1]
        self._zstore(res, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: or {ops[0 : self.numops]}", 2)

    def _and(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        res = ops[0] & ops[1]
        self._zstore(res, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: and {ops[0 : self.numops]}", 2)

    def _test_attr(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        obj = self._find_object(ops[0])
        if self.zver < 4:
            b = (
                (self.mem[obj] << 24)
                + (self.mem[obj + 1] << 16)
                + (self.mem[obj + 2] << 8)
                + self.mem[obj + 3]
            )
            mask = 1 << (31 - ops[1])
        else:
            b = (
                (self.mem[obj] << 40)
                + (self.mem[obj + 1] << 32)
                + (self.mem[obj + 2] << 24)
                + (self.mem[obj + 3] << 16)
                + (self.mem[obj + 4] << 8)
                + self.mem[obj + 5]
            )
            mask = 1 << (47 - ops[1])
        condition = (b & mask) == mask
        jif, offset = self.branch(condition)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: test_attr {ops[0 : self.numops]} [{jif}] {offset}",
                2,
            )

    def _set_attr(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: set_attr {ops[0 : self.numops]}", 2
            )
        if ops[0] == 0:
            print("set_attr: Cannot set attr of object 0!")
            return
        obj = self._find_object(ops[0])
        if self.zver < 4:
            b = (
                (self.mem[obj] << 24)
                + (self.mem[obj + 1] << 16)
                + (self.mem[obj + 2] << 8)
                + self.mem[obj + 3]
            )
            mask = 1 << (31 - ops[1])
            b |= mask
            self.mem[obj] = b >> 24
            self.mem[obj + 1] = (b & 0xFF0000) >> 16
            self.mem[obj + 2] = (b & 0xFF00) >> 8
            self.mem[obj + 3] = b & 0xFF
        else:
            b = (
                (self.mem[obj] << 40)
                + (self.mem[obj + 1] << 32)
                + (self.mem[obj + 2] << 24)
                + (self.mem[obj + 3] << 16)
                + (self.mem[obj + 4] << 8)
                + self.mem[obj + 5]
            )
            mask = 1 << (47 - ops[1])
            b |= mask
            self.mem[obj] = b >> 40
            self.mem[obj + 1] = (b & 0xFF00000000) >> 32
            self.mem[obj + 2] = (b & 0xFF000000) >> 24
            self.mem[obj + 3] = (b & 0xFF0000) >> 16
            self.mem[obj + 4] = (b & 0xFF00) >> 8
            self.mem[obj + 5] = b & 0xFF

    def _clear_attr(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: clear_attr {ops[0 : self.numops]}", 2
            )
        if ops[0] == 0:
            print("clear_attr: Cannot clear attr of object 0!")
            return
        obj = self._find_object(ops[0])
        if self.zver < 4:
            b = (
                (self.mem[obj] << 24)
                + (self.mem[obj + 1] << 16)
                + (self.mem[obj + 2] << 8)
                + self.mem[obj + 3]
            )
            mask = 1 << (31 - ops[1])
            if (b & mask) != 0:
                b ^= mask
                self.mem[obj] = b >> 24
                self.mem[obj + 1] = (b & 0xFF0000) >> 16
                self.mem[obj + 2] = (b & 0xFF00) >> 8
                self.mem[obj + 3] = b & 0xFF
        else:
            b = (
                (self.mem[obj] << 40)
                + (self.mem[obj + 1] << 32)
                + (self.mem[obj + 2] << 24)
                + (self.mem[obj + 3] << 16)
                + (self.mem[obj + 4] << 8)
                + self.mem[obj + 5]
            )
            mask = 1 << (47 - ops[1])
            if (b & mask) != 0:
                b ^= mask
                self.mem[obj] = b >> 40
                self.mem[obj + 1] = (b & 0xFF00000000) >> 32
                self.mem[obj + 2] = (b & 0xFF000000) >> 24
                self.mem[obj + 3] = (b & 0xFF0000) >> 16
                self.mem[obj + 4] = (b & 0xFF00) >> 8
                self.mem[obj + 5] = b & 0xFF

    def _store(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if ops[0] == 0:
            self.stack.pop()
        self._zstore(ops[1], ops[0])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: store {ops[0 : self.numops]}", 2
            )

    def _insert_obj(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: insert_obj {ops[0 : self.numops]}", 2
            )
        if ops[1] == 0 or ops[0] == 0:
            print("insert_obj: Cannot use 0 as source or destination!")
            return
        d = self._find_object(ops[1])
        o = self._find_object(ops[0])
        if self.zver < 4:
            dchild = self.mem[d + 6]
            self.mem[d + 6] = ops[0]
            if self.mem[o + 4] != 0:
                f = self._find_object(self.mem[o + 4])
                if self.mem[f + 6] == ops[0]:
                    self.mem[f + 6] = self.mem[o + 5]
                else:
                    t = self._find_object(self.mem[f + 6])
                    while self.mem[t + 5] != ops[0]:
                        t = self._find_object(self.mem[t + 5])
                    self.mem[t + 5] = self.mem[o + 5]
            self.mem[o + 4] = ops[1]
            self.mem[o + 5] = dchild
        else:
            n = (self.mem[o + 6] << 8) + self.mem[o + 7]
            if n != ops[1]:
                dchild_p1 = self.mem[d + 10]
                dchild_p2 = self.mem[d + 11]
                self.mem[d + 10] = ops[0] >> 8
                self.mem[d + 11] = ops[0] & 0xFF
                if n != 0:
                    f = self._find_object(n)
                    cn = (self.mem[f + 10] << 8) + self.mem[f + 11]
                    if cn == ops[0]:
                        self.mem[f + 10] = self.mem[o + 8]
                        self.mem[f + 11] = self.mem[o + 9]
                    else:
                        t = self._find_object(cn)
                        sn = (self.mem[t + 8] << 8) + self.mem[t + 9]
                        while sn != ops[0]:
                            t = self._find_object(sn)
                            sn = (self.mem[t + 8] << 8) + self.mem[t + 9]
                        self.mem[t + 8] = self.mem[o + 8]
                        self.mem[t + 9] = self.mem[o + 9]
                self.mem[o + 6] = ops[1] >> 8
                self.mem[o + 7] = ops[1] & 0xFF
                self.mem[o + 8] = dchild_p1
                self.mem[o + 9] = dchild_p2

    def _loadw(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        return_var = self.mem[self.pc]
        self.pc += 1
        addr = (ops[0] + 2 * ops[1]) % 65536
        data = (self.mem[addr] << 8) + self.mem[addr + 1]
        self._zstore(data, return_var)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: loadw {ops[0 : self.numops]}", 2
            )

    def _loadb(self):
        pc = self.pc
        mem = self.mem
        if mem[pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        return_var = mem[self.pc]
        self.pc += 1
        addr = (ops[0] + ops[1]) % 65536
        data = mem[addr]
        self._zstore(data, return_var)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: loadb {ops[0 : self.numops]}", 2
            )

    def _get_prop(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if ops[0] == 0:
            print("get_prop: Can't get property of nothing!")
            self._zstore(0, self.mem[self.pc])
            self.pc += 1
            return
        obj = self._find_object(ops[0])
        addr = self._get_prop_table_addr(obj)
        prop = self._find_prop(addr, ops[1])
        if prop == 0:
            base = self.header.obj_table
            data = (self.mem[base + ((ops[1] - 1) * 2)] << 8) + self.mem[
                base + ((ops[1] - 1) * 2) + 1
            ]
        else:
            if self.zver < 4:
                size = self.mem[prop]
                nob = self._get_prop_size(size, ops[1])
                if nob == 1:
                    data = self.mem[prop + 1]
                else:
                    data = (self.mem[prop + 1] << 8) + self.mem[prop + 2]
            else:
                if (self.mem[prop] & 0x80) == 0x80:
                    size = self.mem[prop + 1] & 0x3F
                    if size == 0:
                        size = 64
                    if size == 1:
                        data = self.mem[prop + 2]
                    else:
                        data = (self.mem[prop + 2] << 8) + self.mem[prop + 3]
                elif (self.mem[prop] & 0x40) == 0x40:
                    data = (self.mem[prop + 1] << 8) + self.mem[prop + 2]
                else:
                    data = self.mem[prop + 1]
        self._zstore(data, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: get_prop {ops[0 : self.numops]}", 2
            )

    def _get_prop_addr(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if ops[0] == 0:
            self.output.print_string(
                "** get_prop_addr got 0 as object! **\n", ops[0 : self.numops]
            )
            prop = 0
        else:
            obj = self._find_object(ops[0])
            addr = self._get_prop_table_addr(obj)
            prop = self._find_prop(addr, ops[1])
            if prop != 0:
                if self.zver < 4:
                    prop += 1
                else:
                    if (self.mem[prop] & 128) == 128:
                        prop += 2
                    else:
                        prop += 1
        self._zstore(prop, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: get_prop_addr {ops[0 : self.numops]}",
                2,
            )

    def _get_next_prop(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: get_next_prop {ops[0 : self.numops]}",
                2,
            )
        if ops[0] == 0:
            print("get_next_prop: Can't get property of nothing!")
            self._zstore(0, self.mem[self.pc])
            self.pc += 1
            return
        obj = self._find_object(ops[0])
        if ops[1] == 0:
            find_first_value = True
        else:
            find_first_value = False
        if self.zver < 4:
            if find_first_value:
                addr = self._get_prop_table_addr(obj)
                l = self.mem[addr]
                prop_addr = addr + (2 * l) + 2
                prop = prop_addr % 32
            else:
                addr = self._get_prop_table_addr(obj)
                prop_addr = self._find_prop(addr, ops[1])
                if prop_addr != 0:
                    nob = (prop_addr // 32) + 1
                    prop_addr += nob + 1
                    prop = prop_addr % 32
                else:
                    exit("No such property!")
        else:
            if find_first_value:
                addr = self._get_prop_table_addr(obj)
                prop = self.mem[addr] & 0x3F
            else:
                addr = self._get_prop_table_addr(obj)
                prop_addr = self._find_prop(addr, ops[1])
                if prop_addr != 0:
                    if (self.mem[prop_addr] & 0x80) != 0:
                        prop_addr += 1
                        num = self.mem[prop_addr] & 0x3F
                        if num == 0:
                            num = 64
                        prop_addr += num + 1
                    elif (self.mem[prop_addr] & 0x40) != 0:
                        prop_addr += 3
                    else:
                        prop_addr += 2
                    prop = self.mem[prop_addr] & 0x3F
                else:
                    exit("No such property!")
        self._zstore(prop, self.mem[self.pc])
        self.pc += 1

    def _add(self):
        pc = self.pc
        mem = self.mem
        if mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        result = (ops[0] + ops[1]) & 0xFFFF
        self._zstore(result, mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: add {ops[0 : self.numops]}", 2)

    def _sub(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        result = (ops[0] - ops[1]) & 0xFFFF
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: sub {ops[0 : self.numops]}", 2)

    def _mul(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        result = (ops[0] * ops[1]) & 0xFFFF
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: mul {ops[0 : self.numops]}", 2)

    def _div(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if ops[1] == 0:
            print("Divide by zero!")
            exit(20)
        a = self._s2i(ops[0])
        b = self._s2i(ops[1])
        if a < 0:
            s1 = -1
        else:
            s1 = 1
        if b < 0:
            s2 = -1
        else:
            s2 = 1
        result = self._i2s(s1 * s2 * (abs(a) // abs(b)))
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: div {ops[0 : self.numops]}", 2)

    def _mod(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if ops[1] == 0:
            print("Divide by zero!")
            exit(20)
        a = self._s2i(ops[0])
        b = self._s2i(ops[1])
        if a < 0:
            s1 = -1
        else:
            s1 = 1
        result = self._i2s(s1 * (abs(a) % abs(b)))
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: mod {ops[0 : self.numops]}", 2)

    def _call_2s(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        argv = [ops[1]]
        return_addr = self.mem[self.pc]
        self.pc += 1
        self._routine(ops[0], argv, 1, return_addr)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call_2s {ops[0 : self.numops]}", 2
            )
            self.plugin.debug_print("--v", 2)

    def _call_2n(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        argv = [ops[1]]
        return_addr = -1
        self._routine(ops[0], argv, 1, return_addr)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call_2n {ops[0 : self.numops]}", 2
            )
            self.plugin.debug_print("--v", 2)

    def _set_colour(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        self.output.set_colour(ops[0], ops[1])
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: set_colour {ops[0 : self.numops]}", 2
            )

    def _throw(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xC0:
            self._read_operands_var_2op()
        else:
            self._read_operands_long_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: throw {ops[0 : self.numops]}", 2
            )

        value = ops[0]
        stack_frame = ops[1]

        stack = self.stack

        if stack_frame < 2 or stack_frame > stack.framespos:
            if self.plugin.level >= 2:
                self.plugin.debug_print(
                    f"throw: invalid stack_frame {stack_frame}, doing normal return", 2
                )
            self._return(value)
            return

        stack.framespos = stack_frame
        stack.pop_local_vars()
        stack.pop_eval_stack()
        self._return(value)
