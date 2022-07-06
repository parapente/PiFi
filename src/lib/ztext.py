# -*- coding: utf-8

from array import array

__author__ = "Theofilos Intzoglou"
__date__ = "$24 Ιουν 2009 10:28:44 μμ$"


def decode_text(text_buffer: array, version: int, mem: array,
                abbreviation_table: int, is_abbreviation: bool,
                alphabet_table: int, unicode_table: int) -> str:
    z2 = [1, 2, 0]
    z3 = [2, 0, 1]
    z = [z2, z3]
    alphabet = 0         # Current alphabet
    prev_alphabet = 0    # Previous alphabet
    shift_next = 0       # Flag next character for shift
    abbrev_offset = 0
    abbrev_next = 0      # Flag next z-character as abbreviation
    ten_bit_z_char = 0
    ten_bit_next = 0     # Flag next z-character as part of ten bit z-character
    text = ""
    i = 0
    text_buffer_length = len(text_buffer)
    while (i < text_buffer_length):
        # Every two bytes we get three z-characters
        z_char1 = (text_buffer[i] & 124) >> 2
        z_char2 = ((text_buffer[i] & 3) << 3) | ((text_buffer[i+1] & 224) >> 5)
        z_char3 = (text_buffer[i+1] & 31)
        for z_char in [z_char1, z_char2, z_char3]:
            if ten_bit_next == 1:
                # First part of ten bit z-char
                ten_bit_z_char = z_char << 5
                ten_bit_next = 2
            elif ten_bit_next == 2:
                # Second part of ten bit z-char
                ten_bit_z_char |= z_char
                text += convert_from_zscii(ten_bit_z_char, mem, unicode_table)
                # Reset ten bit flag
                ten_bit_next = 0
                if ((version < 3) and (shift_next == 1)):
                    alphabet = prev_alphabet
                if (version >= 3):
                    alphabet = 0
            elif abbrev_next == 1:
                abbrev_offset += z_char * 2
                idx = 2 * ((mem[abbrev_offset] << 8) + mem[abbrev_offset + 1])
                new_buffer = array('B')
                eot = False
                while not(eot):
                    if (mem[idx] & 128) == 128:
                        eot = True
                    new_buffer.append(mem[idx])
                    new_buffer.append(mem[idx+1])
                    idx += 2
                text += decode_text(new_buffer, version, mem,
                                    abbreviation_table, True,
                                    alphabet_table, unicode_table)
                abbrev_next = 0
            elif ((version < 3) and (z_char >= 2) and (z_char <= 5)):
                # We need to shift or lock to another alphabet
                prev_alphabet = alphabet
                alphabet = z[z_char % 2][alphabet]
                if (z_char1 < 4):
                    shift_next = 1
            elif ((version >= 3) and ((z_char == 4) or (z_char == 5))):
                # We need to shift to a different alphabet
                # for the next z-character
                if (z_char == 4):
                    alphabet = 1
                else:
                    alphabet = 2
                shift_next = 1
            elif ((((version >= 3) and (z_char > 0) and (z_char < 4)) or
                   ((version == 2) and (z_char == 1))) and
                  not(is_abbreviation)):
                abbrev_offset = abbreviation_table + 32 * (z_char - 1) * 2
                abbrev_next = 1
            elif (z_char == 6) and (alphabet == 2):
                ten_bit_next = 1
            else:
                text += check_z_char(z_char, alphabet, version, mem,
                                     alphabet_table, unicode_table)
                if ((version < 3) and (shift_next == 1)):
                    alphabet = prev_alphabet
                if (version >= 3):
                    alphabet = 0
                shift_next = 0
        i += 2
    return text


def check_z_char(z_char: int, alphabet: int, version: int, mem: array,
                 alphabet_table: int, unicode_table: int) -> str:
    a2 = ['\n', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.',
          ',', '!', '?', '_', '#', '\'', '\"', '/', '\\', '-', ':', '(', ')']
    if z_char == 0:
        return " "
    elif (version == 1) and (z_char == 1):
        return "\n"
    else:
        if (version >= 5) and (alphabet_table != 0):
            return convert_from_zscii(mem[alphabet_table+alphabet*26+(z_char-6)], mem, unicode_table)
        elif (version == 1):
            a2.remove('\n')
            a2.insert(a2.index('-'), '<')
        if (alphabet == 0):
            return chr(ord('a')+z_char-6)
        elif (alphabet == 1):
            return chr(ord('A')+z_char-6)
        else:
            return a2[z_char-7]


def convert_from_zscii(zscii_char: int, mem: array, unicode_table: int) -> str:
    ut = [0xe4, 0xf6, 0xfc, 0xc4, 0xd6, 0xdc, 0xdf, 0xbb,
          0xab, 0xeb, 0xef, 0xff, 0xcb, 0xcf, 0xe1, 0xe9,
          0xed, 0xf3, 0xfa, 0xfd, 0xc1, 0xc9, 0xcd, 0xd3,
          0xda, 0xdd, 0xe0, 0xe8, 0xec, 0xf2, 0xf9, 0xc0,
          0xc8, 0xcc, 0xd2, 0xd9, 0xe2, 0xea, 0xee, 0xf4,
          0xfb, 0xc2, 0xca, 0xce, 0xd4, 0xdb, 0xe5, 0xc5,
          0xf8, 0xd8, 0xe3, 0xf1, 0xf5, 0xc3, 0xd1, 0xd5,
          0xe6, 0xc6, 0xe7, 0xc7, 0xfe, 0xf0, 0xde, 0xd0,
          0xa3, 0x153, 0x152, 0xa1, 0xbf]
    if zscii_char == 0:
        return ''
    elif zscii_char == 9:
        return '\t'
    elif zscii_char == 11:
        return ' '  # This should be a 'sentence space'
    elif zscii_char == 13:
        return '\n'
    elif (zscii_char >= 32) and (zscii_char <= 126):
        return chr(zscii_char)
    elif (unicode_table == 0):  # Standard unicode table
        print("TB -", zscii_char)
        if zscii_char <= 255:
            if zscii_char <= 223:
                return chr(ut[zscii_char-155])
            else:
                return '?'
        else:
            return chr(zscii_char)
    else:  # Story file's unicode table
        n = mem[unicode_table]
        i = 0
        while n > 0:  # Read table from mem to ut
            uc = mem[unicode_table+2*i] << 8
            uc += mem[unicode_table+2*i+1]
            ut[i] = uc
            i += 1
            n -= 1
        return chr(ut[zscii_char-155])


def encode_text(text: list, version: int, mem: array, alphabet_table: int, unicode_table) -> array:
    a0 = dict()
    a1 = dict()
    a2 = dict()
    prepare_dicts(a0, a1, a2, version, mem, alphabet_table)

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
                raise ValueError(
                    "Unexpected character in text '" + text[i] + "'")
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
        buf.extend([5]*(buffer_limit - char_count))
    output = convert_to_z_bytes(buf)
    return array('B', output)


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


def prepare_dicts(a0: dict, a1: dict, a2: dict, version: int, mem: array,
                  alphabet_table: int) -> None:
    if version >= 5 and alphabet_table:
        i = 0
        for x in range(26):
            a0[mem[alphabet_table+x]] = 6 + i
            i += 1
        i = 0
        for x in range(26, 52):
            a1[mem[alphabet_table+x]] = 6 + i
            i += 1
        i = 0
        for x in range(52, 78):
            a2[mem[alphabet_table+x]] = 6 + i
            i += 1
    else:
        i = 0
        for x in range(ord('a'), ord('z') + 1):
            a0[x] = 6 + i
            i += 1
        i = 0
        for x in range(ord('A'), ord('Z') + 1):
            a1[x] = 6 + i
            i += 1
        if version == 1:
            i = 0
            for x in [' ', '0', '1', '2', '3', '4', '5', '6', '7', '8',
                      '9', '.', ',', '!', '?', '_', '#', '\'', '\"', '/',
                      '\\', '<', '-', ':', '(', ')']:
                a2[ord(x)] = 6 + i
                i += 1
        else:
            i = 0
            for x in [' ', '\n', '0', '1', '2', '3', '4', '5', '6', '7',
                      '8', '9', '.', ',', '!', '?', '_', '#', '\'', '\"',
                      '/', '\\', '-', ':', '(', ')']:
                a2[ord(x)] = 6 + i
                i += 1
