# -*- coding: utf-8

from array import array

__author__ = "Theofilos Intzoglou"
__date__ = "$24 Ιουν 2009 10:28:44 μμ$"


def decode_text(text_buffer, version, mem, abbrev, isabbrev, alpha_table, unicode_table):
    z2 = [1, 2, 0]
    z3 = [2, 0, 1]
    z = [z2, z3]
    a = 0           # Current alphabet
    prev_a = 0      # Previous alphabet
    shift_next = 0
    abbrev_offset = 0
    abbrev_next = 0
    tenbit = 0
    tenbit_next = 0
    text = ""
    i = 0
    l = len(text_buffer)
    while (i < l):
        b1 = (text_buffer[i] & 124) >> 2
        b2 = ((text_buffer[i] & 3) << 3) | ((text_buffer[i+1] & 224) >> 5)
        b3 = (text_buffer[i+1] & 31)
        bz = [b1, b2, b3]
        for b in bz:
            if tenbit_next == 1:
                tenbit = b << 5
                tenbit_next = 2
            elif tenbit_next == 2:
                tenbit |= b
                # print "Tenbit:", tenbit
                text += convert_from_zscii(tenbit, mem, unicode_table)
                tenbit_next = 0
                if ((version < 3) and (shift_next == 1)):
                    a = prev_a
                if (version >= 3):
                    a = 0
            elif abbrev_next == 1:
                abbrev_offset += b * 2
                idx = 2 * ((mem[abbrev_offset] << 8) + mem[abbrev_offset + 1])
                newbuf = array('B')
                eot = False
                while not(eot):
                    if (mem[idx] & 128) == 128:
                        eot = True
                    newbuf.append(mem[idx])
                    newbuf.append(mem[idx+1])
                    idx += 2
                text += decode_text(newbuf, version, mem,
                                    abbrev, True, alpha_table, unicode_table)
                abbrev_next = 0
            elif ((version < 3) and (b >= 2) and (b <= 5)):
                # We need to shift or lock to another alphabet
                prev_a = a
                a = z[b % 2, a]
                if (b1 < 4):
                    shift_next = 1
            elif ((version >= 3) and ((b == 4) or (b == 5))):
                # We need to shift to a different alphabet for the next zchar
                if (b == 4):
                    a = 1
                else:
                    a = 2
                shift_next = 1
            elif ((((version >= 3) and (b > 0) and (b < 4)) or ((version == 2) and (b == 1))) and not(isabbrev)):
                abbrev_offset = abbrev + 32 * (b - 1) * 2
                abbrev_next = 1
            elif (b == 6) and (a == 2):
                tenbit_next = 1
            else:
                text += check_zchar(b, a, version, mem,
                                    alpha_table, unicode_table)
                if ((version < 3) and (shift_next == 1)):
                    a = prev_a
                if (version >= 3):
                    a = 0
                shift_next = 0
        i += 2
    return text


def check_zchar(c, a, ver, mem, alpha_table, unicode_table):
    a2 = ['\n', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.',
          ',', '!', '?', '_', '#', '\'', '\"', '/', '\\', '-', ':', '(', ')']
    if c == 0:
        return " "
    elif (ver == 1) and (c == 1):
        return "\n"
    else:
        if (ver >= 5) and (alpha_table != 0):
            return convert_from_zscii(mem[alpha_table+a*26+(c-6)], mem, unicode_table)
        elif (ver == 1):
            a2.remove('\n')
            a2.insert(a2.index('-'), '<')
        if (a == 0):
            return chr(ord('a')+c-6)
        elif (a == 1):
            return chr(ord('A')+c-6)
        else:
            return a2[c-7]


def convert_from_zscii(tb, mem, uni_table):
    ut = [0xe4, 0xf6, 0xfc, 0xc4, 0xd6, 0xdc, 0xdf, 0xbb,
          0xab, 0xeb, 0xef, 0xff, 0xcb, 0xcf, 0xe1, 0xe9,
          0xed, 0xf3, 0xfa, 0xfd, 0xc1, 0xc9, 0xcd, 0xd3,
          0xda, 0xdd, 0xe0, 0xe8, 0xec, 0xf2, 0xf9, 0xc0,
          0xc8, 0xcc, 0xd2, 0xd9, 0xe2, 0xea, 0xee, 0xf4,
          0xfb, 0xc2, 0xca, 0xce, 0xd4, 0xdb, 0xe5, 0xc5,
          0xf8, 0xd8, 0xe3, 0xf1, 0xf5, 0xc3, 0xd1, 0xd5,
          0xe6, 0xc6, 0xe7, 0xc7, 0xfe, 0xf0, 0xde, 0xd0,
          0xa3, 0x153, 0x152, 0xa1, 0xbf]
    if tb == 0:
        return ''
    elif tb == 9:
        return '\t'
    elif tb == 11:
        return ' '  # This should be a 'sentense space'
    elif tb == 13:
        return '\n'
    elif (tb >= 32) and (tb <= 126):
        return chr(tb)
    elif (uni_table == 0):  # Standard unicode table
        print("TB -", tb)
        if tb <= 255:
            if tb <= 223:
                return chr(ut[tb-155])
            else:
                return '?'
        else:
            return chr(tb)
    else:  # Story file's unicode table
        n = mem[uni_table]
        i = 0
        while n > 0:  # Read table from mem to ut
            uc = mem[uni_table+2*i] << 8
            uc += mem[uni_table+2*i+1]
            ut[i] = uc
            i += 1
            n -= 1
        return chr(ut[tb-155])


def encode_text(text, version, mem, abbrev, isabbrev, alpha_table, unicode_table):
    a2 = ['\n', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.',
          ',', '!', '?', '_', '#', '\'', '\"', '/', '\\', '-', ':', '(', ')']
    t = str(text)
    l = len(t)
    j = 1
    buf = []
    b1 = 0
    b2 = 0
    if (version == 1):
        a2.remove('\n')
        a2.insert(a2.index('-'), '<')
    for i in range(l):
        c = t[i].lower()
        if (c >= 'a') and (c <= 'z'):
            n = (ord(c) - ord('a')) + 6
            if (j % 3) == 1:
                b1 = n << 2
            elif (j % 3) == 2:
                p1 = n >> 3
                p2 = (n & 7) << 5
                b1 += p1
                b2 = p2
            else:
                b2 += n
                buf.append(b1)
                buf.append(b2)
            j += 1
        elif c in a2:  # Char is symbol in standard alphabet
            if version < 3:
                zc = 3
            else:
                zc = 5
            n = a2.index(c) + 7
            if (j % 3) == 1:
                b1 = zc << 2
                p1 = n >> 3
                p2 = (n & 7) << 5
                b1 += p1
                b2 = p2
            elif (j % 3) == 2:
                p1 = zc >> 3
                p2 = (zc & 7) << 5
                b1 += p1
                b2 = p2
                b2 += n
                buf.append(b1)
                buf.append(b2)
            else:
                b2 += zc
                buf.append(b1)
                buf.append(b2)
                b1 = n << 2
            j += 2
    if (j % 3) == 1:
        b1 |= 128
    elif (j % 3) == 2:
        p1 = 5 >> 3
        p2 = (5 & 7) << 5
        b1 += p1
        b1 |= 128
        b2 = p2
        b2 += 5
    else:
        b1 |= 128
        b2 += 5
    buf.append(b1)
    buf.append(b2)
    print(buf)
