# Z-Machine Opcode Test Fix Guide

## Current Status

**Total Tests:** 146
**Passing:** 116 (79%)
**Skipped:** 30 (21%) - Unimplemented opcodes
**Failing:** 0 (0%) ✓

---

## Implementation Status

The ZCpu implementation is **CORRECT**. All opcode implementations work as designed per the Z-machine specification.

---

## Quick Reference: Object Addresses

### V3 (9 bytes per object)

| Object | Address | Formula |
|--------|---------|---------|
| Object 1 | `base + 62` | `base + 62 + (1-1)*9` |
| Object 2 | `base + 71` | `base + 62 + (2-1)*9` |
| Object 3 | `base + 80` | `base + 62 + (3-1)*9` |

### V4+ (14 bytes per object)

| Object | Address | Formula |
|--------|---------|---------|
| Object 1 | `base + 126` | `base + 126 + (1-1)*14` |
| Object 2 | `base + 140` | `base + 126 + (2-1)*14` |
| Object 3 | `base + 154` | `base + 126 + (3-1)*14` |

---

## Quick Reference: Object Field Offsets

### V3 Object Fields

| Offset | Field | Size |
|--------|-------|------|
| 0-3 | Attributes | 4 bytes |
| 4 | Parent | 1 byte |
| 5 | Sibling | 1 byte |
| 6 | Child | 1 byte |
| 7-8 | Property table address | 2 bytes |

### V4+ Object Fields

| Offset | Field | Size |
|--------|-------|------|
| 0-5 | Attributes | 6 bytes |
| 6-7 | Parent | 2 bytes |
| 8-9 | Sibling | 2 bytes |
| 10-11 | Child | 2 bytes |
| 12-13 | Property table address | 2 bytes |

---

## Helper Functions

Use these helper functions from the test file:

```python
# Get/set global variables
val = get_global_var(cpu, N)
set_global_var(cpu, N, value)

# Get variable reference for store
store_ref = global_var_ref(N)  # Returns N + 16

# Convert between signed/unsigned
unsigned = i2s(signed_value)
signed = s2i(unsigned_value)
```

---

## Lessons Learned

1. **Read the Z-machine spec carefully** - Object table layout is specific
2. **Property defaults come FIRST** - This is easy to miss
3. **V3 property format is unique** - IDs before data
4. **V4+ uses 2-byte addresses** - Always use big-endian
5. **Object tree must be consistent** - Parent/child/sibling must match
6. **Check opcode formats** - LONG vs VARIABLE 2OP

---

## See Also

- `tests/test_encoding_guide.md` - Detailed operand encoding guide
- `tests/opcode_bug_report.md` - Implementation bug report (all fixed)
- `tests/test_final_summary.md` - Overall test status
