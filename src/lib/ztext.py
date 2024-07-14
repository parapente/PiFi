# -*- coding: utf-8

from array import array

from lib.memory import ZMemory

__author__ = "Theofilos Intzoglou"
__date__ = "$24 Ιουν 2009 10:28:44 μμ$"


def decode_text(
    text_buffer: array,
    version: int,
    abbreviation_table: int,
    is_abbreviation: bool,
    alphabet_table: int,
    unicode_table: int,
) -> str:
    mem = ZMemory().mem
    z2 = [1, 2, 0]
    z3 = [2, 0, 1]
    z = [z2, z3]
    alphabet = 0  # Current alphabet
    prev_alphabet = 0  # Previous alphabet
    shift_next = 0  # Flag next character for shift
    abbrev_offset = 0
    abbrev_next = 0  # Flag next z-character as abbreviation
    ten_bit_z_char = 0
    ten_bit_next = 0  # Flag next z-character as part of ten bit z-character
    text = ""
    i = 0
    text_buffer_length = len(text_buffer)
    while i < text_buffer_length:
        # Every two bytes we get three z-characters
        z_char1 = (text_buffer[i] & 124) >> 2
        z_char2 = ((text_buffer[i] & 3) << 3) | ((text_buffer[i + 1] & 224) >> 5)
        z_char3 = text_buffer[i + 1] & 31
        for z_char in [z_char1, z_char2, z_char3]:
            if ten_bit_next == 1:
                # First part of ten bit z-char
                ten_bit_z_char = z_char << 5
                ten_bit_next = 2
            elif ten_bit_next == 2:
                # Second part of ten bit z-char
                ten_bit_z_char |= z_char
                text += convert_from_zscii(ten_bit_z_char, unicode_table)
                # Reset ten bit flag
                ten_bit_next = 0
                if (version < 3) and (shift_next == 1):
                    alphabet = prev_alphabet
                if version >= 3:
                    alphabet = 0
            elif abbrev_next == 1:
                abbrev_offset += z_char * 2
                idx = 2 * ((mem[abbrev_offset] << 8) + mem[abbrev_offset + 1])
                new_buffer = array("B")
                eot = False
                while not (eot):
                    if (mem[idx] & 128) == 128:
                        eot = True
                    new_buffer.append(mem[idx])
                    new_buffer.append(mem[idx + 1])
                    idx += 2
                text += decode_text(
                    new_buffer,
                    version,
                    abbreviation_table,
                    True,
                    alphabet_table,
                    unicode_table,
                )
                abbrev_next = 0
            elif (version < 3) and (z_char >= 2) and (z_char <= 5):
                # We need to shift or lock to another alphabet
                prev_alphabet = alphabet
                alphabet = z[z_char % 2][alphabet]
                if z_char1 < 4:
                    shift_next = 1
            elif (version >= 3) and ((z_char == 4) or (z_char == 5)):
                # We need to shift to a different alphabet
                # for the next z-character
                if z_char == 4:
                    alphabet = 1
                else:
                    alphabet = 2
                shift_next = 1
            elif (
                ((version >= 3) and (z_char > 0) and (z_char < 4))
                or ((version == 2) and (z_char == 1))
            ) and not (is_abbreviation):
                abbrev_offset = abbreviation_table + 32 * (z_char - 1) * 2
                abbrev_next = 1
            elif (z_char == 6) and (alphabet == 2):
                ten_bit_next = 1
            else:
                text += check_z_char(
                    z_char, alphabet, version, alphabet_table, unicode_table
                )
                if (version < 3) and (shift_next == 1):
                    alphabet = prev_alphabet
                if version >= 3:
                    alphabet = 0
                shift_next = 0
        i += 2
    return text


def check_z_char(
    z_char: int,
    alphabet: int,
    version: int,
    alphabet_table: int,
    unicode_table: int,
) -> str:
    mem = ZMemory().mem
    # fmt: off
    a2 = [
        "\n", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        ".", ",", "!", "?", "_", "#", "'", '"', "/", "\\", "-",
        ":", "(", ")",
    ]
    # fmt: on
    if z_char == 0:
        return " "
    elif (version == 1) and (z_char == 1):
        return "\n"
    else:
        if (version >= 5) and (alphabet_table != 0):
            return convert_from_zscii(
                mem[alphabet_table + alphabet * 26 + (z_char - 6)], unicode_table
            )
        elif version == 1:
            a2.remove("\n")
            a2.insert(a2.index("-"), "<")
        if alphabet == 0:
            return chr(ord("a") + z_char - 6)
        elif alphabet == 1:
            return chr(ord("A") + z_char - 6)
        else:
            return a2[z_char - 7]


def convert_from_zscii(zscii_char: int, unicode_table: int) -> str:
    mem = ZMemory().mem
    # fmt: off
    ut = [
        0xE4, 0xF6, 0xFC, 0xC4, 0xD6, 0xDC, 0xDF, 0xBB,
        0xAB, 0xEB, 0xEF, 0xFF, 0xCB, 0xCF, 0xE1, 0xE9,
        0xED, 0xF3, 0xFA, 0xFD, 0xC1, 0xC9, 0xCD, 0xD3,
        0xDA, 0xDD, 0xE0, 0xE8, 0xEC, 0xF2, 0xF9, 0xC0,
        0xC8, 0xCC, 0xD2, 0xD9, 0xE2, 0xEA, 0xEE, 0xF4,
        0xFB, 0xC2, 0xCA, 0xCE, 0xD4, 0xDB, 0xE5, 0xC5,
        0xF8, 0xD8, 0xE3, 0xF1, 0xF5, 0xC3, 0xD1, 0xD5,
        0xE6, 0xC6, 0xE7, 0xC7, 0xFE, 0xF0, 0xDE, 0xD0,
        0xA3, 0x153, 0x152, 0xA1, 0xBF,
    ]
    # fmt: on
    if zscii_char == 0:
        return ""
    elif zscii_char == 9:
        return "\t"
    elif zscii_char == 11:
        return " "  # This should be a 'sentence space'
    elif zscii_char == 13:
        return "\n"
    elif (zscii_char >= 32) and (zscii_char <= 126):
        return chr(zscii_char)
    elif unicode_table == 0:  # Standard unicode table
        print("TB -", zscii_char)
        if zscii_char <= 255:
            if zscii_char <= 223:
                return chr(ut[zscii_char - 155])
            else:
                return "?"
        else:
            return chr(zscii_char)
    else:  # Story file's unicode table
        n = mem[unicode_table]
        i = 0
        while n > 0:  # Read table from mem to ut
            uc = mem[unicode_table + 2 * i] << 8
            uc += mem[unicode_table + 2 * i + 1]
            ut[i] = uc
            i += 1
            n -= 1
        return chr(ut[zscii_char - 155])


def encode_text(text: list, version: int, alphabet_table: int, unicode_table) -> array:
    a0 = dict()
    a1 = dict()
    a2 = dict()
    prepare_dicts(a0, a1, a2, version, alphabet_table)

    string_length = len(text)
    buf = []
    if version < 4:
        buffer_limit = 6
    else:
        buffer_limit = 9

    i = 0
    char_count = 0
    while i < string_length and char_count < buffer_limit:
        a2_is_used = False
        if text[i] == 32:  # if it is space character
            code = 0
        else:
            item = text[i]
            if item in a0:
                code = a0[item]
            elif item in a1:
                code = a1[item]
            elif item in a2:
                a2_is_used = True
                code = a2[item]
            else:
                raise ValueError("Unexpected character in text '" + text[i] + "'")
        if a2_is_used:
            if version < 3:
                shift_char = 3
            else:
                shift_char = 5

            if char_count < buffer_limit - 1:
                buf.extend([shift_char, code])
                char_count += 2
            else:
                buf.append(shift_char)
                char_count += 1
        else:
            buf.append(code)
            char_count += 1
        i += 1

    if char_count < buffer_limit:
        buf.extend([5] * (buffer_limit - char_count))
    output = convert_to_z_bytes(buf)
    return array("B", output)


def convert_to_z_bytes(buf: list) -> list:
    output = []
    byte_count = 1
    b1 = 0
    b2 = 0
    for z_char in buf:
        if (byte_count % 3) == 1:
            b1 = z_char << 2
        elif (byte_count % 3) == 2:
            p1 = z_char >> 3
            p2 = (z_char & 7) << 5
            b1 += p1
            b2 = p2
        else:
            b2 += z_char
            if byte_count == len(buf):
                b1 |= 128
            output.append(b1)
            output.append(b2)
        byte_count += 1
    return output


def prepare_dicts(
    a0: dict, a1: dict, a2: dict, version: int, alphabet_table: int
) -> None:
    mem = ZMemory().mem
    if version >= 5 and alphabet_table:
        i = 0
        for x in range(26):
            a0[mem[alphabet_table + x]] = 6 + i
            i += 1
        i = 0
        for x in range(26, 52):
            a1[mem[alphabet_table + x]] = 6 + i
            i += 1
        i = 0
        for x in range(52, 78):
            a2[mem[alphabet_table + x]] = 6 + i
            i += 1
    else:
        i = 0
        for x in range(ord("a"), ord("z") + 1):
            a0[x] = 6 + i
            i += 1
        i = 0
        for x in range(ord("A"), ord("Z") + 1):
            a1[x] = 6 + i
            i += 1
        if version == 1:
            i = 0
            # fmt: off
            for x in [
                " ", "0", "1", "2", "3", "4", "5", "6", "7", "8",
                "9", ".", ",", "!", "?", "_", "#", "'", '"', "/",
                "\\", "<", "-", ":", "(", ")",
            ]:
            # fmt: on
                a2[ord(x)] = 6 + i
                i += 1
        else:
            i = 0
            # fmt: off
            for x in [
                " ", "\n", "0", "1", "2", "3", "4", "5", "6", "7", "8",
                "9", ".", ",", "!", "?", "_", "#", "'", '"', "/", "\\",
                "-", ":", "(", ")",
            ]:
            # fmt: on
                a2[ord(x)] = 6 + i
                i += 1
