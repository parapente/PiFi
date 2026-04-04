from typing import cast
from lib.container.container import Container
from lib.header import ZHeader
from lib.memory import ZMemory
from lib.output import ZOutput
from lib.stack import ZStack
from lib.zrandom import ZRandom
from lib.ztext import decode_text, encode_text, convert_from_zscii, encode_to_zscii
from plugins.plugskel import PluginSkeleton
from sys import exit


class ZCpuBase:
    mem = None
    header = None
    stack = None
    output = None
    random = None
    pc = 0
    zver = 0
    t2op = None
    t1op = None
    t0op = None
    tvar = None
    text = None
    intr = 0
    intr_data = []
    file = None
    plugin = None
    ops = [0] * 8
    numops = 0

    def __init__(self, o: ZOutput, p: PluginSkeleton):
        self.container = Container()
        self.mem = cast(ZMemory, self.container.resolve("ZMemory")).mem
        self.header = cast(ZHeader, self.container.resolve("ZHeader"))
        self.output = o
        self.plugin = p
        self.pc = self.header.pc
        self.plugin.debug_print(f"Starting PC: {self.pc}", 1)
        self.zver = self.header.version
        self.stack = cast(ZStack, self.container.resolve("ZStack"))
        self.random = cast(ZRandom, self.container.resolve("ZRandom"))
        self.print_dict = dict()
        self.print_char_dict = dict()
        self.command_dict = dict()
        self._bind_version_specific_methods()
        self._init_opcode_dicts()

    def _init_opcode_dicts(self):
        self.t2op = dict(
            {
                1: self._je,
                2: self._jl,
                3: self._jg,
                4: self._dec_chk,
                5: self._inc_chk,
                6: self._jin,
                7: self._test,
                8: self._or,
                9: self._and,
                10: self._test_attr,
                11: self._set_attr,
                12: self._clear_attr,
                13: self._store,
                14: self._insert_obj,
                15: self._loadw,
                16: self._loadb,
                17: self._get_prop,
                18: self._get_prop_addr,
                19: self._get_next_prop,
                20: self._add,
                21: self._sub,
                22: self._mul,
                23: self._div,
                24: self._mod,
                25: self._call_2s,
                26: self._call_2n,
                27: self._set_colour,
                28: self._throw,
            }
        )
        self.t1op = dict(
            {
                128: self._jz,
                129: self._get_sibling,
                130: self._get_child,
                131: self._get_parent,
                132: self._get_prop_len,
                133: self._inc,
                134: self._dec,
                135: self._print_addr,
                136: self._call_1s,
                137: self._remove_obj,
                138: self._print_obj,
                139: self._ret,
                140: self._jump,
                141: self._print_paddr,
                142: self._load,
                143: self._not,
            }
        )
        self.t0op = dict(
            {
                176: self._rtrue,
                177: self._rfalse,
                178: self._print,
                179: self._print_ret,
                180: self._nop,
                181: self._save,
                182: self._restore,
                183: self._restart,
                184: self._ret_popped,
                185: self._pop,
                186: self._quit,
                187: self._new_line,
                188: self._show_status,
                189: self._verify,
                190: None,
                191: self._piracy,
            }
        )
        self.tvar = dict(
            {
                224: self._call,
                225: self._storew,
                226: self._storeb,
                227: self._put_prop,
                228: self._sread,
                229: self._print_char,
                230: self._print_num,
                231: self._random,
                232: self._push,
                233: self._pull,
                234: self._split_window,
                235: self._set_window,
                236: self._call_vs2,
                237: self._erase_window,
                238: self._erase_line,
                239: self._set_cursor,
                240: self._get_cursor,
                241: self._set_text_style,
                242: self._buffer_mode,
                243: self._output_stream,
                244: self._input_stream,
                245: self._sound_effect,
                246: self._read_char,
                247: self._scan_table,
                248: self._not_var,
                249: self._call_vn,
                250: self._call_vn2,
                251: self._tokenize,
                252: self._encode_text,
                253: self._copy_table,
                254: self._print_table,
                255: self._check_arg_count,
            }
        )
        self.text = dict(
            {
                0: self._save_ext,
                1: self._restore_ext,
                2: self._log_shift,
                3: self._art_shift,
                4: self._set_font,
                5: self._draw_picture,
                6: self._picture_data,
                7: self._erase_picture,
                8: self._set_margins,
                9: self._save_undo,
                10: self._restore_undo,
                11: self._print_unicode,
                12: self._check_unicode,
                13: None,
                14: None,
                15: None,
                16: self._move_window,
                17: self._window_size,
                18: self._window_style,
                19: self._get_wind_prop,
                20: self._scroll_window,
                21: self._pop_stack,
                22: self._read_mouse,
                23: self._mouse_window,
                24: self._push_stack,
                25: self._put_wind_prop,
                26: self._print_form,
                27: self._make_menu,
                28: self._picture_table,
            }
        )

    def _bind_version_specific_methods(self):
        if self.zver < 4:
            self._unpack_addr = self._unpack_addr_v123
            self._get_obj_parent = self._get_obj_parent_v123
            self._get_obj_sibling = self._get_obj_sibling_v123
            self._get_obj_child = self._get_obj_child_v123
            self._get_prop_table_addr = self._get_prop_table_addr_v123
            self._get_prop_size = self._get_prop_size_v123
            self._get_prop_size_from_addr = self._get_prop_size_from_addr_v123
            self._prepare_routine = self._prepare_routine_v1234
            self._not_impl = self._not_v1234
            self._pop_impl = self._pop_v1234
            self._show_status2 = self._show_status2_v1234
        elif self.zver < 5:
            self._unpack_addr = self._unpack_addr_v45
            self._get_obj_parent = self._get_obj_parent_v4plus
            self._get_obj_sibling = self._get_obj_sibling_v4plus
            self._get_obj_child = self._get_obj_child_v4plus
            self._get_prop_table_addr = self._get_prop_table_addr_v4plus
            self._get_prop_size = self._get_prop_size_v4plus
            self._get_prop_size_from_addr = self._get_prop_size_from_addr_v4plus
            self._prepare_routine = self._prepare_routine_v1234
            self._not_impl = self._not_v1234
            self._pop_impl = self._pop_v1234
            self._show_status2 = self._show_status2_v1234
        elif self.zver < 6:
            self._unpack_addr = self._unpack_addr_v45
            self._get_obj_parent = self._get_obj_parent_v4plus
            self._get_obj_sibling = self._get_obj_sibling_v4plus
            self._get_obj_child = self._get_obj_child_v4plus
            self._get_prop_table_addr = self._get_prop_table_addr_v4plus
            self._get_prop_size = self._get_prop_size_v4plus
            self._get_prop_size_from_addr = self._get_prop_size_from_addr_v4plus
            self._prepare_routine = self._prepare_routine_v5plus
            self._not_impl = self._not_v5plus
            self._pop_impl = self._pop_v5plus
            self._show_status2 = self._show_status2_v5plus
        elif self.zver < 8:
            self._unpack_addr = self._unpack_addr_v67
            self._get_obj_parent = self._get_obj_parent_v4plus
            self._get_obj_sibling = self._get_obj_sibling_v4plus
            self._get_obj_child = self._get_obj_child_v4plus
            self._get_prop_table_addr = self._get_prop_table_addr_v4plus
            self._get_prop_size = self._get_prop_size_v4plus
            self._get_prop_size_from_addr = self._get_prop_size_from_addr_v4plus
            self._prepare_routine = self._prepare_routine_v5plus
            self._not_impl = self._not_v5plus
            self._pop_impl = self._pop_v5plus
            self._show_status2 = self._show_status2_v5plus
        else:
            self._unpack_addr = self._unpack_addr_v8
            self._get_obj_parent = self._get_obj_parent_v4plus
            self._get_obj_sibling = self._get_obj_sibling_v4plus
            self._get_obj_child = self._get_obj_child_v4plus
            self._get_prop_table_addr = self._get_prop_table_addr_v4plus
            self._get_prop_size = self._get_prop_size_v4plus
            self._get_prop_size_from_addr = self._get_prop_size_from_addr_v4plus
            self._prepare_routine = self._prepare_routine_v5plus
            self._not_impl = self._not_v5plus
            self._pop_impl = self._pop_v5plus
            self._show_status2 = self._show_status2_v5plus

    def _unpack_addr_v123(self, addr, usage=0):
        return 2 * addr

    def _unpack_addr_v45(self, addr, usage=0):
        return 4 * addr

    def _unpack_addr_v67(self, addr, usage=0):
        if usage == 0:
            return 4 * addr + 8 * self.header.routines
        else:
            return 4 * addr + 8 * self.header.strings

    def _unpack_addr_v8(self, addr, usage=0):
        return 8 * addr

    def _get_obj_parent_v123(self, obj):
        return self.mem[obj + 4]

    def _get_obj_parent_v4plus(self, obj):
        return (self.mem[obj + 6] << 8) + self.mem[obj + 7]

    def _get_obj_sibling_v123(self, obj):
        return self.mem[obj + 5]

    def _get_obj_sibling_v4plus(self, obj):
        return (self.mem[obj + 8] << 8) + self.mem[obj + 9]

    def _get_obj_child_v123(self, obj):
        return self.mem[obj + 6]

    def _get_obj_child_v4plus(self, obj):
        return (self.mem[obj + 10] << 8) + self.mem[obj + 11]

    def _get_prop_table_addr_v123(self, obj):
        return (self.mem[obj + 7] << 8) + self.mem[obj + 8]

    def _get_prop_table_addr_v4plus(self, obj):
        return (self.mem[obj + 12] << 8) + self.mem[obj + 13]

    def _get_prop_size_v123(self, prop_byte, prop_num):
        nob = ((prop_byte - prop_num) // 32) + 1
        return nob

    def _get_prop_size_v4plus(self, prop_byte, mem, prop_addr):
        if (prop_byte & 0x80) == 0x80:
            size = mem[prop_addr + 1] & 0x3F
            if size == 0:
                size = 64
            return size
        elif (prop_byte & 0x40) == 0x40:
            return 2
        else:
            return 1

    def _get_prop_size_from_addr_v123(self, prop_addr):
        prop_num = self.mem[prop_addr] % 32
        nob = ((self.mem[prop_addr] - prop_num) // 32) + 1
        return nob

    def _get_prop_size_from_addr_v4plus(self, prop_addr):
        prop_byte = self.mem[prop_addr]
        if (prop_byte & 128) == 128:
            nob = prop_byte & 63
            if nob == 0:
                nob = 64
            return nob
        elif (prop_byte & 64) == 64:
            return 2
        else:
            return 1

    def _prepare_routine_v1234(self, r: int, argv: list, lenargv: int):
        usage = 0
        if self.zver < 4:
            self.pc = 2 * r
        elif self.zver < 6:
            self.pc = 4 * r
        elif self.zver < 8:
            if usage == 0:
                self.pc = 4 * r + 8 * self.header.routines
            else:
                self.pc = 4 * r + 8 * self.header.strings
        else:
            self.pc = 8 * r

        if self.pc > self.header.length_of_file:
            exit("Call out of bounds!")

        stack = self.stack
        mem = self.mem
        stack.queue = [0] * 1000
        stack.queuepos = 0
        stack.queuemaxpos = 1000
        stack.local_vars_num = mem[self.pc]
        stack.local_vars = [0] * stack.local_vars_num
        self.pc = self.pc + 1
        if stack.local_vars_num > 0:
            if lenargv <= stack.local_vars_num:
                stack.local_vars[0:lenargv] = argv[0:lenargv]
            else:
                stack.local_vars[0 : stack.local_vars_num] = argv[
                    0 : stack.local_vars_num
                ]
            if self.zver < 5:
                self.pc += 2 * lenargv
                while lenargv < stack.local_vars_num:
                    stack.local_vars[lenargv] = (mem[self.pc] << 8) + mem[self.pc + 1]
                    lenargv += 1
                    self.pc += 2

    def _prepare_routine_v5plus(self, r: int, argv: list, lenargv: int):
        usage = 0
        if self.zver < 4:
            self.pc = 2 * r
        elif self.zver < 6:
            self.pc = 4 * r
        elif self.zver < 8:
            if usage == 0:
                self.pc = 4 * r + 8 * self.header.routines
            else:
                self.pc = 4 * r + 8 * self.header.strings
        else:
            self.pc = 8 * r

        if self.pc > self.header.length_of_file:
            exit("Call out of bounds!")

        stack = self.stack
        mem = self.mem
        stack.queue = [0] * 1000
        stack.queuepos = 0
        stack.queuemaxpos = 1000
        stack.local_vars_num = mem[self.pc]
        stack.local_vars = [0] * stack.local_vars_num
        self.pc = self.pc + 1
        if stack.local_vars_num > 0:
            if lenargv <= stack.local_vars_num:
                stack.local_vars[0:lenargv] = argv[0:lenargv]
            else:
                stack.local_vars[0 : stack.local_vars_num] = argv[
                    0 : stack.local_vars_num
                ]

    def _not_v1234(self, pc: int, ops: list):
        r = ops[0] ^ 0xFFFF
        self._zstore(r, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: not {ops[0 : self.numops]}", 2
            )

    def _not_v5plus(self, pc: int, ops: list):
        self._call_1n(pc, ops)

    def _pop_v1234(self, pc: int):
        self.stack.pop()
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: pop", 2)

    def _pop_v5plus(self, pc: int):
        self._catch()

    def _show_status2_v1234(self):
        objnum = (self.mem[self.header.global_variables_table] << 8) + self.mem[
            self.header.global_variables_table + 1
        ]
        obj = self._find_object(objnum)
        prop_addr = self._get_prop_table_addr(obj)
        nob = 2 * self.mem[prop_addr]
        buf = []
        for i in range(nob):
            buf.append(self.mem[prop_addr + i + 1])
        text = decode_text(buf)

        score_game = False
        if self.zver < 3:
            score_game = True
        else:
            if self.header.status_line_type == 0:
                score_game = True
        if score_game:
            score = (
                self.mem[self.header.global_variables_table + 2] << 8
            ) + self.mem[self.header.global_variables_table + 3]
            turns = (
                self.mem[self.header.global_variables_table + 4] << 8
            ) + self.mem[self.header.global_variables_table + 5]
            self.output.print_status(text, f"Score: {score} Turns: {turns}")
        else:
            hour = (
                self.mem[self.header.global_variables_table + 2] << 8
            ) + self.mem[self.header.global_variables_table + 3]
            mins = (
                self.mem[self.header.global_variables_table + 4] << 8
            ) + self.mem[self.header.global_variables_table + 5]
            if mins < 10:
                self.output.print_status(text, f"{hour}:0{mins}")
            else:
                self.output.print_status(text, f"{hour}:{mins}")

    def _show_status2_v5plus(self):
        objnum = (self.mem[self.header.global_variables_table] << 8) + self.mem[
            self.header.global_variables_table + 1
        ]
        obj = self._find_object(objnum)
        prop_addr = self._get_prop_table_addr(obj)
        nob = 2 * self.mem[prop_addr]
        buf = []
        for i in range(nob):
            buf.append(self.mem[prop_addr + i + 1])
        text = decode_text(buf)

        score_game = False
        if self.zver < 3:
            score_game = True
        else:
            if self.header.status_line_type == 0:
                score_game = True
        if score_game:
            score = (
                self.mem[self.header.global_variables_table + 2] << 8
            ) + self.mem[self.header.global_variables_table + 3]
            turns = (
                self.mem[self.header.global_variables_table + 4] << 8
            ) + self.mem[self.header.global_variables_table + 5]
            self.output.print_status(text, f"Score: {score} Turns: {turns}")
        else:
            hour = (
                self.mem[self.header.global_variables_table + 2] << 8
            ) + self.mem[self.header.global_variables_table + 3]
            mins = (
                self.mem[self.header.global_variables_table + 4] << 8
            ) + self.mem[self.header.global_variables_table + 5]
            if mins < 10:
                self.output.print_status(text, f"{hour}:0{mins}")
            else:
                self.output.print_status(text, f"{hour}:{mins}")

    def _read_operands_short_1op(self):
        if (self.mem[self.pc] & 48) == 0:
            self.pc += 1
            self.ops[0] = (self.mem[self.pc] << 8) + self.mem[self.pc + 1]
            self.pc += 2
        elif (self.mem[self.pc] & 48) == 16:
            self.pc += 1
            self.ops[0] = self.mem[self.pc]
            self.pc += 1
        else:
            self.pc += 1
            if self.mem[self.pc] == 0:
                self.ops[0] = self.stack.pop()
            elif self.mem[self.pc] < 0x10:
                self.ops[0] = self.stack.local_vars[self.mem[self.pc] - 1]
            else:
                addr = self.header.global_variables_table + (self.mem[self.pc] - 16) * 2
                b1 = self.mem[addr]
                b2 = self.mem[addr + 1]
                self.ops[0] = (b1 << 8) + b2
            self.pc += 1
        self.numops = 1

    def _read_operands_var_2op(self):
        self.pc = self.pc + 1
        num = 0
        mask = 192
        type_byte = self.mem[self.pc]
        self.pc = self.pc + 1
        for i in range(4):
            optype = (type_byte & mask) >> (3 - i) * 2
            if optype == 0:
                self.ops[num] = (self.mem[self.pc] << 8) + self.mem[self.pc + 1]
                num += 1
                self.pc = self.pc + 2
            elif optype == 1:
                self.ops[num] = self.mem[self.pc]
                num += 1
                self.pc = self.pc + 1
            elif optype == 2:
                if self.mem[self.pc] == 0:
                    self.ops[num] = self.stack.pop()
                    num += 1
                elif self.mem[self.pc] < 0x10:
                    self.ops[num] = self.stack.local_vars[self.mem[self.pc] - 1]
                    num += 1
                else:
                    b1 = self.mem[
                        self.header.global_variables_table
                        + (self.mem[self.pc] - 16) * 2
                    ]
                    b2 = self.mem[
                        self.header.global_variables_table
                        + (self.mem[self.pc] - 16) * 2
                        + 1
                    ]
                    self.ops[num] = (b1 << 8) + b2
                    num += 1
                self.pc = self.pc + 1
            else:
                pass
            mask = mask >> 2
        self.numops = num

    def _read_operands_var_2op2(self):
        self.pc = self.pc + 1
        num = 0
        mask = 192
        type_byte = self.mem[self.pc]
        type_byte2 = self.mem[self.pc + 1]
        self.pc = self.pc + 2
        for i in range(4):
            optype = (type_byte & mask) >> (3 - i) * 2
            if optype == 0:
                self.ops[num] = (self.mem[self.pc] << 8) + self.mem[self.pc + 1]
                num += 1
                self.pc = self.pc + 2
            elif optype == 1:
                self.ops[num] = self.mem[self.pc]
                num += 1
                self.pc = self.pc + 1
            elif optype == 2:
                if self.mem[self.pc] == 0:
                    self.ops[num] = self.stack.pop()
                    num += 1
                elif self.mem[self.pc] < 0x10:
                    self.ops[num] = self.stack.local_vars[self.mem[self.pc] - 1]
                    num += 1
                else:
                    b1 = self.mem[
                        self.header.global_variables_table
                        + (self.mem[self.pc] - 16) * 2
                    ]
                    b2 = self.mem[
                        self.header.global_variables_table
                        + (self.mem[self.pc] - 16) * 2
                        + 1
                    ]
                    self.ops[num] = (b1 << 8) + b2
                    num += 1
                self.pc = self.pc + 1
            else:
                pass
            mask = mask >> 2
        mask = 192
        for i in range(4):
            optype = (type_byte2 & mask) >> (3 - i) * 2
            if optype == 0:
                self.ops[num] = (self.mem[self.pc] << 8) + self.mem[self.pc + 1]
                num += 1
                self.pc = self.pc + 2
            elif optype == 1:
                self.ops[num] = self.mem[self.pc]
                num += 1
                self.pc = self.pc + 1
            elif optype == 2:
                if self.mem[self.pc] == 0:
                    self.ops[num] = self.stack.pop()
                    num += 1
                elif self.mem[self.pc] < 0x10:
                    self.ops[num] = self.stack.local_vars[self.mem[self.pc] - 1]
                    num += 1
                else:
                    b1 = self.mem[
                        self.header.global_variables_table
                        + (self.mem[self.pc] - 16) * 2
                    ]
                    b2 = self.mem[
                        self.header.global_variables_table
                        + (self.mem[self.pc] - 16) * 2
                        + 1
                    ]
                    self.ops[num] = (b1 << 8) + b2
                    num += 1
                self.pc = self.pc + 1
            else:
                pass
            mask = mask >> 2
        self.numops = num

    def _read_operands_long_2op(self):
        code = self.mem[self.pc]
        self.pc += 1
        code2 = self.mem[self.pc]
        if (code & 64) == 0:
            self.ops[0] = code2
        else:
            if code2 == 0:
                self.ops[0] = self.stack.pop()
            elif code2 < 0x10:
                self.ops[0] = self.stack.local_vars[code2 - 1]
            else:
                pos = self.header.global_variables_table + (code2 - 16) * 2
                val = self.mem[pos] << 8
                val += self.mem[pos + 1]
                self.ops[0] = val
        self.pc += 1
        code2 = self.mem[self.pc]
        if (code & 32) == 0:
            self.ops[1] = code2
        else:
            if code2 == 0:
                self.ops[1] = self.stack.pop()
            elif code2 < 0x10:
                self.ops[1] = self.stack.local_vars[code2 - 1]
            else:
                pos = self.header.global_variables_table + (code2 - 16) * 2
                val = self.mem[pos] << 8
                val += self.mem[pos + 1]
                self.ops[1] = val
        self.pc += 1
        self.numops = 2

    def _zstore(self, value: int, where: int):
        if where == 0:
            self.stack.push(value)
        elif where < 16:
            self.stack.local_vars[where - 1] = value
        elif where < 256:
            addr = self.header.global_variables_table + 2 * where - 32
            self.mem[addr] = value >> 8
            self.mem[addr + 1] = value & 0xFF
        else:
            self.mem[where] = value >> 8
            self.mem[where + 1] = value & 0xFF

    def _i2s(self, value: int):
        if value < 0:
            value = 0x10000 + value
        if value > 0xFFFF:
            return value % 0x10000
        elif value >= 0:
            return value
        elif value >= 0x8000:
            return 0x10000 - value
        else:
            return (-value) % 0x10000

    def _s2i(self, value: int):
        if value > 0x7FFF:
            return -(0x10000 - value)
        else:
            return value

    def _inc2(self, var):
        if var == 0:
            tmp = self.stack.pop() + 1
            if tmp == 0x10000:
                tmp = 0
            self.stack.push(tmp)
            return tmp
        elif var < 0x10:
            tmp = self.stack.local_vars[var - 1] + 1
            if tmp == 0x10000:
                tmp = 0
            self.stack.local_vars[var - 1] = tmp
            return tmp
        else:
            b1 = self.mem[self.header.global_variables_table + (var - 16) * 2]
            b2 = self.mem[self.header.global_variables_table + (var - 16) * 2 + 1]
            tmp = (b1 << 8) + b2 + 1
            if tmp == 0x10000:
                tmp = 0
            self.mem[self.header.global_variables_table + (var - 16) * 2] = tmp >> 8
            self.mem[self.header.global_variables_table + (var - 16) * 2 + 1] = (
                tmp & 0xFF
            )
            return tmp

    def _dec2(self, var):
        if var == 0:
            tmp = self.stack.pop() - 1
            if tmp == -1:
                tmp = 0xFFFF
            self.stack.push(tmp)
            return tmp
        elif var < 0x10:
            tmp = self.stack.local_vars[var - 1] - 1
            if tmp == -1:
                tmp = 0xFFFF
            self.stack.local_vars[var - 1] = tmp
            return tmp
        else:
            b1 = self.mem[self.header.global_variables_table + (var - 16) * 2]
            b2 = self.mem[self.header.global_variables_table + (var - 16) * 2 + 1]
            tmp = (b1 << 8) + b2 - 1
            if tmp == -1:
                tmp = 0xFFFF
            self.mem[self.header.global_variables_table + (var - 16) * 2] = tmp >> 8
            self.mem[self.header.global_variables_table + (var - 16) * 2 + 1] = (
                tmp & 0xFF
            )
            return tmp

    def _find_object(self, value: int):
        if self.zver < 4:
            base = self.header.obj_table
            d = base + (31 * 2)
            obj_details = (self.mem[d + 7] << 8) + self.mem[d + 8]
            d = d + (value - 1) * 9
            if d < obj_details:
                return d
            else:
                exit("Couldn't find object")
        else:
            base = self.header.obj_table
            d = base + (63 * 2)
            obj_details = (self.mem[d + 12] << 8) + self.mem[d + 13]
            d = d + (value - 1) * 14
            if d < obj_details:
                return d
            else:
                exit("Couldn't find object")

    def _find_prop(self, table_addr: int, prop: int):
        l = self.mem[table_addr]
        a = table_addr + 1
        i = 0
        text = []
        while i < l:
            text.append(self.mem[a])
            a = a + 1
            text.append(self.mem[a])
            a = a + 1
            i = i + 1
        p = table_addr + self.mem[table_addr] * 2 + 1
        if self.zver < 4:
            while (self.mem[p] % 32) > prop:
                p = p + (self.mem[p] // 32) + 2
            if (self.mem[p] % 32) == prop:
                return p
            else:
                return 0
        else:
            while (self.mem[p] & 0x3F) > prop:
                if (self.mem[p] & 0x80) != 0:
                    p = p + 1
                    num = self.mem[p] & 0x3F
                    if num == 0:
                        num = 64
                    p = p + num + 1
                elif (self.mem[p] & 0x40) != 0:
                    p = p + 3
                else:
                    p = p + 2
            if (self.mem[p] & 0x3F) == prop:
                return p
            else:
                return 0

    def branch(self, condition: bool):
        if (self.mem[self.pc] & 64) == 64:
            offset = self.mem[self.pc] & 63
            gf = 1
        else:
            if self.mem[self.pc] & 32 == 32:
                offset = (
                    ((self.mem[self.pc] | 0xC0) << 8) + self.mem[self.pc + 1] - 65536
                )
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = "True"
        if (self.mem[self.pc] & 128) == 128:
            if condition:
                if offset == 0:
                    self._return(0)
                elif offset == 1:
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        else:
            jif = "False"
            if not (condition):
                if offset == 0:
                    self._return(0)
                elif offset == 1:
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        return [jif, offset]

    def _return(self, value: int):
        stack = self.stack
        stack.pop_frame()
        data = stack.pop_frame()
        prev_pc, return_var, self.intr, self.intr_data = data
        stack.pop_eval_stack()
        stack.pop_local_vars()
        if return_var != -1:
            self._zstore(value, return_var)
        self.last_return = value
        self.pc = prev_pc

    def _routine(self, r, argv, lenargv, res, intr_on_return=0):
        data = [self.pc, res, intr_on_return, self.intr_data]
        self.stack.push_local_vars()
        self.stack.push_eval_stack()
        self.stack.push_frame(data)
        self.stack.push_frame(lenargv)
        self._prepare_routine(r, argv, lenargv)

    def _catch(self):
        pc = self.pc
        stack = self.stack
        return_var = self.mem[self.pc + 1]
        stack.push_eval_stack()
        stack.push_local_vars()
        stack_frame_id = stack.framespos
        self._zstore(stack_frame_id, return_var)
        self.pc += 2
        if self.plugin.level >= 2:
            self.plugin.debug_print(f"{format(pc, 'X')}: catch", 2)

    def _call_1n(self, pc: int, ops: list):
        argv = []
        addr = ops[0]
        return_addr = -1
        self._routine(addr, argv, 0, return_addr)
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: call_1n {ops[0 : self.numops]}", 2
            )

    def command(self):
        value = self.mem[self.pc]
        if value == 0xBE:
            self.pc += 1
            code = self.mem[self.pc]
            ext_key = 0xBE00 | code
            if ext_key in self.command_dict:
                self.command_dict[ext_key]()
            else:
                self.command_dict[ext_key] = self.text[code]
                self.text[code]()
        else:
            try:
                cmd = self.command_dict[value]
                cmd()
            except KeyError:
                if value < 0x80:
                    code = value & 31
                    if value == 0:
                        exit("Invalid opcode!")
                    self.command_dict[value] = self.t2op[code]
                    self.t2op[code]()
                elif value < 0xB0:
                    code = (value & 15) + 128
                    self.command_dict[value] = self.t1op[code]
                    self.t1op[code]()
                elif value < 0xC0:
                    code = (value & 15) + 176
                    self.command_dict[value] = self.t0op[code]
                    self.t0op[code]()
                elif value < 0xE0:
                    code = value & 31
                    self.command_dict[value] = self.t2op[code]
                    self.t2op[code]()
                else:
                    code = (value & 31) + 224
                    self.command_dict[value] = self.tvar[code]
                    self.tvar[code]()

    def start(self):
        t0op = self.t0op
        t1op = self.t1op
        t2op = self.t2op
        text = self.text
        tvar = self.tvar
        cmddict = self.command_dict
        while self.intr == 0:
            value = self.mem[self.pc]
            if value == 0xBE:
                self.pc += 1
                code = self.mem[self.pc]
                ext_key = 0xBE00 | code
                if ext_key in cmddict:
                    cmddict[ext_key]()
                else:
                    cmddict[ext_key] = text[code]
                    text[code]()
            else:
                try:
                    cmd = cmddict[value]
                    cmd()
                except KeyError:
                    if value < 0x80:
                        code = value & 31
                        if value == 0:
                            exit("Invalid opcode!")
                        cmddict[value] = t2op[code]
                        t2op[code]()
                    elif value < 0xB0:
                        code = (value & 15) + 128
                        cmddict[value] = t1op[code]
                        t1op[code]()
                    elif value < 0xC0:
                        code = (value & 15) + 176
                        cmddict[value] = t0op[code]
                        t0op[code]()
                    elif value < 0xE0:
                        code = value & 31
                        cmddict[value] = t2op[code]
                        t2op[code]()
                    else:
                        code = (value & 31) + 224
                        cmddict[value] = tvar[code]
                        tvar[code]()

    def start6(self):
        print((self.pc))
        self._prepare_routine(self.pc, [], 0, 0)
        print((self.pc))

    def got_char(self, char):
        self._zstore(char, self.mem[self.pc])
        self.pc += 1


Container.register("ZCpuBase", ZCpuBase)
