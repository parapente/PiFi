from typing import cast
import pytest
from lib.container import initialize_container
from lib.container.container import Container
from lib.header import ZHeader
from lib.memory import ZMemory
from src.lib.ztext import decode_text, encode_text, encode_to_zscii


@pytest.fixture
def decode_text_data():
    return [
        [1, "", []],
        [
            1,
            "This is a test!",
            [0xB, 0x2D, 0x3B, 0x0, 0x3B, 0x0, 0x18, 0x19, 0x2B, 0x19, 0xE, 0x65],
        ],
        [
            2,
            "This is a test!",
            [0xB, 0x2D, 0x3B, 0x0, 0x3B, 0x0, 0x18, 0x19, 0x2B, 0x19, 0xE, 0x85],
        ],
        [
            3,
            "This is a test!",
            [0x13, 0x2D, 0x3B, 0x0, 0x3B, 0x0, 0x18, 0x19, 0x2B, 0x19, 0x16, 0x85],
        ],
        [
            5,
            "This is a test!",
            [0x13, 0x2D, 0x3B, 0x0, 0x3B, 0x0, 0x18, 0x19, 0x2B, 0x19, 0x16, 0x85],
        ],
        # shift and lock tests
        [1, "", [0x8, 0x42, 0x8, 0x42, 0x8, 0x42]],
        [1, "", [0x10, 0x84, 0x8, 0x42, 0xC, 0x63]],
        [1, "", [0x10, 0x84, 0x8, 0x42, 0x14, 0xA5]],
        [1, "THIS", [0x13, 0x2D, 0x3B, 0x5]],
        [1, "<", [0x17, 0x65]],
        [1, "\n", [0x4, 0xA5]],
        [2, "\n", [0x14, 0xE5]],
        [1, "", [0x14, 0xC0]],
    ]


@pytest.fixture
def encode_text_data():
    return [
        [1, "hello"],
        [2, "hello"],
        [3, "hello"],
        [4, "hello"],
        [5, "hello"],
        [1, "hellooooo"],
        [2, "HELLO"],
        [3, "this is a test"],
        [4, "this is a test"],
    ]


def test_ztext_decode_text(decode_text_data):
    container = initialize_container()
    # Create dummy empty 1k memory
    memory = cast(ZMemory, container.resolve("ZMemory"))
    memory.mem = bytearray()
    memory.mem.extend([0] * 1024)

    mem = memory.mem
    for data in decode_text_data:
        version, text, z_chars = data
        text_buffer = bytearray(z_chars)
        print(data)
        header = cast(ZHeader, container.resolve("ZHeader"))
        header.version = version
        assert decode_text(text_buffer) == text
    Container.destroy()


def test_ztext_encode_text(encode_text_data):
    container = initialize_container()
    # Create dummy empty 1k memory
    memory = cast(ZMemory, container.resolve("ZMemory"))
    memory.mem = bytearray()
    memory.mem.extend([0] * 1024)

    for data in encode_text_data:
        version, text = data
        decoded_text = [ord(x) for x in text]
        header = cast(ZHeader, container.resolve("ZHeader"))
        header.version = version
        encoded_string = encode_text(decoded_text)
        decoded_string = decode_text(encoded_string)
        if version < 4:
            assert decoded_string == text[:6].lower()
        else:
            assert decoded_string == text[:9].lower()
    Container.destroy()


@pytest.fixture
def encode_to_zscii_data():
    return [
        # Basic ASCII text
        ("Hello", [72, 101, 108, 108, 111]),
        ("Test!", [84, 101, 115, 116, 33]),
        ("hello world", [104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]),
        # Control characters
        ("\n", [13]),
        ("\t", [9]),
        (" ", [32]),
        # Mixed text with control characters
        ("Hello\nWorld", [72, 101, 108, 108, 111, 13, 87, 111, 114, 108, 100]),
        # Numbers and punctuation
        ("Test 123!", [84, 101, 115, 116, 32, 49, 50, 51, 33]),
        ("Hello, World!", [72, 101, 108, 108, 111, 44, 32, 87, 111, 114, 108, 100, 33]),
        # Extended Latin characters
        ("café", [99, 97, 102, 170]),
        ("naïve", [110, 97, 165, 118, 101]),
        ("über", [157, 98, 101, 114]),
        ("señor", [115, 101, 206, 111, 114]),
        # German umlauts
        ("Äpfel", [158, 112, 102, 101, 108]),
        ("Öl", [159, 108]),
        ("Übung", [160, 98, 117, 110, 103]),
        # French accents
        ("été", [170, 116, 170]),
        ("à la carte", [181, 32, 108, 97, 32, 99, 97, 114, 116, 101]),
        # Nordic characters
        ("åre", [201, 114, 101]),
        ("ÆØÅ", [211, 204, 202]),
        # British/特殊 characters
        ("£5", [218, 53]),
        ("thþ", [116, 104, 214]),
        # Empty string
        ("", []),
    ]


def test_encode_to_zscii(encode_to_zscii_data):
    """Test encoding of strings to ZSCII character codes."""
    for text, expected_codes in encode_to_zscii_data:
        result = encode_to_zscii(text)
        assert result == expected_codes, f"Failed for '{text}': expected {expected_codes}, got {result}"


def test_encode_to_zscii_unsupported_characters():
    """Test that unsupported characters raise ValueError."""
    # Emojis are not supported in ZSCII
    with pytest.raises(ValueError, match="cannot be encoded to ZSCII"):
        encode_to_zscii("Hello 😀")

    # Cyrillic characters are not supported
    with pytest.raises(ValueError, match="cannot be encoded to ZSCII"):
        encode_to_zscii("Привет")

    # Chinese characters are not supported
    with pytest.raises(ValueError, match="cannot be encoded to ZSCII"):
        encode_to_zscii("你好")

    # Greek characters are not supported
    with pytest.raises(ValueError, match="cannot be encoded to ZSCII"):
        encode_to_zscii("Γειά")
