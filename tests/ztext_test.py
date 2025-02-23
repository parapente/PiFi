from array import array
from typing import cast
import pytest
from lib.container import initialize_container
from lib.container.container import Container
from lib.header import ZHeader
from lib.memory import ZMemory
from src.lib.ztext import decode_text, encode_text


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
    memory.mem = array("B")
    memory.mem.extend([0] * 1024)

    mem = memory.mem
    for data in decode_text_data:
        version, text, z_chars = data
        text_buffer = array("B", z_chars)
        print(data)
        header = cast(ZHeader, container.resolve("ZHeader"))
        header.version = version
        assert decode_text(text_buffer) == text
    Container.destroy()


def test_ztext_encode_text(encode_text_data):
    container = initialize_container()
    # Create dummy empty 1k memory
    memory = cast(ZMemory, container.resolve("ZMemory"))
    memory.mem = array("B")
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
