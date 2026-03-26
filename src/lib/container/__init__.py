from lib.container.container import Container
from lib.container.item import ItemType
from lib.header import ZHeader
from lib.machine import ZMachine
from lib.memory import ZMemory


def initialize_container():
    container = Container()
    container.bind("ZMemory", lambda: ZMemory(), ItemType.SINGLETON)
    container.bind("ZHeader", lambda: ZHeader(), ItemType.SINGLETON)
    container.bind("ZMachine", lambda: ZMachine(), ItemType.SINGLETON)
    return container
