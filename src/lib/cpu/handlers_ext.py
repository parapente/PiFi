from sys import exit


class ZCpuExtHandlers:
    def _save_ext(self):
        self.plugin.debug_print(": save_ext", 0)
        exit("Not implemented yet!")

    def _restore_ext(self):
        self.plugin.debug_print(": restore_ext", 0)
        exit("Not implemented yet!")

    def _log_shift(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        shift = self._s2i(ops[1])
        if shift > 0:
            res = ops[0] << ops[1]
        else:
            res = ops[0] >> abs(shift)
        self._zstore(self._i2s(res), self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: log_shift {ops[0 : self.numops]}", 2
            )

    def _art_shift(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        shift = self._s2i(ops[1])
        if shift > 0:
            res = self._s2i(ops[0]) << ops[1]
        else:
            res = self._s2i(ops[0]) >> abs(shift)
        self._zstore(self._i2s(res), self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: art_shift {ops[0 : self.numops]}", 2
            )

    def _set_font(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if self.plugin.level >= 2:
            self.plugin.debug_print("TODO:Implement all fonts", 2)
        res = self.output.set_font(ops[0])
        self._zstore(res, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: set_font {ops[0 : self.numops]}", 2
            )

    def _draw_picture(self):
        self.plugin.debug_print(": draw_picture", 0)
        exit("Not implemented yet!")

    def _picture_data(self):
        self.plugin.debug_print(": picture_data", 0)
        exit("Not implemented yet!")

    def _erase_picture(self):
        self.plugin.debug_print(": erase_picture", 0)
        exit("Not implemented yet!")

    def _set_margins(self):
        self.plugin.debug_print(": set_margins", 0)
        exit("Not implemented yet!")

    def _save_undo(self):
        pc = self.pc
        if self.plugin.level >= 2:
            self.plugin.debug_print("TODO:Implement undo", 2)
        self._read_operands_var_2op()
        ops = self.ops
        self._zstore(65535, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: save_undo {ops[0 : self.numops]}", 2
            )

    def _restore_undo(self):
        self.plugin.debug_print(": restore_undo", 0)
        exit("Not implemented yet!")

    def _print_unicode(self):
        self.plugin.debug_print(": print_unicode", 0)
        exit("Not implemented yet!")

    def _check_unicode(self):
        pc = self.pc
        self._read_operands_var_2op()
        ops = self.ops
        if (ops[0] >= 0x20) and (ops[0] <= 0x7E):
            self._zstore(3, self.mem[self.pc])
        elif ops[0] == 0xA0:
            self._zstore(1, self.mem[self.pc])
        elif (ops[0] >= 0xA1) and (ops[0] <= 0xFF):
            self._zstore(3, self.mem[self.pc])
        else:
            self._zstore(0, self.mem[self.pc])
        self.pc += 1
        if self.plugin.level >= 2:
            self.plugin.debug_print(
                f"{format(pc, 'X')}: check_unicode {ops[0 : self.numops]}",
                2,
            )

    def _move_window(self):
        self.plugin.debug_print(": move_window", 0)
        exit("Not implemented yet!")

    def _window_size(self):
        self.plugin.debug_print(": window_size", 0)
        exit("Not implemented yet!")

    def _window_style(self):
        self.plugin.debug_print(": window_style", 0)
        exit("Not implemented yet!")

    def _get_wind_prop(self):
        self.plugin.debug_print(": wind_prop", 0)
        exit("Not implemented yet!")

    def _scroll_window(self):
        self.plugin.debug_print(": scroll_window", 0)
        exit("Not implemented yet!")

    def _pop_stack(self):
        self.plugin.debug_print(": pop_stack", 0)
        exit("Not implemented yet!")

    def _read_mouse(self):
        self.plugin.debug_print(": read_mouse", 0)
        exit("Not implemented yet!")

    def _mouse_window(self):
        self.plugin.debug_print(": mouse_window", 0)
        exit("Not implemented yet!")

    def _push_stack(self):
        self.plugin.debug_print(": push_stack", 0)
        exit("Not implemented yet!")

    def _put_wind_prop(self):
        self.plugin.debug_print(": put_wind_prop", 0)
        exit("Not implemented yet!")

    def _print_form(self):
        self.plugin.debug_print(": print_form", 0)
        exit("Not implemented yet!")

    def _make_menu(self):
        self.plugin.debug_print(": make_menu", 0)
        exit("Not implemented yet!")

    def _picture_table(self):
        self.plugin.debug_print(": picture_table", 0)
        exit("Not implemented yet!")
