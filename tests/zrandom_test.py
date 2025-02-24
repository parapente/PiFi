from typing import cast
from lib.container.container import Container
from lib.zrandom import ZRandom


def test_get_random():
    container = Container()
    rand = cast(ZRandom, container.resolve("ZRandom"))
    for i in range(1, 100):
        result = rand.get_random(i)
        assert result >= 1 and result <= i
    Container.destroy()


def test_get_predictable_random():
    container = Container()
    rand = cast(ZRandom, container.resolve("ZRandom"))
    rand.set_seed(42)
    pass1 = []
    for i in range(1000):
        pass1.append(rand.get_random(100))
    rand.set_seed(42)
    pass2 = []
    for i in range(1000):
        pass2.append(rand.get_random(100))
    assert pass1 == pass2


def test_get_predictable_random_then_random():
    container = Container()
    rand = cast(ZRandom, container.resolve("ZRandom"))
    rand.set_seed(42)
    pass1 = []
    for i in range(1000):
        pass1.append(rand.get_random(100))
    rand.set_seed(0)
    pass2 = []
    for i in range(1000):
        pass2.append(rand.get_random(100))
    assert pass1 != pass2
    pass3 = []
    for i in range(1000):
        pass3.append(rand.get_random(100))
    assert pass2 != pass3
