# -*- coding: utf-8

from ztext import *
from stack import ZStack
from zrandom import ZRandom

import sys

__author__="Theofilos Intzoglou"
__date__ ="$24 Ιουν 2009 4:21:45 πμ$"

class ZCpu:
    # @type header ZHeader
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

    def __init__(self,m,h,o,p):
        self.mem = m
        self.header = h
        self.output = o
        self.plugin = p
        self.pc = self.header.pc()
        self.plugin.debugprint("Starting PC: {0}".format(self.pc), 1)
        self.zver = self.header.version()
        self.stack = ZStack()
        self.random = ZRandom()
        self.t2op = dict({1:self._je,
                     2:self._jl,
                     3:self._jg,
                     4:self._dec_chk,
                     5:self._inc_chk,
                     6:self._jin,
                     7:self._test,
                     8:self._or,
                     9:self._and,
                     10:self._test_attr,
                     11:self._set_attr,
                     12:self._clear_attr,
                     13:self._store,
                     14:self._insert_obj,
                     15:self._loadw,
                     16:self._loadb,
                     17:self._get_prop,
                     18:self._get_prop_addr,
                     19:self._get_next_prop,
                     20:self._add,
                     21:self._sub,
                     22:self._mul,
                     23:self._div,
                     24:self._mod,
                     25:self._call_2s,
                     26:self._call_2n,
                     27:self._set_colour,
                     28:self._throw})
        self.t1op = dict({128:self._jz,
                     129:self._get_sibling,
                     130:self._get_child,
                     131:self._get_parent,
                     132:self._get_prop_len,
                     133:self._inc,
                     134:self._dec,
                     135:self._print_addr,
                     136:self._call_1s,
                     137:self._remove_obj,
                     138:self._print_obj,
                     139:self._ret,
                     140:self._jump,
                     141:self._print_paddr,
                     142:self._load,
                     143:self._not})
        self.t0op = dict({176:self._rtrue,
                     177:self._rfalse,
                     178:self._print,
                     179:self._print_ret,
                     180:self._nop,
                     181:self._save,
                     182:self._restore,
                     183:self._restart,
                     184:self._ret_popped,
                     185:self._pop,
                     186:self._quit,
                     187:self._new_line,
                     188:self._show_status,
                     189:self._verify,
                     190:None,
                     191:self._piracy})
        self.tvar = dict({224:self._call,
                     225:self._storew,
                     226:self._storeb,
                     227:self._put_prop,
                     228:self._sread,
                     229:self._print_char,
                     230:self._print_num,
                     231:self._random,
                     232:self._push,
                     233:self._pull,
                     234:self._split_window,
                     235:self._set_window,
                     236:self._call_vs2,
                     237:self._erase_window,
                     238:self._erase_line,
                     239:self._set_cursor,
                     240:self._get_cursor,
                     241:self._set_text_style,
                     242:self._buffer_mode,
                     243:self._output_stream,
                     244:self._input_stream,
                     245:self._sound_effect,
                     246:self._read_char,
                     247:self._scan_table,
                     248:self._not_var,
                     249:self._call_vn,
                     250:self._call_vn2,
                     251:self._tokenise,
                     252:self._encode_text,
                     253:self._copy_table,
                     254:self._print_table,
                     255:self._check_arg_count})
        self.text = dict({0:self._save_ext,
                     1:self._restore_ext,
                     2:self._log_shift,
                     3:self._art_shift,
                     4:self._set_font,
                     5:self._draw_picture,
                     6:self._picture_data,
                     7:self._erase_picture,
                     8:self._set_margins,
                     9:self._save_undo,
                     10:self._restore_undo,
                     11:self._print_unicode,
                     12:self._check_unicode,
                     13:None,
                     14:None,
                     15:None,
                     16:self._move_window,
                     17:self._window_size,
                     18:self._window_style,
                     19:self._get_wind_prop,
                     20:self._scroll_window,
                     21:self._pop_stack,
                     22:self._read_mouse,
                     23:self._mouse_window,
                     24:self._push_stack,
                     25:self._put_wind_prop,
                     26:self._print_form,
                     27:self._make_menu,
                     28:self._picture_table})

    def command(self):
        if self.mem[self.pc] < 0x80: # LONG 2OP
            code = (self.mem[self.pc] & 31)
            if self.mem[self.pc] == 0:
                sys.exit("Invalid opcode!")
            self.t2op[code]()
        elif self.mem[self.pc] < 0xb0: # SHORT 1OP
            code = (self.mem[self.pc] & 15) + 128
            self.t1op[code]()
        elif (self.mem[self.pc] < 0xc0) and (self.mem[self.pc] != 0xbe): # SHORT 0OP
            code = (self.mem[self.pc] & 15) + 176
            self.t0op[code]()
        elif self.mem[self.pc] == 0xbe: # EXTENDED VAR
            self.pc += 1
            code = self.mem[self.pc]
            self.text[code]()
        elif self.mem[self.pc] < 0xe0: # VARIABLE 2OP
            code = self.mem[self.pc] & 31
            self.t2op[code]()
        else:
            code = (self.mem[self.pc] & 31) + 224
            self.tvar[code]()

    def _je(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(ops[0]) == self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(ops[0]) == self._s2i(ops[j]))
                    j += 1
                if r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        else:
            jif = 'False'
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(ops[0]) == self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(ops[0]) == self._s2i(ops[j]))
                    j += 1
                if not r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: je {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _jl(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(ops[0]) < self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(ops[0]) < self._s2i(ops[j]))
                    j += 1
                if r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        else:
            jif = 'False'
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(ops[0]) < self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(ops[0]) < self._s2i(ops[j]))
                    j += 1
                if not r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: jl {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _jg(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(ops[0]) > self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(ops[0]) > self._s2i(ops[j]))
                    j += 1
                if r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        else:
            jif = 'False'
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(ops[0]) > self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(ops[0]) > self._s2i(ops[j]))
                    j += 1
                if not r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: jg {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _dec_chk(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        val = self._dec2(ops[0])
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(val) < self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(val) < self._s2i(ops[j]))
                    j += 1
                if r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        else:
            jif = 'False'
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(val) >= self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(val) >= self._s2i(ops[j]))
                    j += 1
                if not r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: dec_chk {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _inc_chk(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        val = self._inc2(ops[0])
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(val) > self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(val) > self._s2i(ops[j]))
                    j += 1
                if r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        else:
            jif = 'False'
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                j = 2
                r = self._s2i(val) <= self._s2i(ops[1])
                while j < n:
                    r = r or (self._s2i(val) <= self._s2i(ops[j]))
                    j += 1
                if not r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: inc_chk {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _jin(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        obj = self._find_object(ops[0])
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            if self.zver < 4:
                b = self.mem[obj+4]
            else:
                b = (self.mem[obj+6] << 8) + self.mem[obj+7]
            if b == ops[1]:
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        else:
            jif = 'False'
            if self.zver < 4:
                b = self.mem[obj+4]
            else:
                b = (self.mem[obj+6] << 8) + self.mem[obj+7]
            if b <> ops[1]:
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: jin {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _test(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                r = ((ops[0] & ops[1]) == ops[1])
                if r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        else:
            jif = 'False'
            n = len(ops)
            if n == 1: # Nothing to compare
                self.pc = self.pc + gf
            else:
                r = ((ops[0] & ops[1]) == ops[1])
                if not r: # Jump to label
                    if offset == 0: # Return false
                        self._return(0)
                    elif offset == 1: # Return true
                        self._return(1)
                    else:
                        self.pc = self.pc + gf + offset - 2
                else:
                    self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: test {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _or(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        res = ops[0] | ops[1]
        self._zstore(res, self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: or {1}'.format(format(pc,'X'),ops), 2 )

    def _and(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        res = ops[0] & ops[1]
        self._zstore(res, self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: and {1}'.format(format(pc,'X'),ops), 2 )

    def _test_attr(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        obj = self._find_object(ops[0])
        #print "Obj:",ops[0],"addr:",format(obj,"X")
        if self.zver < 4:
            b = (self.mem[obj] << 24) + (self.mem[obj + 1] << 16) + (self.mem[obj + 2] << 8) + self.mem[obj + 3]
            #print "b:",format(b,"X")
            mask = 1 << (31 - ops[1])
            #print "mask:",format(mask,"X")
        else:
            b = (self.mem[obj] << 40) + (self.mem[obj + 1] << 32) + (self.mem[obj + 2] << 24) + (self.mem[obj + 3] << 16) + (self.mem[obj + 4] << 8) + self.mem[obj + 5]
            #print "b:",format(b,"X")
            mask = 1 << (47 - ops[1])
            #print "mask:",format(mask,"X")
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            if (b & mask) == mask: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        else:
            jif = 'False'
            if (b & mask) == 0: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: test_attr {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _set_attr(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: set_attr {1}'.format(format(pc,'X'),ops), 2 )
        if ops[0] == 0:
            print "set_attr: Cannot set attr of object 0!"
            return
        obj = self._find_object(ops[0])
        if self.zver < 4:
            b = (self.mem[obj] << 24) + (self.mem[obj + 1] << 16) + (self.mem[obj + 2] << 8) + self.mem[obj + 3]
            mask = 1 << (31 - ops[1])
            b |= mask
            self.mem[obj] = b >> 24
            self.mem[obj + 1] = (b & 0xff0000) >> 16
            self.mem[obj + 2] = (b & 0xff00) >> 8
            self.mem[obj + 3] = b & 0xff
        else:
            b = (self.mem[obj] << 40) + (self.mem[obj + 1] << 32) + (self.mem[obj + 2] << 24) + (self.mem[obj + 3] << 16) + (self.mem[obj + 4] << 8) + self.mem[obj + 5]
            mask = 1 << (47 - ops[1])
            b |= mask
            self.mem[obj] = b >> 40
            self.mem[obj + 1] = (b & 0xff00000000) >> 32
            self.mem[obj + 2] = (b & 0xff000000) >> 24
            self.mem[obj + 3] = (b & 0xff0000) >> 16
            self.mem[obj + 4] = (b & 0xff00) >> 8
            self.mem[obj + 5] = b & 0xff

    def _clear_attr(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: clear_attr {1}'.format(format(pc,'X'),ops), 2 )
        if ops[0] == 0:
            print "clear_attr: Cannot clear attr of object 0!"
            return
        obj = self._find_object(ops[0])
        if self.zver < 4:
            b = (self.mem[obj] << 24) + (self.mem[obj + 1] << 16) + (self.mem[obj + 2] << 8) + self.mem[obj + 3]
            mask = 1 << (31 - ops[1])
            if (b & mask) <> 0:
                b ^= mask
                self.mem[obj] = b >> 24
                self.mem[obj + 1] = (b & 0xff0000) >> 16
                self.mem[obj + 2] = (b & 0xff00) >> 8
                self.mem[obj + 3] = b & 0xff
        else:
            b = (self.mem[obj] << 40) + (self.mem[obj + 1] << 32) + (self.mem[obj + 2] << 24) + (self.mem[obj + 3] << 16) + (self.mem[obj + 4] << 8) + self.mem[obj + 5]
            mask = 1 << (47 - ops[1])
            if (b & mask) <> 0:
                b ^= mask
                self.mem[obj] = b >> 40
                self.mem[obj + 1] = (b & 0xff00000000) >> 32
                self.mem[obj + 2] = (b & 0xff000000) >> 24
                self.mem[obj + 3] = (b & 0xff0000) >> 16
                self.mem[obj + 4] = (b & 0xff00) >> 8
                self.mem[obj + 5] = b & 0xff

    def _store(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if ops[0]==0: # store should not add new value to stack
            self.stack.pop() # so we pop the top value
        self._zstore(ops[1], ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: store {1}'.format(format(pc,'X'),ops), 2 )

    def _insert_obj(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: insert_obj {1}'.format(format(pc,'X'),ops), 2 )
        if ops[1] == 0 or ops[0] == 0:
            print "insert_obj: Cannot use 0 as source or destination!"
            return
        d = self._find_object(ops[1])
        o = self._find_object(ops[0])
        if self.zver < 4:
            dchild = self.mem[d+6]
            self.mem[d+6] = ops[0] # Set child of d
            if self.mem[o+4] <> 0: # If the object to move has a parent
                f = self._find_object(self.mem[o+4]) # Find the addr of parent
                if self.mem[f+6] == ops[0]: # If the object to move is the first child
                    self.mem[f+6] = self.mem[o+5]
                    #print "Father", self.mem[o+4], "now has as child", self.mem[o+5]
                else:
                    t = self._find_object(self.mem[f+6]) # Get the first child of the father
                    #print "^^", self.mem[t+5], "^^"
                    #tn = self.mem[f+6]
                    while (self.mem[t+5] <> ops[0]): # While the object t isn't a sibling of o
                        #tn = self.mem[t+5]
                        t = self._find_object(self.mem[t+5])
                    #print "Got ", self.mem[o+5], "as sibling of", tn
                    self.mem[t+5] = self.mem[o+5]
            self.mem[o+4] = ops[1] # Set father of o
            self.mem[o+5] = dchild # Set sibling of o
            #print "Sibling of", ops[0], "is", dchild
        else:
            n = (self.mem[o+6] << 8) + self.mem[o+7]
            if n <> ops[1]: # If the parent of o isn't already d
                dchild_p1 = self.mem[d+10]
                dchild_p2 = self.mem[d+11]
                self.mem[d+10] = ops[0] >> 8 # Set child of d
                self.mem[d+11] = ops[0] & 0xff
                if n <> 0: # If the object to move has a parent
                    f = self._find_object(n) # Find the addr of parent
                    cn = (self.mem[f+10] << 8) + self.mem[f+11]
                    if cn == ops[0]: # If the object to move is the first child
                        self.mem[f+10] = self.mem[o+8]
                        self.mem[f+11] = self.mem[o+9]
                        #print "Father", n, "now has as child", ((self.mem[o+8] << 8) + self.mem[o+9])
                    else:
                        t = self._find_object(cn) # Get the first child of the father
                        sn = (self.mem[t+8] << 8) + self.mem[t+9]
                        #print "^^", sn, "^^"
                        #tn = cn
                        while (sn <> ops[0]): # While the object t isn't a sibling of o
                            #tn = sn
                            t = self._find_object(sn)
                            sn = (self.mem[t+8] << 8) + self.mem[t+9]
                        #print "Got ", ((self.mem[o+8] << 8) + self.mem[o+9]), "as sibling of", tn
                        self.mem[t+8] = self.mem[o+8]
                        self.mem[t+9] = self.mem[o+9]
                self.mem[o+6] = ops[1] >> 8 # Set father of o
                self.mem[o+7] = ops[1] & 0xff
                self.mem[o+8] = dchild_p1 # Set sibling of o
                self.mem[o+9] = dchild_p2

    def _loadw(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        return_var = self.mem[self.pc]
        self.pc += 1
        addr = ops[0] + 2 * ops[1]
        data = (self.mem[addr] << 8) + self.mem[addr + 1]
        self._zstore(data, return_var)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: loadw {1}'.format(format(pc,'X'),ops), 2 )

    def _loadb(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        return_var = self.mem[self.pc]
        self.pc += 1
        addr = ops[0] + ops[1]
        data = self.mem[addr]
        self._zstore(data, return_var)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: loadb {1}'.format(format(pc,'X'),ops), 2 )

    def _get_prop(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if ops[0] == 0:
            # Failing gracefully...
            print "get_prop: Can't get property of nothing!"
            self._zstore(0, self.mem[self.pc])
            self.pc += 1
            return
        obj = self._find_object(ops[0])
        if self.zver < 4:
            addr = (self.mem[obj + 7] << 8) + self.mem[obj + 8]
        else:
            addr = (self.mem[obj + 12] << 8) + self.mem[obj + 13]
        prop = self._find_prop(addr, ops[1])
        if prop == 0: # No defined property, try default
            base = self.header.obj_table()
            data = (self.mem[base + ((ops[1] - 1) * 2)] << 8) + self.mem[base + ((ops[1] - 1) * 2) + 1]
        else: # Property found
            if self.zver < 4:
                size = self.mem[prop]
                nob = ((size - ops[1]) / 32) + 1
                #print "Number of bytes:", nob
                if nob == 1:
                    data = self.mem[prop + 1]
                else:
                    data = (self.mem[prop + 1] << 8) + self.mem[prop + 2]
            else:
                if (self.mem[prop] & 0x80) == 0x80: # There is a second size byte
                    size = (self.mem[prop + 1] & 0x3f)
                    if size == 0:
                        size = 64
                    if size == 1:
                        data = self.mem[prop + 2]
                    else:
                        data = (self.mem[prop + 2] << 8) + self.mem[prop + 3]
                elif (self.mem[prop] & 0x40) == 0x40: # Length 2
                    data = (self.mem[prop + 1] << 8) + self.mem[prop + 2]
                else:
                    data = self.mem[prop + 1]
        self._zstore(data, self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: get_prop {1}'.format(format(pc,'X'),ops), 2 )

    def _get_prop_addr(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if ops[0] == 0:
            self.output.prints("** get_prop_addr got 0 as object! **\n")
            prop = 0
            #sys.exit("Can't get property of nothing!")
        else:
            obj = self._find_object(ops[0])
            #print "Obj addr:", obj
            if self.zver < 4:
                addr = (self.mem[obj + 7] << 8) + self.mem[obj + 8]
                prop = self._find_prop(addr, ops[1])
                if prop <> 0:
                    prop += 1
            else:
                addr = (self.mem[obj + 12] << 8) + self.mem[obj + 13]
                prop = self._find_prop(addr, ops[1])
                if prop <> 0:
                    if (self.mem[prop] & 128) == 128:
                        prop += 2
                    else:
                        prop += 1
        self._zstore(prop, self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: get_prop_addr {1}'.format(format(pc,'X'),ops), 2 )

    def _get_next_prop(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: get_next_prop {1}'.format(format(pc,'X'),ops), 2 )
        if ops[0] == 0:
            print "get_next_prop: Can't get property of nothing!"
            self._zstore(0, self.mem[self.pc])
            self.pc += 1
            return
        obj = self._find_object(ops[0])
        #print "Obj addr:", obj
        if ops[1] == 0:
            find_first_value = True
        else:
            find_first_value = False
        if self.zver < 4:
            if find_first_value:
                addr = (self.mem[obj + 7] << 8) + self.mem[obj + 8]
                l = self.mem[addr]
                prop_addr = addr + (2 * l) + 2
                prop = prop_addr % 32
            else:
                addr = (self.mem[obj + 7] << 8) + self.mem[obj + 8]
                prop_addr = self._find_prop(addr, ops[1])
                if prop_addr <> 0: # Property found!
                    nob = (prop_addr // 32) + 1
                    prop_addr += nob + 1
                    prop = prop_addr % 32
                else: # Property not found... :-(
                    sys.exit("No such property!")
        else:
            if find_first_value:
                addr = (self.mem[obj + 12] << 8) + self.mem[obj + 13]
                prop = self.mem[addr] & 0x3f
            else:
                addr = (self.mem[obj + 12] << 8) + self.mem[obj + 13]
                prop_addr = self._find_prop(addr, ops[1])
                if prop_addr <> 0: # Property found!
                    if (self.mem[prop_addr] & 0x80) <> 0: # Top bit is 1 so there is a second byte
                        #print "There is a second byte!"
                        prop_addr += 1
                        num = self.mem[prop_addr] & 0x3f
                        if num == 0:
                            num = 64
                        prop_addr += num + 1
                    elif (self.mem[prop_addr] & 0x40) <> 0: # 6th bit is 1 so there are 2 bytes of data
                        prop_addr += 3
                    else: # Only 1 byte of data
                        prop_addr += 2
                    prop = self.mem[prop_addr] & 0x3f
                else: # Property not found... :-(
                    sys.exit("No such property!")
        self._zstore(prop, self.mem[self.pc])
        self.pc += 1

    def _add(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        result = self._i2s(self._s2i(ops[0]) + self._s2i(ops[1]))
        #print "Result:", result
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: add {1}'.format(format(pc,'X'),ops), 2 )

    def _sub(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        result = self._i2s(self._s2i(ops[0]) - self._s2i(ops[1]))
        #print "Result:", result
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: sub {1}'.format(format(pc,'X'),ops), 2 )

    def _mul(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        result = self._i2s(self._s2i(ops[0]) * self._s2i(ops[1]))
        #print "Result:", result
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: mul {1}'.format(format(pc,'X'),ops), 2 )

    def _div(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if ops[1] == 0: # Division by zero
            print "Divide by zero!"
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
        result = self._i2s(s1*s2*(abs(a)/abs(b)))
        #print "Result:", result
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: div {1}'.format(format(pc,'X'),ops), 2 )

    def _mod(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if ops[1] == 0: # Division by zero
            print "Divide by zero!"
            exit(20)
        a = self._s2i(ops[0])
        b = self._s2i(ops[1])
        if a < 0:
            s1 = -1
        else:
            s1 = 1
        # mod always follows the sign of the first num
        result = self._i2s(s1*(abs(a)%abs(b)))
        #print "Result:", result
        self._zstore(result, self.mem[self.pc])
        self.pc = self.pc + 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: mod {1}'.format(format(pc,'X'),ops), 2 )

    def _call_2s(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        argv = [ops[1]]
        return_addr = self.mem[self.pc]
        self.pc += 1
        self._routine(ops[0],argv,return_addr)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: call_2s {1}'.format(format(pc,'X'),ops), 2 )
            self.plugin.debugprint( '--v', 2 )

    def _call_2n(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        argv = [ops[1]]
        return_addr = -1
        self._routine(ops[0],argv,return_addr)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: call_2n {1}'.format(format(pc,'X'),ops), 2 )
            self.plugin.debugprint( '--v', 2 )

    def _set_colour(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        self.output.set_colour(ops[0],ops[1])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: set_colour {1}'.format(format(pc,'X'),ops), 2 )

    def _throw(self):
        pc = self.pc
        if self.mem[self.pc] >= 0xc0: # Variable 2OP
            ops = self._read_operands_var_2op()
        else: # Long 2OP
            ops = self._read_operands_long_2op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: throw {1}'.format(format(pc,'X'),ops), 2 )
        sys.exit("Not implemented yet!")

    def _jz(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            if ops[0] == 0: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        else:
            jif = 'False'
            if ops[0] <> 0: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: jz {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _get_sibling(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        return_var = self.mem[self.pc]
        self.pc += 1
        #print self.mem[self.pc]
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        #print "Offset -", offset, " Gf -", gf
        obj = self._find_object(ops[0])
        if self.zver < 4:
            sibl = self.mem[obj + 5]
        else:
            sibl = (self.mem[obj + 8] << 8) + self.mem[obj + 9]
        #print "Sibli -", sibl
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            if sibl <> 0: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc += gf
        else:
            jif = 'False'
            if sibl == 0: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc += gf
        self._zstore(sibl, return_var)
        #print self.pc
        #print self.mem[self.pc]
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: get_sibling {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _get_child(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        return_var = self.mem[self.pc]
        self.pc += 1
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        #print "Offset -", offset, " Gf -", gf
        obj = self._find_object(ops[0])
        if self.zver < 4:
            child = self.mem[obj + 6]
        else:
            child = (self.mem[obj + 10] << 8) + self.mem[obj + 11]
        #print "Child:", child
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            if child <> 0: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc += gf
        else:
            jif = 'False'
            if child == 0: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc += gf
        self._zstore(child, return_var)
        #print self.pc
        #print self.mem[self.pc]
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: get_child {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _get_parent(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        obj = self._find_object(ops[0])
        if self.zver < 4:
            self._zstore(self.mem[obj+4], self.mem[self.pc])
            #print "Parent:", self.mem[obj+4]
        else:
            parent = (self.mem[obj+6] << 8) + self.mem[obj+7]
            self._zstore(parent, self.mem[self.pc])
            #print "Parent:", parent
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: get_parent {1}'.format(format(pc,'X'),ops), 2 )

    def _get_prop_len(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        ops[0] = ops[0] - 1
        if self.zver < 4:
            prop_num = self.mem[ops[0]] % 32
            nob = ((self.mem[ops[0]] - prop_num) / 32) + 1
        else:
            if (self.mem[ops[0]] & 128) == 128:
                nob = self.mem[ops[0]] & 63
                if nob == 0:
                    nob = 64
            elif (self.mem[ops[0]] & 64) == 64:
                nob = 2
            else:
                nob = 1
        self._zstore(nob, self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: get_prop_len {1}'.format(format(pc,'X'),ops), 2 )

    def _inc(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        self._inc2(ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: inc {1}'.format(format(pc,'X'),ops), 2 )

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
            #print "Inc --", tmp
            return tmp
        else:
            b1 = self.mem[ self.header.global_table() + (var - 16) * 2 ]
            b2 = self.mem[ self.header.global_table() + (var - 16) * 2 + 1]
            #print "Before:", (b1 << 8) + b2
            tmp = (b1 << 8) + b2 + 1
            if tmp == 0x10000:
                tmp = 0
            #print "After:", tmp
            self.mem[ self.header.global_table() + (var - 16) * 2 ] = tmp >> 8
            self.mem[ self.header.global_table() + (var - 16) * 2 + 1] = tmp & 0xff
            #print "Global var", var - 15, "has now value", tmp
            return tmp

    def _dec(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        self._dec2(ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: dec {1}'.format(format(pc,'X'),ops), 2 )

    def _dec2(self, var):
        if var == 0:
            tmp = self.stack.pop() - 1
            if tmp == -1:
                tmp = 0xffff
            self.stack.push(tmp)
            return tmp
        elif var < 0x10:
            tmp = self.stack.local_vars[var - 1] - 1
            if tmp == -1:
                tmp = 0xffff
            self.stack.local_vars[var - 1] = tmp
            #print "Dec --", tmp
            return tmp
        else:
            b1 = self.mem[ self.header.global_table() + (var - 16) * 2 ]
            b2 = self.mem[ self.header.global_table() + (var - 16) * 2 + 1]
            #print "Before:", (b1 << 8) + b2
            tmp = (b1 << 8) + b2 - 1
            if tmp == -1:
                tmp = 0xffff
            #print "After:", tmp
            self.mem[ self.header.global_table() + (var - 16) * 2 ] = tmp >> 8
            self.mem[ self.header.global_table() + (var - 16) * 2 + 1] = tmp & 0xff
            #print "Global var", var - 15, "has now value", tmp
            return tmp

    def _print_addr(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        uaddr = ops[0]
        #print uaddr
        buf = []
        eot = False
        i = 0
        while not eot:
            if (self.mem[uaddr + i] & 128) == 128:
                eot = True
            buf.append(self.mem[uaddr + i])
            buf.append(self.mem[uaddr + i + 1])
            i += 2
        text = decode_text(buf, self.zver, self.mem, self.header.abbrev_table(), False, self.header.alphabet_table(), 0)
        self.output.prints(text)
        #print text
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: print_addr {1}'.format(format(pc,'X'),ops), 2 )

    def _call_1s(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        argv = []
        return_addr = self.mem[self.pc]
        self.pc += 1
        self._routine(ops[0],argv,return_addr)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: call_1s {1}'.format(format(pc,'X'),ops), 2 )

    def _remove_obj(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: remove_obj {1}'.format(format(pc,'X'),ops), 2 )
        if ops[0] == 0: # We have nothing to do here!
            return
        obj = self._find_object(ops[0])
        if self.zver < 4:
            f = self._find_object(self.mem[obj+4]) # Find the addr of parent
            if self.mem[f+6] == ops[0]: # If the object to move is the first child
                self.mem[f+6] = self.mem[obj+5]
                #print "Father", self.mem[obj+4], "now has as child", self.mem[obj+5]
            else:
                t = self._find_object(self.mem[f+6]) # Get the first child of the father
                #print "^^", self.mem[t+5], "^^"
                while (self.mem[t+5] <> ops[0]): # While the object t isn't a sibling of o
                    t = self._find_object(self.mem[t+5])
                #print "Got ", self.mem[obj+5], "as sibling of", tn
                self.mem[t+5] = self.mem[obj+5]
            self.mem[obj+4] = 0 # Father of obj
            self.mem[obj+5] = 0 # Sibling of obj
        else:
            fn = (self.mem[obj+6] << 8) + self.mem[obj+7]
            if fn != 0:
                f = self._find_object(fn) # Find the addr of parent
                cn = (self.mem[f+10] << 8) + self.mem[f+11]
                if cn == ops[0]: # If the object to move is the first child
                    self.mem[f+10] = self.mem[obj+8]
                    self.mem[f+11] = self.mem[obj+9]
                    #print "Father", (self.mem[obj+6] << 8) + self.mem[obj+7], "now has as child", (self.mem[obj+8] << 8) + self.mem[obj+9]
                else:
                    t = self._find_object(cn) # Get the first child of the father
                    #print "^^", (self.mem[t+8] << 8) + self.mem[t+9], "^^"
                    #tn = cn
                    sn = (self.mem[t+8] << 8) + self.mem[t+9]
                    while (sn <> ops[0]): # While the object t isn't a sibling of o
                        #print fn,sn,ops[0]
                        #tn = sn
                        t = self._find_object(sn)
                        sn = (self.mem[t+8] << 8) + self.mem[t+9]
                    #print "Got ", (self.mem[obj+8] << 8) + self.mem[obj+9], "as sibling of", tn
                    self.mem[t+8] = self.mem[obj+8]
                    self.mem[t+9] = self.mem[obj+9]
            self.mem[obj+6] = 0 # Father of obj
            self.mem[obj+7] = 0
            self.mem[obj+8] = 0 # Sibling of obj
            self.mem[obj+9] = 0

    def _print_obj(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        if (ops[0] < 1) or ((self.zver < 4) and (ops[0] > 255)) or ((self.zver > 3) and (ops[0] > 65535)):
            sys.exit("Invalid object number")
        obj = self._find_object(ops[0])
        if self.zver < 4:
            addr = (self.mem[obj + 7] << 8) + self.mem[obj + 8]
        else:
            addr = (self.mem[obj + 12] << 8) + self.mem[obj + 13]
        length = self.mem[addr]
        #print "Addr:", format(addr, "X"), "Length:", length
        buf = []
        i = 1
        while i < (2 * length):
            buf.append(self.mem[addr + i])
            buf.append(self.mem[addr + i + 1])
            i += 2
        #print buf
        text = decode_text(buf, self.zver, self.mem, self.header.abbrev_table(), False, self.header.alphabet_table(), 0)
        self.output.prints(text)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: print_obj {1}'.format(format(pc,'X'),ops), 2 )

    def _ret(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        self._return(ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: ret {1}'.format(format(pc,'X'),ops), 2 )

    def _return(self, value):
        self.stack.pop_frame() # We don't need the number of args
        self.intr_data = self.stack.pop_frame()
        self.intr = self.stack.pop_frame()
        return_var = self.stack.pop_frame()
        prev_pc = self.stack.pop_frame()
        self.stack.pop_local_vars()
        if return_var <> -1: # If we want the returned value...
            self._zstore(value,return_var)
        self.last_return = value # Keep last value (used in timed input)
        self.pc = prev_pc

    def _jump(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        offset = ops[0] - 2
        if offset > 0x7fff:
            offset = offset - 0x10000
        #print "Jump to offset", offset
        self.pc = self.pc + offset
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: jump {1}'.format(format(pc,'X'),ops), 2 )

    def _print_paddr(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        uaddr = self._unpack_addr(ops[0])
        #print uaddr
        buf = []
        eot = False
        i = 0
        while not eot:
            if (self.mem[uaddr + i] & 128) == 128:
                eot = True
            buf.append(self.mem[uaddr + i])
            buf.append(self.mem[uaddr + i + 1])
            i += 2
        text = decode_text(buf, self.zver, self.mem, self.header.abbrev_table(), False, self.header.alphabet_table(), 0)
        self.output.prints(text)
        #print text
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: print_paddr {1}'.format(format(pc,'X'),ops), 2 )

    def _load(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        if ops[0] == 0:
            data = self.stack.pop() # load shouldn't lose the top value of stack
            self.stack.push(data)
        elif ops[0] < 16:
            data = self.stack.local_vars[ops[0] - 1]
        elif ops[0] < 256:
            data = self.mem[self.header.global_table() + (where - 16) * 2] << 8
            data += self.mem[self.header.global_table() + (where - 16) * 2 + 1]
        else:
            sys.exit("No such variable!!!")
        self._zstore(data, self.pc)
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: load {1}'.format(format(pc,'X'),ops), 2 )

    def _not(self):
        pc = self.pc
        ops = self._read_operands_short_1op()
        if self.zver >= 5:
            #print "This is truly a call_1n"
            self._call_1n(pc,ops)
        else:
            r = ops[0] ^ 0xffff
            self._zstore(r,self.mem[self.pc])
            self.pc += 1
            if (self.plugin.level >= 2):
                self.plugin.debugprint( '{0}: not {1}'.format(format(pc,'X'),ops), 2 )

    def _call_1n(self,pc,ops):
        argv = []
        addr = ops[0]
        return_addr = -1
        self._routine(addr,argv,return_addr)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: call_1n {1}'.format(format(pc,'X'),ops), 2 )

    def _rtrue(self):
        pc = self.pc
        self._return(1)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: rtrue'.format(format(pc,'X')), 2 )

    def _rfalse(self):
        pc = self.pc
        self._return(0)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: rfalse'.format(format(pc,'X')), 2 )

    def _print(self):
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
        #print buf
        text = decode_text(buf, self.zver, self.mem, self.header.abbrev_table(), False, self.header.alphabet_table(), 0)
        #print text
        self.output.prints(text)
        self.pc += i + 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: print "{1}"'.format(format(pc,'X'),text), 2 )

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
        #print buf
        text = decode_text(buf, self.zver, self.mem, self.header.abbrev_table(), False, self.header.alphabet_table(), 0)
        self.output.prints(text + "\n")
        #print text
        self.pc += i + 1
        self._return(1)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: print_ret "{1}"'.format(format(pc,'X'),text), 2 )

    def _nop(self):
        pc = self.pc
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: nop'.format(format(pc,'X')), 2 )

    def _save(self):
        self.plugin.debugprint( ': save', 0 )
        sys.exit("Not implemented yet!")

    def _restore(self):
        self.plugin.debugprint( ': restore', 0 )
        sys.exit("Not implemented yet!")

    def _restart(self):
        pc = self.pc
        self.intr = 3
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: restart'.format(format(pc,'X')), 2 )

    def _ret_popped(self):
        pc = self.pc
        data = self.stack.pop()
        self._return(data)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: ret_popped'.format(format(pc,'X')), 2 )

    def _pop(self):
        pc = self.pc
        if self.zver < 5:
            self.stack.pop()
            self.pc += 1
            if (self.plugin.level >= 2):
                self.plugin.debugprint( '{0}: pop'.format(format(pc,'X')), 2 )
        else:
            #print "actually catch is used!"
            if (self.plugin.level >= 2):
                self.plugin.debugprint( '{0}: catch'.format(format(pc,'X')), 2 )
            self._catch()

    def _catch(self):
        self.stack.push_local_vars()
        self.stack.push_frame(self.pc)
        self.stack.push_frame(self.mem[self.pc])
        sys.exit()

    def _quit(self):
        pc = self.pc
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: quit'.format(format(pc,'X')), 2 )
        self.output.prints('[Press any key to quit]')
        self.intr = 69

    def _new_line(self):
        pc = self.pc
        self.output.new_line()
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: new_line'.format(format(pc,'X')), 2 )

    def _show_status(self):
        pc = self.pc
        self._show_status2()
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: show_status'.format(format(pc,'X')), 2 )

    def _verify(self):
        pc = self.pc
        # Read file
        self.file.seek(0x40)
        if (self.zver < 4):
            max_length = 128 * 1024
        elif (self.zver < 6):
            max_length = 256 * 1024
        elif (self.zver == 6 or self.zver == 8):
            max_length = 512 * 1024
        else:
            max_length = 320 * 1024
        data = self.file.read(max_length)

        # Calculate checksum
        chksum = 0
        i = 0
        l = len(data)
        while i < l:
            chksum += data[i]
        chksum %= 0x10000

        # Check offset
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            if chksum == self.header.checksum(): # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        else:
            jif = 'False'
            if not (chksum == self.header.checksum()): # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: verify {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _piracy(self):
        pc = self.pc
        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            if offset == 0: # Return false
                self._return(0)
            elif offset == 1: # Return true
                self._return(1)
            else:
                self.pc = self.pc + gf + offset - 2
        else:
            jif = 'False'
            self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: piracy {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _call(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        i = 1
        argv = []
        while i < len(ops):
            argv.append(ops[i])
            i += 1
        return_addr = self.mem[self.pc]
        self.pc = self.pc + 1
        self._routine(ops[0],argv,return_addr)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: call {1}'.format(format(pc,'X'),ops), 2 )

    def _storew(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        addr = ops[0] + (2 * ops[1])
        self.mem[addr] = ops[2] >> 8
        self.mem[addr + 1] = ops[2] & 0xff
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: storew {1}'.format(format(pc,'X'),ops), 2 )

    def _storeb(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        addr = ops[0] + ops[1]
        self.mem[addr] = ops[2]
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: storeb {1}'.format(format(pc,'X'),ops), 2 )

    def _put_prop(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if ops[0] == 0:
            exit("Can't put prop to nothing!")
        d = self._find_object(ops[0])
        #print d
        if self.zver < 4:
            # Get the property table address
            prop_addr = (self.mem[d+7] << 8) + self.mem[d+8]
            #print prop_addr
            prop = self._find_prop(prop_addr,ops[1])
            if prop == 0: # Property not found!
                print "Property ",ops[1]," not found for object ",ops[0]
                sys.exit()
            else:
                #print self.mem[prop] / 32
                if (self.mem[prop] / 32) == 0: # Only 1 byte
                    self.mem[prop+1] = ops[2] & 0xff
                else:
                    self.mem[prop+1] = ops[2] >> 8
                    self.mem[prop+2] = ops[2] & 0xff
        else:
            # Get the property table address
            prop_addr = (self.mem[d+12] << 8) + self.mem[d+13]
            #print prop_addr
            prop = self._find_prop(prop_addr,ops[1])
            if prop == 0: # Property not found!
                print "Property ",ops[1]," not found for object ",ops[0]
                sys.exit()
            else:
                if ((self.mem[prop] & 0x80) == 0) and ((self.mem[prop] & 0x40) == 0): # Only 1 byte
                    self.mem[prop+1] = ops[2] & 0xff
                elif (self.mem[prop] & 0x80) == 0: # 2 bytes
                    self.mem[prop+1] = ops[2] >> 8
                    self.mem[prop+2] = ops[2] & 0xff
                else:
                    self.mem[prop+2] = ops[2] >> 8
                    self.mem[prop+3] = ops[2] & 0xff
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: put_prop {1}'.format(format(pc,'X'),ops), 2 )

    def _sread(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        self.intr = 1
        if (len(ops)>=2):
            self.intr_data = ops
        else:
            self.intr_data = [ops[0], 0]
        #print "Max read:", self.mem[ops[0]]
        #print "Max parse:", self.mem[ops[1]]
        #if (self.mem[ops[0]] < 7):
        #    exit("Input buffer too small")
        if self.zver < 4:
            self._show_status2()
            pass
        elif self.zver == 4:
            pass
        elif self.zver == 5:
            pass
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: sread {1}'.format(format(pc,'X'),ops), 2 )

    def _print_char(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        text = convert_from_zscii(ops[0], self.mem, 0)
        self.output.prints(text)
        #print text
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: print_char {1}'.format(format(pc,'X'),ops), 2 )

    def _print_num(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if ops[0] > 0x7fff:
            self.output.prints("{0}".format(ops[0] - 65536))
            #print (ops[0] - 65536)
        else:
            self.output.prints("{0}".format(ops[0]))
            #print ops[0]
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: print_num {1}'.format(format(pc,'X'),ops), 2 )

    def _random(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if ops[0] > 0x7fff: # Change seed
            self.random.set_seed(0x10000 - ops[0])
            r = 0
        elif ops[0] <> 0: # Get a random num between 1 and ops[0]
            self.random.set_range(ops[0])
            r = self.random.get_random()
        else: # Get random seed
            self.random.set_mode(0)
            r = 0
        #print "Returns:", r
        self._zstore(r,self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: random {1}'.format(format(pc,'X'),ops), 2 )

    def _push(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        self.stack.push(ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: push {1}'.format(format(pc,'X'),ops), 2 )

    def _pull(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if self.zver <> 6:
            n = self.stack.pop()
            self._zstore(n, ops[0])
            if (self.plugin.level >= 2):
                self.plugin.debugprint( '{0}: pull {1}'.format(format(pc,'X'),ops), 2 )
        else:
            if (ops==[]): # Use the game stack
                n = self.stack.pop()
                variable = self.mem[self.pc]
                self._zstore(n, variable)
                self.pc += 1
            else:
                # TODO: Add support for ver 6
                sys.exit('pull: User stacks not implemented for V6!')
                if (self.plugin.level >= 2):
                    self.plugin.debugprint( '{0}: pull {1} -> {2}'.format(format(pc,'X'),ops,variable), 2 )

    def _split_window(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        self.output.show_upper_window(ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: split_window {1}'.format(format(pc,'X'),ops), 2 )

    def _set_window(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        self.output.set_window(ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: set_window {1}'.format(format(pc,'X'),ops), 2 )

    def _call_vs2(self):
        pc = self.pc
        ops = self._read_operands_var_2op2()
        ret = self.mem[self.pc]
        self.pc += 1
        argv = []
        i = 1
        while i < len(ops):
            argv.append(ops[i])
            i += 1
        self._routine(ops[0], argv, ret)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: call_vs2 {1}'.format(format(pc,'X'),ops), 2 )

    def _erase_window(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if ops[0] == 0xffff: # Unsplit and clear screen
            # TODO: Unsplit
            if (self.plugin.level >= 2):
                self.plugin.debugprint("TODO:Unsplit", 2)
            self.output.clear_screen()
        elif ops[0] == 0xfffe: # Just clear the screen
            pass
        else: # Erase window
            self.plugin.erase_window(ops[0])
            if (self.plugin.level >= 2):
                self.plugin.debugprint( '{0}: erase_window {1}'.format(format(pc,'X'),ops), 2 )

    def _erase_line(self):
        self.plugin.debugprint( ': erase_line', 0 )
        sys.exit("Not implemented yet!")

    def _set_cursor(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        self.output.set_cursor(ops[1],ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: set_cursor {1}'.format(format(pc,'X'),ops), 2 )

    def _get_cursor(self):
        self.plugin.debugprint( ': get_cursor', 0 )
        sys.exit("Not implemented yet!")

    def _set_text_style(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        self.output.set_font_style(ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: set_text_style {1}'.format(format(pc,'X'),ops), 2 )

    def _buffer_mode(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        print ops
        self.output.set_buffering(ops[0])
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: buffer_mode {1}'.format(format(pc,'X'),ops), 2 )

    def _output_stream(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        print ops
        if ops[0] <> 0:
            if ops[0] == 3:
                table = ops[1]
            else:
                table = -1
            if ops[0] > 0x7fff: # Negative value
                self.output.deselect_stream(0x10000 - ops[0])
            else:
                self.output.select_stream(ops[0],table)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: output_stream {1}'.format(format(pc,'X'),ops), 2 )

    def _input_stream(self):
        self.plugin.debugprint( ': input_stream', 0 )
        sys.exit("Not implemented yet!")

    def _sound_effect(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        # TODO: Implement beeps and sounds!
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: sound_effect {1}'.format(format(pc,'X'),ops), 2 )
            self.plugin.debugprint( 'TODO:Sound effects', 2)

    def _read_char(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: read_char {1}'.format(format(pc,'X'),ops), 2 )
        if len(ops) > 1:
            self.intr_data = [ops[1],ops[2]]
        else:
            self.intr_data = [0]
        self.intr = 2

    def _scan_table(self):
        self.plugin.debugprint( ': scan_table', 0 )
        sys.exit("Not implemented yet!")

    def _not_var(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        r = ops[0] ^ 0xffff
        self._zstore(r,self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: not_var {1}'.format(format(pc,'X'),ops), 2 )

    def _call_vn(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        argv = []
        i = 1
        while i < len(ops):
            argv.append(ops[i])
            i += 1
        self._routine(ops[0], argv, -1)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: call_vn {1}'.format(format(pc,'X'),ops), 2 )

    def _call_vn2(self):
        pc = self.pc
        ops = self._read_operands_var_2op2()
        argv = []
        i = 1
        while i < len(ops):
            argv.append(ops[i])
            i += 1
        self._routine(ops[0], argv, -1)
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: call_vn2 {1}'.format(format(pc,'X'),ops), 2 )

    def _tokenise(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        self.intr = 4
        self.intr_data = [0,0,0,0]
        self.intr_data[0] = ops[0]
        self.intr_data[1] = ops[1]
        if len(ops) >= 3:
            self.intr_data[2] = ops[2]
        if len(ops) == 4:
            self.intr_data[3] = ops[3]
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: tokenise {1}'.format(format(pc,'X'),ops), 2 )

    def _encode_text(self):
        self.plugin.debugprint( ': encode_text', 0 )
        sys.exit("Not implemented yet!")

    def _copy_table(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: copy_table {1}'.format(format(pc,'X'),ops), 2 )
        if (ops[1] == 0): # Copy zeros to the first variable
            for i in xrange(abs(ops[2])):
                self.mem[ops[0]+i] = 0
        else: # Copy first to second
            tmplist = []
            if (ops[2]>0): # Make sure that the first isn't destroyed
                for i in xrange(ops[2]):
                    tmplist.append(self.mem[ops[0]+i])
                for i in xrange(ops[2]):
                    self.mem[ops[1]+i] = tmplist[i]
                for i in xrange(ops[2]):
                    self.mem[ops[0]+i] = tmplist[i]
            else:
                for i in xrange(abs(ops[2])):
                    self.mem[ops[1]+i] = self.mem[ops[0]+i]

    def _print_table(self):
        self.plugin.debugprint( ': print_table', 0 )
        sys.exit("Not implemented yet!")

    def _check_arg_count(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        noa = self.stack.pop_frame()
        #print "Number of args:",noa
        self.stack.push_frame(noa)
        r = False
        for i in xrange(len(ops)):
            r = r or (ops[i] <= noa)

        if (self.mem[self.pc] & 64) == 64: # Offset is 1 byte long
            offset = self.mem[self.pc] & 63
            gf = 1
        else: # Offset is 2 byte long
            if self.mem[self.pc] & 32 == 32: # Negative offset
                offset = (((self.mem[self.pc] | 0xc0) << 8) + self.mem[self.pc + 1] - 65536)
            else:
                offset = ((self.mem[self.pc] & 63) << 8) + self.mem[self.pc + 1]
            gf = 2
        jif = 'True'
        if (self.mem[self.pc] & 128) == 128: # Jump if true
            if r: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        else:
            jif = 'False'
            if not r: # Jump to label
                if offset == 0: # Return false
                    self._return(0)
                elif offset == 1: # Return true
                    self._return(1)
                else:
                    self.pc = self.pc + gf + offset - 2
            else:
                self.pc = self.pc + gf
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: check_arg_count {1} [{2}] {3}'.format(format(pc,'X'),ops,jif,offset), 2 )

    def _save_ext(self):
        self.plugin.debugprint( ': save_ext', 0 )
        sys.exit("Not implemented yet!")

    def _restore_ext(self):
        self.plugin.debugprint( ': restore_ext', 0 )
        sys.exit("Not implemented yet!")

    def _log_shift(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        shift = self._s2i(ops[1])
        if shift > 0:
            res = ops[0] << ops[1]
        else:
            res = ops[0] >> abs(shift)
        #print "Result:", self._i2s(res)
        self._zstore(self._i2s(res), self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: log_shift {1}'.format(format(pc,'X'),ops), 2 )

    def _art_shift(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        shift = self._s2i(ops[1])
        if shift > 0:
            res = self._s2i(ops[0]) << ops[1]
        else:
            res = self._s2i(ops[0]) >> abs(shift)
        #print "Result:", self._i2s(res)
        self._zstore(self._i2s(res), self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: art_shift {1}'.format(format(pc,'X'),ops), 2 )

    def _set_font(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if (self.plugin.level >= 2):
            self.plugin.debugprint( 'TODO:Implement all fonts', 2)
        # TODO: Implement other fonts
        res = self.output.set_font(ops[0])
        self._zstore(res, self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: set_font {1}'.format(format(pc,'X'),ops), 2 )

    def _draw_picture(self):
        self.plugin.debugprint( ': draw_picture', 0 )
        sys.exit("Not implemented yet!")

    def _picture_data(self):
        self.plugin.debugprint( ': picture_data', 0 )
        sys.exit("Not implemented yet!")

    def _erase_picture(self):
        self.plugin.debugprint( ': erase_picture', 0 )
        sys.exit("Not implemented yet!")

    def _set_margins(self):
        self.plugin.debugprint( ': set_margins', 0 )
        sys.exit("Not implemented yet!")

    def _save_undo(self):
        pc = self.pc
        if (self.plugin.level >= 2):
            self.plugin.debugprint( 'TODO:Implement undo', 2)
        # TODO: Implement undo!
        ops = self._read_operands_var_2op()
        self._zstore(65535, self.mem[self.pc]) # For now say that undo isn't available :-)
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: save_undo {1}'.format(format(pc,'X'),ops), 2 )

    def _restore_undo(self):
        self.plugin.debugprint( ': restore_undo', 0 )
        sys.exit("Not implemented yet!")

    def _print_unicode(self):
        self.plugin.debugprint( ': print_unicode', 0 )
        sys.exit("Not implemented yet!")

    def _check_unicode(self):
        pc = self.pc
        ops = self._read_operands_var_2op()
        if (ops[0] >= 0x20) and (ops[0] <= 0x7e):
            self._zstore(3, self.mem[self.pc])
        elif ops[0] == 0xa0:
            self._zstore(1, self.mem[self.pc])
        elif (ops[0] >= 0xa1) and (ops[0] <= 0xff):
            self._zstore(3, self.mem[self.pc])
        else:
            self._zstore(0, self.mem[self.pc])
        self.pc += 1
        if (self.plugin.level >= 2):
            self.plugin.debugprint( '{0}: check_unicode {1}'.format(format(pc,'X'),ops), 2 )

    def _move_window(self):
        self.plugin.debugprint( ': move_window', 0 )
        sys.exit("Not implemented yet!")

    def _window_size(self):
        self.plugin.debugprint( ': window_size', 0 )
        sys.exit("Not implemented yet!")

    def _window_style(self):
        self.plugin.debugprint( ': window_style', 0 )
        sys.exit("Not implemented yet!")

    def _get_wind_prop(self):
        self.plugin.debugprint( ': wind_prop', 0 )
        sys.exit("Not implemented yet!")

    def _scroll_window(self):
        self.plugin.debugprint( ': scroll_window', 0 )
        sys.exit("Not implemented yet!")

    def _pop_stack(self):
        self.plugin.debugprint( ': pop_stack', 0 )
        sys.exit("Not implemented yet!")

    def _read_mouse(self):
        self.plugin.debugprint( ': read_mouse', 0 )
        sys.exit("Not implemented yet!")

    def _mouse_window(self):
        self.plugin.debugprint( ': mouse_window', 0 )
        sys.exit("Not implemented yet!")

    def _push_stack(self):
        self.plugin.debugprint( ': push_stack', 0 )
        sys.exit("Not implemented yet!")

    def _put_wind_prop(self):
        self.plugin.debugprint( ': put_wind_prop', 0 )
        sys.exit("Not implemented yet!")

    def _print_form(self):
        self.plugin.debugprint( ': print_form', 0 )
        sys.exit("Not implemented yet!")

    def _make_menu(self):
        self.plugin.debugprint( ': make_menu', 0 )
        sys.exit("Not implemented yet!")

    def _picture_table(self):
        self.plugin.debugprint( ': picture_table', 0 )
        sys.exit("Not implemented yet!")

    def _read_operands_short_1op(self):
        values = []
        if (self.mem[self.pc] & 48) == 0:
            #print "Long const"
            self.pc += 1
            num = ( self.mem[self.pc] << 8 ) + self.mem[self.pc+1]
            values.append( num )
            self.pc += 2
        elif (self.mem[self.pc] & 48) == 16:
            #print "Small const"
            self.pc += 1
            num = self.mem[self.pc]
            values.append( num )
            self.pc += 1
        else:
            self.pc += 1
            if self.mem[self.pc] == 0:
                #print "Got stack!"
                values.append( self.stack.pop() )
            elif self.mem[self.pc] < 0x10:
                #print "Got local variable", self.mem[self.pc]
                values.append( self.stack.local_vars[self.mem[self.pc] - 1] )
            else:
                #print "Got global var", (self.mem[self.pc] - 15)
                b1 = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 ]
                b2 = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 + 1]
                values.append( (b1 << 8) + b2 )
            self.pc += 1
        return values


    def _read_operands_var_2op(self):
        self.pc = self.pc + 1
        values = []
        mask = 192
        type_byte = self.mem[self.pc]
        self.pc = self.pc + 1
        for i in xrange(4):
            optype = ( type_byte & mask) >> (3-i)*2
            if optype == 0: # Large constant (2 bytes)
                #print "PC:",hex(self.pc),"--",hex(self.mem[self.pc]),",",hex(self.mem[self.pc+1])
                num = ( self.mem[self.pc] << 8 ) + self.mem[self.pc+1]
                values.append( num )
                self.pc = self.pc + 2
            elif optype == 1: # Small constant (1 byte)
                values.append( self.mem[self.pc] )
                self.pc = self.pc + 1
            elif optype == 2: # Variable (1 byte)
                if self.mem[self.pc] == 0:
                    values.append( self.stack.pop() )
                elif self.mem[self.pc] < 0x10:
                    values.append( self.stack.local_vars[self.mem[self.pc] - 1] )
                else:
                    b1 = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 ]
                    b2 = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 + 1]
                    values.append( (b1 << 8) + b2 )
                self.pc = self.pc + 1
            else: # Omitted
                pass
            mask = mask >> 2
        return values

    def _read_operands_var_2op2(self):
        self.pc = self.pc + 1
        values = []
        mask = 192
        type_byte = self.mem[self.pc]
        type_byte2 = self.mem[self.pc + 1]
        self.pc = self.pc + 2
        for i in xrange(4):
            optype = ( type_byte & mask) >> (3-i)*2
            if optype == 0: # Large constant (2 bytes)
                #print "PC:",hex(self.pc),"--",hex(self.mem[self.pc]),",",hex(self.mem[self.pc+1])
                num = ( self.mem[self.pc] << 8 ) + self.mem[self.pc+1]
                values.append( num )
                self.pc = self.pc + 2
            elif optype == 1: # Small constant (1 byte)
                values.append( self.mem[self.pc] )
                self.pc = self.pc + 1
            elif optype == 2: # Variable (1 byte)
                if self.mem[self.pc] == 0:
                    values.append( self.stack.pop() )
                elif self.mem[self.pc] < 0x10:
                    values.append( self.stack.local_vars[self.mem[self.pc] - 1] )
                else:
                    b1 = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 ]
                    b2 = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 + 1]
                    values.append( (b1 << 8) + b2 )
                self.pc = self.pc + 1
            else: # Omitted
                pass
            mask = mask >> 2
        mask = 192
        for i in xrange(4):
            optype = ( type_byte2 & mask) >> (3-i)*2
            if optype == 0: # Large constant (2 bytes)
                #print "PC:",hex(self.pc),"--",hex(self.mem[self.pc]),",",hex(self.mem[self.pc+1])
                num = ( self.mem[self.pc] << 8 ) + self.mem[self.pc+1]
                values.append( num )
                self.pc = self.pc + 2
            elif optype == 1: # Small constant (1 byte)
                values.append( self.mem[self.pc] )
                self.pc = self.pc + 1
            elif optype == 2: # Variable (1 byte)
                if self.mem[self.pc] == 0:
                    values.append( self.stack.pop() )
                elif self.mem[self.pc] < 0x10:
                    values.append( self.stack.local_vars[self.mem[self.pc] - 1] )
                else:
                    b1 = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 ]
                    b2 = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 + 1]
                    values.append( (b1 << 8) + b2 )
                self.pc = self.pc + 1
            else: # Omitted
                pass
            mask = mask >> 2
        return values

    def _read_operands_long_2op(self):
        values = []
        code = self.mem[self.pc]
        self.pc = self.pc + 1
        if (code & 64) == 0:
            values.append(self.mem[self.pc])
        else:
            if self.mem[self.pc] == 0:
                values.append( self.stack.pop() )
            elif self.mem[self.pc] < 0x10:
                values.append( self.stack.local_vars[self.mem[self.pc] - 1] )
            else:
                num = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 ] << 8
                num = num + self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 + 1]
                values.append( num )
        self.pc = self.pc + 1
        if (code & 32) == 0:
            values.append(self.mem[self.pc])
        else:
            if self.mem[self.pc] == 0:
                values.append( self.stack.pop() )
            elif self.mem[self.pc] < 0x10:
                values.append( self.stack.local_vars[self.mem[self.pc] - 1] )
            else:
                num = self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 ] << 8
                num = num + self.mem[ self.header.global_table() + (self.mem[self.pc] - 16) * 2 + 1]
                values.append( num )
        self.pc = self.pc + 1
        return values


    def _unpack_addr(self,addr,usage=0):
        if self.zver < 4:
            return 2*addr
        elif self.zver < 6:
            return 4*addr
        elif self.zver < 8:
            if usage == 0:
                return 4*addr + 8*self.header.routines()
            else:
                return 4*addr + 8*self.header.strings()
        else:
            return 8*addr

    def _zstore(self,value,where):
        # Deal with overflow
        if value >= 0x10000:
            value = value % 0x10000
        # Check where to save the value
        if where == 0:
            self.stack.push(value)
            #print "Value",value," pushed into stack"
        elif where < 16:
            self.stack.local_vars[where - 1] = value
            #print "Local var", where, "has now value", value
        elif where < 256:
            self.mem[self.header.global_table() + (where - 16) * 2] = (value >> 8)
            self.mem[self.header.global_table() + (where - 16) * 2 + 1] = (value & 0xff)
            #print "Global var", where - 15, "has now value", value
        else:
            self.mem[where] = value >> 8
            self.mem[where + 1] = value & 0xff

    def _i2s(self,value):
        """Convert value to short int"""
        #print "i2s --", value
        if value < 0:
            value = 0x10000 + value
        if value > 0xffff: # Overflow
            return value % 0x10000
        elif value >= 0: # Normal positive number
            return value
        elif value >= 0x8000: # Normal negative number
            return 0x10000 - value
        else: # Underflow
            # Don't know if this is the right thing to do
            # However we shouldn't get underflows anyway :-)
            return (-value) % 0x10000

    def _s2i(self,value):
        """Convert value back to int"""
        if value > 0x7fff: # Negative
            return -(0x10000 - value)
        else:
            return value

    def _find_object(self,value):
        if self.zver < 4:
            base = self.header.obj_table()
            d = base + (31 * 2) # Skip property defaults table
            obj_details = (self.mem[d + 7] << 8) + self.mem[d + 8]
            d = d + (value - 1) * 9
            if d < obj_details:
                return d
            else:
                sys.exit("Couln't find object")
        else:
            base = self.header.obj_table()
            d = base + (63 * 2) # Skip property defaults table
            obj_details = (self.mem[d + 12] << 8) + self.mem[d + 13]
            d = d + (value - 1) * 14
            if d < obj_details:
                return d
            else:
                sys.exit("Couln't find object")

    def _find_prop(self,table_addr,prop):
        #print "--", format(table_addr, "X"), "--", self.mem[table_addr]
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
        #dtext = decode_text(text, self.zver, self.mem, self.header.abbrev_table(), False, self.header.alphabet_table(), 0)
        #print dtext
        p = table_addr + self.mem[table_addr] * 2 + 1 # Skip property name
        if self.zver < 4:
            #print "++",p,"++"
            while (self.mem[p] % 32) > prop:
                p = p + (self.mem[p] // 32) + 2
                #print "++=",p,"=++"
            if (self.mem[p] % 32) == prop:
                return p
            else:
                return 0
        else:
            #print "++",format(p,"X"),"++"
            while (self.mem[p] & 0x3f) > prop:
                if (self.mem[p] & 0x80) <> 0: # Top bit is 1 so there is a second byte
                    #print "There is a second byte!"
                    p = p + 1
                    num = self.mem[p] & 0x3f
                    if num == 0:
                        num = 64
                    p = p + num + 1
                elif (self.mem[p] & 0x40) <> 0: # 6th bit is 1 so there are 2 bytes of data
                    p = p + 3
                else: # Only 1 byte of data
                    p = p + 2
                #print "++=",format(p,"X"),"=++"
            if (self.mem[p] & 0x3f) == prop:
                return p
            else:
                return 0

    def start(self):
        while(self.intr == 0):
            self.command()

    def start6(self):
        print self.pc
        self._prepare_routine(self.pc, [])
        print self.pc

    def _show_status2(self):
        if self.zver < 4:
            # Find the name of the current room
            objnum = (self.mem[self.header.global_table()] << 8) + self.mem[self.header.global_table() + 1]
            obj = self._find_object(objnum)
            if self.zver < 4:
                prop_addr = (self.mem[obj + 7] << 8) + self.mem[obj + 8]
            else:
                prop_addr = (self.mem[obj + 12] << 8) + self.mem[obj + 13]
            nob = 2 * self.mem[prop_addr]
            buf = []
            for i in xrange(nob):
                buf.append(self.mem[prop_addr + i + 1])
            text = decode_text(buf, self.zver, self.mem, self.header.abbrev_table(), False, self.header.alphabet_table(), 0)

            # Now we need to determine if it is a score game or a time game
            score_game = False
            if self.zver < 3:
                score_game = True
            else:
                if self.header.score_game() == 0:
                    score_game = True
            if score_game:
                score = (self.mem[self.header.global_table() + 2] << 8) + self.mem[self.header.global_table() + 3]
                turns = (self.mem[self.header.global_table() + 4] << 8) + self.mem[self.header.global_table() + 5]
                self.output.print_status(text, "Score: {0} Turns: {1}".format(score, turns))
            else:
                hour = (self.mem[self.header.global_table() + 2] << 8) + self.mem[self.header.global_table() + 3]
                mins = (self.mem[self.header.global_table() + 4] << 8) + self.mem[self.header.global_table() + 5]
                if mins < 10:
                    self.output.print_status(text, "{0}:0{1}".format(hour, mins))
                else:
                    self.output.print_status(text, "{0}:{1}".format(hour, mins))

    def _routine(self,r,argv,res,intr_on_return=0):
        # Save local vars, pc and return address in stack
        self.stack.push_local_vars()
        self.stack.push_frame( self.pc )
        self.stack.push_frame( res )
        self.stack.push_frame( intr_on_return )
        self.stack.push_frame( self.intr_data )
        self.stack.push_frame(len(argv))
        self._prepare_routine(r, argv)

    def _prepare_routine(self, r, argv):
        # Jump to routine address
        self.pc = self._unpack_addr(r)
        #print "Max:", self.header.length_of_file()
        #print self.pc
        if self.pc > self.header.length_of_file():
            sys.exit("Call out of bounds!")
        #print self.mem[self.pc]
        self.stack.local_vars_num = self.mem[self.pc]
        self.pc = self.pc + 1
        if self.stack.local_vars_num > 0:
            # Initialize local variables
            if self.zver < 5:
                for i in xrange(self.stack.local_vars_num):
                    self.stack.local_vars[i] = (self.mem[self.pc] << 8) + self.mem[self.pc + 1]
                    if i < len(argv):
                        self.stack.local_vars[i] = argv[i]
                    #print self.stack.local_vars[i]
                    self.pc = self.pc + 2
            else:
                for i in xrange(self.stack.local_vars_num):
                    self.stack.local_vars[i] = 0
                    if i < len(argv):
                        self.stack.local_vars[i] = argv[i]
                    #print self.stack.local_vars[i]

    def got_char(self, char):
        self._zstore(char, self.mem[self.pc])
        self.pc += 1
