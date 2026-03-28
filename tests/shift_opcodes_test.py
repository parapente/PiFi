#!/usr/bin/env python3
"""
Test suite for art_shift and log_shift opcodes.
Tests verify the correct implementation of arithmetic and logical shift operations.

According to Z-machine 1.1 spec:
- art_shift: Arithmetic shift (sign bit preserved on right shift)
- log_shift: Logical shift (zeros fill on right shift)
- Both shift left if places > 0, right if places < 0
- places must be in range -15 to +15
"""

import pytest
import sys
from io import BytesIO
from lib.container.container import Container
from lib.container.item import ItemType
from lib.cpu import ZCpu
from lib.memory import ZMemory
from lib.stack import ZStack
from lib.zrandom import ZRandom
from lib.output import ZOutput
from lib.header import ZHeader


class MockPlugin:
    """Mock plugin for testing."""
    def __init__(self, zver=5):
        self.zver = zver
        self.debug_level = 0
        self.output_buffer = []
        self.level = 0
        
    def debug_print(self, msg, level=0):
        pass
    
    def select_output_stream(self, n):
        pass
    
    def deselect_output_stream(self, n):
        pass
    
    def selected_output_streams(self):
        return []
    
    def print_string(self, s):
        self.output_buffer.append(s)
    
    def print_status(self, room, status):
        pass
    
    def clear_screen(self):
        pass
    
    def set_font_style(self, s):
        pass
    
    def show_upper_window(self, lines):
        pass
    
    def set_window(self, w):
        pass
    
    def set_cursor(self, y, x):
        pass
    
    def set_colour(self, fg, bg):
        pass
    
    def new_line(self):
        pass
    
    def set_font(self, f):
        return 1
    
    def show_cursor(self):
        pass


def create_minimal_memory(zver=5):
    """Create minimal valid Z-machine memory."""
    mem = bytearray(64 * 1024)
    
    # Header
    mem[0] = zver
    mem[1] = 0b00000010
    mem[2] = 0x01
    mem[3] = 0x00
    mem[6] = 0x00
    mem[7] = 0x20
    mem[8] = 0x00
    mem[9] = 0x30
    mem[0x0A] = 0x00
    mem[0x0B] = 0x60
    mem[0x0C] = 0x00
    mem[0x0D] = 0x70
    mem[0x0E] = 0x00
    mem[0x0F] = 0x80
    mem[0x1C] = 0x12
    mem[0x1D] = 0x34
    mem[0x10] = 0b00000000
    
    if zver >= 5:
        mem[0x20] = 25
        mem[0x21] = 80
        mem[0x2C] = 2
        mem[0x2D] = 9
    
    return mem


def setup_cpu(mem, zver=5):
    """Set up CPU for testing."""
    container = Container()
    container.destroy()
    
    memory = ZMemory()
    memory.mem = mem
    
    container.bind("ZMemory", lambda: memory, ItemType.RESOLVABLE)
    
    header = ZHeader()
    stack = ZStack()
    random = ZRandom()
    plugin = MockPlugin(zver)
    output = ZOutput(zver, plugin)
    
    container.bind("ZHeader", lambda: header, ItemType.RESOLVABLE)
    container.bind("ZStack", lambda: stack, ItemType.RESOLVABLE)
    container.bind("ZRandom", lambda: random, ItemType.RESOLVABLE)
    container.bind("ZOutput", lambda: output, ItemType.RESOLVABLE)
    
    cpu = ZCpu(output, plugin)
    cpu.mem = mem
    cpu.header = header
    cpu.stack = stack
    cpu.random = random
    cpu.zver = zver
    cpu.pc = header.pc
    cpu.file = BytesIO(mem)
    
    return cpu


def get_global_var(cpu, var_num):
    """Get value of global variable."""
    addr = cpu.header.global_variables_table + (var_num - 16) * 2
    return (cpu.mem[addr] << 8) | cpu.mem[addr + 1]


def set_global_var(cpu, var_num, value):
    """Set value of global variable."""
    addr = cpu.header.global_variables_table + (var_num - 16) * 2
    cpu.mem[addr] = (value >> 8) & 0xFF
    cpu.mem[addr + 1] = value & 0xFF


def s2i(value):
    """Convert unsigned 16-bit to signed."""
    if value > 0x7FFF:
        return -(0x10000 - value)
    return value


def i2s(value):
    """Convert signed to unsigned 16-bit."""
    return value & 0xFFFF


@pytest.fixture
def cpu_v5():
    """Create CPU for Version 5."""
    mem = create_minimal_memory(zver=5)
    return setup_cpu(mem, zver=5)


# ============================================================================
# art_shift Tests (EXT:3)
# ============================================================================

class TestArtShift:
    """Tests for art_shift opcode (EXT:3) - Arithmetic shift with sign preservation."""
    
    def test_art_shift_left_basic(self, cpu_v5):
        """Test art_shift left: 1 << 3 = 8."""
        cpu = cpu_v5
        mem = cpu.mem
        
        # EXT opcode prefix
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03  # art_shift
        # Type byte: 2 large constants
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0x00
        mem[cpu.pc + 4] = 0x01  # number = 1
        mem[cpu.pc + 5] = 0x00
        mem[cpu.pc + 6] = 0x03  # places = 3
        mem[cpu.pc + 7] = 0x70  # Store in global 112
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        assert result == 0x0008
    
    def test_art_shift_left_negative(self, cpu_v5):
        """Test art_shift left with negative: -16 << 1 = -32."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0xFF
        mem[cpu.pc + 4] = 0xF0  # -16 (0xFFF0)
        mem[cpu.pc + 5] = 0x00
        mem[cpu.pc + 6] = 0x01  # places = 1
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        # -16 << 1 = -32 = 0xFFE0
        assert result == 0xFFE0
    
    def test_art_shift_right_positive(self, cpu_v5):
        """Test art_shift right: 16 >> 2 = 4."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0x00
        mem[cpu.pc + 4] = 0x10  # 16
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFE  # -2
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        assert result == 0x0004
    
    def test_art_shift_right_negative_preserves_sign(self, cpu_v5):
        """Test art_shift right: -16 >> 2 = -4 (sign preserved)."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0xFF
        mem[cpu.pc + 4] = 0xF0  # -16 (0xFFF0)
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFE  # -2
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        # -16 >> 2 = -4 = 0xFFFC
        assert result == 0xFFFC, f"Expected 0xFFFC (-4), got 0x{result:04X} ({s2i(result)})"
    
    def test_art_shift_right_negative_large(self, cpu_v5):
        """Test art_shift right: -1 >> 1 = -1 (sign preserved, all 1s)."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0xFF
        mem[cpu.pc + 4] = 0xFF  # -1 (0xFFFF)
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFF  # -1
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        # -1 >> 1 = -1 = 0xFFFF (all bits remain 1)
        assert result == 0xFFFF, f"Expected 0xFFFF (-1), got 0x{result:04X} ({s2i(result)})"
    
    def test_art_shift_right_zero(self, cpu_v5):
        """Test art_shift right: -100 >> 2 = -25."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0xFF
        mem[cpu.pc + 4] = 0x9C  # -100 (0xFF9C)
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFE  # -2
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        # -100 >> 2 = -25 = 0xFFE7
        assert result == 0xFFE7, f"Expected 0xFFE7 (-25), got 0x{result:04X} ({s2i(result)})"
    
    def test_art_shift_zero_places(self, cpu_v5):
        """Test art_shift with 0 places: no change."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0xFF
        mem[cpu.pc + 4] = 0xF0  # -16
        mem[cpu.pc + 5] = 0x00
        mem[cpu.pc + 6] = 0x00  # places = 0
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        assert result == 0xFFF0  # Unchanged
    
    def test_art_shift_sign_bit_shifted_out(self, cpu_v5):
        """Test art_shift: 0x8000 >> 1 = 0x4000 (sign bit shifted out on left shift)."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0x80
        mem[cpu.pc + 4] = 0x00  # 0x8000 (sign bit set)
        mem[cpu.pc + 5] = 0x00
        mem[cpu.pc + 6] = 0x01  # places = 1 (left shift)
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        # 0x8000 << 1 = 0x10000 & 0xFFFF = 0x0000 (overflow)
        assert result == 0x0000


# ============================================================================
# log_shift Tests (EXT:2)
# ============================================================================

class TestLogShift:
    """Tests for log_shift opcode (EXT:2) - Logical shift with zero fill."""
    
    def test_log_shift_left_basic(self, cpu_v5):
        """Test log_shift left: 1 << 3 = 8."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x02  # log_shift
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0x00
        mem[cpu.pc + 4] = 0x01
        mem[cpu.pc + 5] = 0x00
        mem[cpu.pc + 6] = 0x03
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        assert result == 0x0008
    
    def test_log_shift_right_positive(self, cpu_v5):
        """Test log_shift right: 16 >> 2 = 4."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x02
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0x00
        mem[cpu.pc + 4] = 0x10  # 16
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFE  # -2
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        assert result == 0x0004
    
    def test_log_shift_right_negative_zero_fill(self, cpu_v5):
        """Test log_shift right: -16 >> 2 = 0x3FFC (zeros fill, NOT sign preserved)."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x02
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0xFF
        mem[cpu.pc + 4] = 0xF0  # -16 (0xFFF0)
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFE  # -2
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        # Logical shift: 0xFFF0 >> 2 = 0x3FFC (zeros fill from left)
        # This is the KEY difference from art_shift!
        assert result == 0x3FFC, f"Expected 0x3FFC (16380), got 0x{result:04X}"
    
    def test_log_shift_right_negative_ones(self, cpu_v5):
        """Test log_shift right: -1 >> 1 = 0x7FFF (zeros fill, NOT -1)."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x02
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0xFF
        mem[cpu.pc + 4] = 0xFF  # -1 (0xFFFF)
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFF  # -1
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        # Logical shift: 0xFFFF >> 1 = 0x7FFF (zeros fill)
        # This is the KEY difference from art_shift!
        assert result == 0x7FFF, f"Expected 0x7FFF (32767), got 0x{result:04X}"
    
    def test_log_shift_left_overflow(self, cpu_v5):
        """Test log_shift left with overflow: 0x8000 << 1 = 0x0000."""
        cpu = cpu_v5
        mem = cpu.mem
        
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x02
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0x80
        mem[cpu.pc + 4] = 0x00  # 0x8000
        mem[cpu.pc + 5] = 0x00
        mem[cpu.pc + 6] = 0x01
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        
        result = get_global_var(cpu, 112)
        # 0x8000 << 1 = 0x10000 & 0xFFFF = 0x0000
        assert result == 0x0000


# ============================================================================
# Comparison Tests (art_shift vs log_shift)
# ============================================================================

class TestShiftComparison:
    """Tests comparing art_shift and log_shift behavior."""
    
    def test_art_vs_log_positive_number(self, cpu_v5):
        """Test that art_shift and log_shift give same result for positive numbers."""
        # Positive numbers should give same result for both shifts
        cpu = cpu_v5
        mem = cpu.mem
        
        # art_shift 16, -2
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x03
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0x00
        mem[cpu.pc + 4] = 0x10
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFE
        mem[cpu.pc + 7] = 0x70
        
        cpu.command()
        art_result = get_global_var(cpu, 112)
        
        # log_shift 16, -2
        mem[cpu.pc] = 0xBE
        mem[cpu.pc + 1] = 0x02
        mem[cpu.pc + 2] = 0xF0
        mem[cpu.pc + 3] = 0x00
        mem[cpu.pc + 4] = 0x10
        mem[cpu.pc + 5] = 0xFF
        mem[cpu.pc + 6] = 0xFE
        mem[cpu.pc + 7] = 0x71
        
        cpu.command()
        log_result = get_global_var(cpu, 113)
        
        # For positive numbers, both should give 4
        assert art_result == 0x0004
        assert log_result == 0x0004
    
    def test_art_vs_log_negative_number(self, cpu_v5):
        """Test that art_shift and log_shift differ for negative numbers (right shift)."""
        cpu = cpu_v5
        mem = cpu.mem
        
        # Set up BOTH instructions at fixed addresses
        # art_shift -16, -2 at PC 0x20 (should give -4 = 0xFFFC)
        mem[0x20] = 0xBE
        mem[0x21] = 0x03  # art_shift
        mem[0x22] = 0xF0
        mem[0x23] = 0xFF
        mem[0x24] = 0xF0  # -16
        mem[0x25] = 0xFF
        mem[0x26] = 0xFE  # -2
        mem[0x27] = 0x70  # Store in global 112
        
        # log_shift -16, -2 at PC 0x28 (should give 0x3FFC = 16380)
        mem[0x28] = 0xBE
        mem[0x29] = 0x02  # log_shift
        mem[0x2A] = 0xF0
        mem[0x2B] = 0xFF
        mem[0x2C] = 0xF0  # -16
        mem[0x2D] = 0xFF
        mem[0x2E] = 0xFE  # -2
        mem[0x2F] = 0x71  # Store in global 113
        
        # Set PC to start of art_shift
        cpu.pc = 0x20
        
        cpu.command()
        art_result = get_global_var(cpu, 112)
        
        # Now run log_shift (PC should be at 0x28 now)
        cpu.command()
        log_result = get_global_var(cpu, 113)
        
        # art_shift preserves sign: -16 >> 2 = -4 = 0xFFFC
        assert art_result == 0xFFFC, f"art_shift expected 0xFFFC, got 0x{art_result:04X}"
        
        # log_shift zero-fills: 0xFFF0 >> 2 = 0x3FFC = 16380
        assert log_result == 0x3FFC, f"log_shift expected 0x3FFC, got 0x{log_result:04X}"
        
        # They should be DIFFERENT for negative numbers
        assert art_result != log_result, "art_shift and log_shift should differ for negative numbers"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
