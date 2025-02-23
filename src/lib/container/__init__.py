from lib.container.container import Container
from lib.header import ZHeader
from lib.machine import ZMachine
from lib.memory import ZMemory


def initialize_container():
    container = Container()
    container.bind("ZMemory", lambda: ZMemory(), "singleton")
    container.bind("ZHeader", lambda: ZHeader(), "singleton")
    container.bind("ZMachine", lambda: ZMachine(), "singleton")
    return container
