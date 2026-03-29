# Z-Machine Test Encoding Guide

## Understanding Operand Encoding

The Z-machine uses compact operand encoding to save space. This guide explains how to correctly encode operands in tests.

### Variable 2OP Format (opcode 0xC0-0xDF)

```
Byte 0: Opcode (0xC0 | opcode_number)
Byte 1: Type byte (8 bits encoding 4 operand types)
Bytes 2+: Operands and store variable
```

### Type Byte Encoding

The type byte encodes 4 operand types in 8 bits (2 bits per operand):

| Bits | Operand | Encoding |
|------|---------|----------|
| 7-6  | Operand 1 | 00=large, 01=small, 10=variable, 11=omit |
| 5-4  | Operand 2 | 00=large, 01=small, 10=variable, 11=omit |
| 3-2  | Operand 3 | 00=large, 01=small, 10=variable, 11=omit |
| 1-0  | Operand 4 | 00=large, 01=small, 10=variable, 11=omit |

**Operand sizes:**
- Large constant: 2 bytes
- Small constant: 1 byte
- Variable: 1 byte (specifies WHICH variable)
- Omitted: 0 bytes

### Common Type Byte Values

| Type Byte | Binary | Meaning | Use Case |
|-----------|--------|---------|----------|
| 0x0F | 00001111 | 2 large + 2 omitted | add, sub, mul, div, mod, and, or |
| 0x4F | 01001111 | 1 small + 1 large + 2 omitted | jl, jg with small constants |
| 0x8F | 10001111 | 1 variable + 1 large + 2 omitted | store, dec_chk, inc_chk |
| 0x50 | 01010000 | 2 small + 2 large | add with small constants |

### Variable Operand Behavior

**CRITICAL:** When using variable operands (optype=10):

- The operand byte specifies WHICH variable (0=stack, 1-15=local, 16-255=global)
- The VALUE is READ from that variable
- To use global variable N as an operand:
  1. Pre-initialize global_vars[N-16] = desired_value
  2. Use operand byte = N

**Example for `store global100, 0x1234`:**
```python
# Setup: global 100's value must be 100 (the target variable number)
set_global_var(cpu, 100, 100)

# Encode: variable + large constant + 2 omitted = 0x8F
mem[cpu.pc] = 0xCD  # store opcode
mem[cpu.pc + 1] = 0x8F  # type byte
mem[cpu.pc + 2] = 0x64  # Use global 100 (reads VALUE = 100)
mem[cpu.pc + 3] = 0x12  # Value high byte
mem[cpu.pc + 4] = 0x34  # Value low byte
```

## Test Templates

### Template: 2 Large Constants (add, sub, mul, etc.)

```python
def test_op_basic(self, cpu_v3):
    """Test opcode with 2 large constants."""
    cpu = cpu_v3
    mem = cpu.mem
    mem[cpu.pc] = 0xD4  # opcode (0xC0 | 20 for add)
    mem[cpu.pc + 1] = 0x0F  # 2 large + 2 omitted
    mem[cpu.pc + 2] = 0x00
    mem[cpu.pc + 3] = 100  # Operand 1
    mem[cpu.pc + 4] = 0x00
    mem[cpu.pc + 5] = 200  # Operand 2
    mem[cpu.pc + 6] = 0x70  # Store in global 112

    cpu.command()

    result = get_global_var(cpu, 112)
    assert result == 300
```

### Template: Variable + Large Constant (store, dec_chk, etc.)

```python
def test_op_variable(self, cpu_v3):
    """Test opcode with variable operand."""
    cpu = cpu_v3
    mem = cpu.mem

    # Pre-initialize the variable
    set_global_var(cpu, 100, 100)  # Set global 100's value to 100

    mem[cpu.pc] = 0xCD  # opcode (0xC0 | 13 for store)
    mem[cpu.pc + 1] = 0x8F  # variable + large + 2 omitted
    mem[cpu.pc + 2] = 0x64  # Global 100 (reads VALUE = 100)
    mem[cpu.pc + 3] = 0x12  # Value high
    mem[cpu.pc + 4] = 0x34  # Value low

    cpu.command()

    result = get_global_var(cpu, 100)
    assert result == 0x1234
```

### Template: 1OP with Large Constant

```python
def test_1op_large(self, cpu_v3):
    """Test 1OP with large constant."""
    cpu = cpu_v3
    mem = cpu.mem
    # 1OP format is different - operand encoding in instruction byte
    mem[cpu.pc] = 0x80  # jz with large constant
    mem[cpu.pc + 1] = 0x00  # Large constant high
    mem[cpu.pc + 2] = 0x00  # Large constant low (value 0)
    mem[cpu.pc + 3] = 0xC2  # Branch if true, offset 2

    cpu.command()
    # Branch should be taken (0 == 0)
```

### Template: 1OP with Variable

```python
def test_1op_variable(self, cpu_v3):
    """Test 1OP with variable operand."""
    cpu = cpu_v3
    mem = cpu.mem

    # Pre-initialize the variable
    set_global_var(cpu, 112, 0)  # Set global 112's value to 0

    mem[cpu.pc] = 0x80  # jz
    mem[cpu.pc + 1] = 0x70  # Global 112 (reads VALUE = 0)
    mem[cpu.pc + 2] = 0xC2  # Branch if true

    cpu.command()
    # Branch should be taken (0 == 0)
```

## Object Table Setup

### V3 Object Structure (9 bytes per object)

```
Offset 0-3: Attributes (4 bytes)
Offset 4:    Parent object number
Offset 5:    Sibling object number
Offset 6:    Child object number
Offset 7-8:  Property table address (2 bytes)
```

### V3 Memory Layout

```
0x40-0x7D: Property defaults table (62 bytes = 31 × 2)
0x7E-0x86: Object 1 (9 bytes)
0x87-0x8F: Object 2 (9 bytes)
0x90-0x98: Object 3 (9 bytes)
```

### V4+ Object Structure (14 bytes per object)

```
Offset 0-5:  Attributes (6 bytes)
Offset 6-7:  Parent object number (2 bytes)
Offset 8-9:  Sibling object number (2 bytes)
Offset 10-11: Child object number (2 bytes)
Offset 12-13: Property table address (2 bytes)
```

### V4+ Memory Layout

```
0x60-0xDD: Property defaults table (126 bytes = 63 × 2)
0xDE-0xEB: Object 1 (14 bytes)
0xEC-0xF9: Object 2 (14 bytes)
0xFA-0x107: Object 3 (14 bytes)
```

### Example: Setting Up Object Tree

```python
def test_jin_true(self, cpu_v3):
    """Test jin: object is child of another."""
    cpu = cpu_v3
    mem = cpu.mem
    base = cpu.header.obj_table
    
    # Object addresses for V3
    obj1_addr = base + 62  # 0x7E
    obj2_addr = base + 71  # 0x87
    obj3_addr = base + 80  # 0x90
    
    # Set up object tree: obj1→child=obj2, obj2→parent=obj1, obj2→child=obj3
    mem[obj1_addr + 6] = 2      # obj1's child = obj2
    mem[obj2_addr + 4] = 1      # obj2's parent = obj1
    mem[obj2_addr + 6] = 3      # obj2's child = obj3
    mem[obj3_addr + 4] = 2      # obj3's parent = obj2
    
    # Now jin obj3, obj2 will succeed
    mem[cpu.pc] = 0xC6  # jin (variable format)
    mem[cpu.pc + 1] = 0x0F  # 2 large constants + 2 omitted
    mem[cpu.pc + 2] = 0x00
    mem[cpu.pc + 3] = 0x03  # obj3
    mem[cpu.pc + 4] = 0x00
    mem[cpu.pc + 5] = 0x02  # obj2
    mem[cpu.pc + 6] = 0xC2  # Branch if true

    cpu.command()
    assert cpu.pc > start_pc + 7  # Branch taken
```

## Property Table Setup (V3)

### V3 Property Table Format

```
Byte 0:   Number of properties (N)
Bytes 1-2N: Property IDs (2 bytes each, big-endian)
Bytes 2N+1+: Property data entries
  - Size byte: (size << 5) | property_number
  - Data bytes: property value
```

### Example: Setting Up Property Table

```python
def test_put_prop(self, cpu_v3):
    """Test put_prop: write property value."""
    cpu = cpu_v3
    mem = cpu.mem
    base = cpu.header.obj_table
    obj1_addr = base + 62
    
    # Property table at 0xA0
    mem[obj1_addr + 7] = 0x00  # prop table high
    mem[obj1_addr + 8] = 0xA0  # prop table low
    
    # Property table format:
    mem[0xA0] = 1              # 1 property
    mem[0xA1] = 0x00           # Property ID high
    mem[0xA2] = 0x01           # Property ID low (property 1)
    mem[0xA3] = (2 << 5) | 1   # Size byte: 2 bytes, property 1
    mem[0xA4] = 0x00           # Value high
    mem[0xA5] = 0x00           # Value low
    
    # put_prop obj1, 1, 0x1234
    mem[cpu.pc] = 0xE3  # put_prop
    mem[cpu.pc + 1] = 0x03  # 3 large constants
    mem[cpu.pc + 2] = 0x00
    mem[cpu.pc + 3] = 0x01  # Object 1
    mem[cpu.pc + 4] = 0x00
    mem[cpu.pc + 5] = 0x01  # Property 1
    mem[cpu.pc + 6] = 0x12
    mem[cpu.pc + 7] = 0x34

    cpu.command()
    assert mem[0xA4] == 0x12
    assert mem[0xA5] == 0x34
```

## Common Opcode Encodings

| Opcode | Name | Typical Type Byte | Notes |
|--------|------|------------------|-------|
| 2OP:1 | je | 0x0F, 0x4F, 0x8F | 2-4 operands for comparison |
| 2OP:2-3 | jl, jg | 0x0F, 0x4F | Signed comparison |
| 2OP:4-5 | dec_chk, inc_chk | 0x8F | variable + value |
| 2OP:8-9 | or, and | 0x0F | Bitwise operations |
| 2OP:13 | store | 0x8F | variable + value |
| 2OP:20-24 | add, sub, mul, div, mod | 0x0F | Arithmetic |
| 1OP:128 | jz | varies | Jump if zero |
| 1OP:133-134 | inc, dec | 0x70-0x7F | Variable operand in low nibble |
| VAR:232 | push | 0x80 | 1 large constant |
| VAR:231 | random | 0x80 | 1 large constant |

## Helper Functions

The test file provides these helper functions:

```python
# Get value of global variable N
val = get_global_var(cpu, N)

# Set value of global variable N
set_global_var(cpu, N, value)

# Get variable reference number for store
store_ref = global_var_ref(N)  # Returns N + 16

# Convert signed to unsigned 16-bit
unsigned = i2s(signed_value)

# Convert unsigned to signed 16-bit
signed = s2i(unsigned_value)
```

## Debugging Tips

1. **Check PC advancement**: After `cpu.command()`, verify PC advanced correctly
2. **Verify operand reading**: Print `cpu.ops[:cpu.numops]` to see what was read
3. **Check store location**: Verify the store variable byte is AFTER all operands
4. **Global variable initialization**: Remember to `set_global_var()` before using as variable operand
5. **Object addresses**: For V3, use `base + 62 + (obj_num - 1) * 9`
6. **Property format**: V3 stores property IDs before property data

## Summary

- **Type byte determines operand sizes** - use 0x0F for "2 large constants + 2 omitted"
- **Variable operands read VALUES** - pre-initialize global variables with desired values
- **Store variable comes last** - after all operand bytes
- **1OP encoding is different** - operand type encoded in instruction byte bits 6-5
- **Object tables have property defaults first** - V3: 62 bytes, V4+: 126 bytes
- **Property tables store IDs before data** - especially important for V3
