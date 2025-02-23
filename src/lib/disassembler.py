# -*- coding: utf-8

from lib.machine import ZMachine
from lib.header import ZHeader
import sys

__author__ = "Theofilos Intzoglou"
__date__ = "$01 Μαΐου 2013 5:49:30 μμ$"


class ZDisassembler:

    def __init__(self, m, verbose):
        self.machine = m
        self.verbose = verbose
        self.t2op = dict({1: "je",
                          2: "jl",
                          3: "jg",
                          4: "dec_chk",
                          5: "inc_chk",
                          6: "jin",
                          7: "test",
                          8: "or",
                          9: "and",
                          10: "test_attr",
                          11: "set_attr",
                          12: "clear_attr",
                          13: "store",
                          14: "insert_obj",
                          15: "loadw",
                          16: "loadb",
                          17: "get_prop",
                          18: "get_prop_addr",
                          19: "get_next_prop",
                          20: "add",
                          21: "sub",
                          22: "mul",
                          23: "div",
                          24: "mod",
                          25: "call_2s",
                          26: "call_2n",
                          27: "set_colour",
                          28: "throw"})
        self.t1op = dict({128: "jz",
                          129: "get_sibling",
                          130: "get_child",
                          131: "get_parent",
                          132: "get_prop_len",
                          133: "inc",
                          134: "dec",
                          135: "print_addr",
                          136: "call_1s",
                          137: "remove_obj",
                          138: "print_obj",
                          139: "ret",
                          140: "jump",
                          141: "print_paddr",
                          142: "load",
                          143: "not"})
        self.t0op = dict({176: "rtrue",
                          177: "rfalse",
                          178: "print",
                          179: "print_ret",
                          180: "nop",
                          181: "save",
                          182: "restore",
                          183: "restart",
                          184: "ret_popped",
                          185: "pop",
                          186: "quit",
                          187: "new_line",
                          188: "show_status",
                          189: "verify",
                          190: None,
                          191: "piracy"})
        self.tvar = dict({224: "call",
                          225: "storew",
                          226: "storeb",
                          227: "put_prop",
                          228: "sread",
                          229: "print_char",
                          230: "print_num",
                          231: "random",
                          232: "push",
                          233: "pull",
                          234: "split_window",
                          235: "set_window",
                          236: "call_vs2",
                          237: "erase_window",
                          238: "erase_line",
                          239: "set_cursor",
                          240: "get_cursor",
                          241: "set_text_style",
                          242: "buffer_mode",
                          243: "output_stream",
                          244: "input_stream",
                          245: "sound_effect",
                          246: "read_char",
                          247: "scan_table",
                          248: "not_var",
                          249: "call_vn",
                          250: "call_vn2",
                          251: "tokenise",
                          252: "encode_text",
                          253: "copy_table",
                          254: "print_table",
                          255: "check_arg_count"})
        self.text = dict({0: "save_ext",
                          1: "restore_ext",
                          2: "log_shift",
                          3: "art_shift",
                          4: "set_font",
                          5: "draw_picture",
                          6: "picture_data",
                          7: "erase_picture",
                          8: "set_margins",
                          9: "save_undo",
                          10: "restore_undo",
                          11: "print_unicode",
                          12: "check_unicode",
                          13: None,
                          14: None,
                          15: None,
                          16: "move_window",
                          17: "window_size",
                          18: "window_style",
                          19: "get_wind_prop",
                          20: "scroll_window",
                          21: "pop_stack",
                          22: "read_mouse",
                          23: "mouse_window",
                          24: "push_stack",
                          25: "put_wind_prop",
                          26: "print_form",
                          27: "make_menu",
                          28: "picture_table"})

    def disassemble(self):
        pc = self.machine.header.pc()
        self.routine_number = 1
        self.routine(pc)
        mem = self.machine.mem.mem
        value = mem[pc]
        try:
            cmd = self.command_dict[value]
            if value == 0xbe:
                self.pc += 1
                cmd()
        except KeyError:
            if value < 0x80:  # LONG 2OP
                code = (value & 31)
            if value == 0:
                sys.exit("Invalid opcode!")
                self.command_dict[value] = self.t2op[code]
                self.t2op[code]()
            elif value < 0xb0:  # SHORT 1OP
                code = (value & 15) + 128
                self.command_dict[value] = self.t1op[code]
                self.t1op[code]()
            elif (value < 0xc0) and (value != 0xbe):  # SHORT 0OP
                code = (value & 15) + 176
                self.command_dict[value] = self.t0op[code]
                self.t0op[code]()
            elif value == 0xbe:  # EXTENDED VAR
                self.pc += 1
                code = self.mem[self.pc]
                self.command_dict[value] = self.text[code]
                self.text[code]()
            elif value < 0xe0:  # VARIABLE 2OP
                code = value & 31
                self.command_dict[value] = self.t2op[code]
                self.t2op[code]()
            else:
                code = (value & 31) + 224
                self.command_dict[value] = self.tvar[code]
                self.tvar[code]()

    def routine(self, pc):
        pass
