import pytest
from lib.container.container import Container
from lib.error import InvalidContainerKeyException, InvalidContainerTypeException
from lib.stream import ZStream
from lib.window import ZWindow


def test_container_simple_bind():
    container = Container()
    container.bind("Test", lambda: "This is a test")
    assert container.resolve("Test") == "This is a test"

    with pytest.raises(InvalidContainerTypeException):
        container.bind("Test", lambda: "This is a test", "InvalidType")

    Container.destroy()


def test_container_bind_with_args():
    container = Container()
    container.bind("Test", lambda x: x * x)
    assert container.resolve("Test", 2) == 4
    container.bind("Test2", lambda x, y: x * y)
    assert container.resolve("Test2", 2, 3) == 6
    Container.destroy()


def test_container_bind_singleton():
    class TestClass:
        pass

    class TestClass2:
        def __init__(self, id):
            self.id = id

    container = Container()
    container.bind("Test", lambda: TestClass())
    a = container.resolve("Test")
    b = container.resolve("Test")
    assert a != b

    container.bind("TestSingleton", lambda: TestClass(), "singleton")
    a = container.resolve("TestSingleton")
    b = container.resolve("TestSingleton")
    assert a == b

    container.bind("TestSingleton", lambda *args: TestClass2(*args), "singleton", 0)
    a = container.resolve("TestSingleton")
    b = container.resolve("TestSingleton")
    assert a == b
    Container.destroy()


def test_container_dynamic_resolution():
    container = Container()
    result = container.resolve("ZStream")
    assert type(result) is ZStream
    result = container.resolve("ZWindow", 0)
    assert type(result) is ZWindow

    with pytest.raises(InvalidContainerKeyException):
        container.resolve("InvalidClass")

    Container.destroy()
