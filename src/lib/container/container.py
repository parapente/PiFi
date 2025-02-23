from os.path import isfile, join, splitext
from os import listdir
from pathlib import Path
from pydoc import locate
from typing import Callable, Dict
from lib.container.item import Item
from lib.error import InvalidContainerKeyException, InvalidContainerTypeException
from lib.singleton import Singleton
from lib.utils import get_project_root


class Container(metaclass=Singleton):
    bindings: Dict[str, Item]

    def __init__(self, *args, **kwargs):
        self.bindings = {}

    def bind(self, key: str, resolver: Callable, type: str = "resolvable", *args):
        if type not in ["resolvable", "singleton"]:
            raise InvalidContainerTypeException("Invalid container item type")

        item = Item(type, resolver, args)
        self.bindings[key] = item

    def resolve(self, key: str, *args):
        if key not in self.bindings:
            result = self.find_class(key)
            if result is None:
                raise InvalidContainerKeyException(
                    f"Key {key} not available in container"
                )

            if len(args):
                item = Item("resolvable", lambda *args: result(*args), args)
            else:
                item = Item("resolvable", lambda: result())

            self.bindings[key] = item
        else:
            item = self.bindings[key]

        return item.resolve(args)

    def find_class(self, name: str):
        d = get_project_root() / "lib"
        onlyfiles = [splitext(f)[0] for f in listdir(d) if isfile(join(d, f))]
        for file in onlyfiles:
            result = locate("lib." + file + "." + name)
            if result is not None:
                return result
        return None
