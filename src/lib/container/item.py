from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Item:
    type: str
    resolvable: Callable
    args: tuple = ()
    singleton = None

    def resolve(self, args: tuple):
        # If no arguments were passed we use the default arguments
        resolvable_args = self.args
        if len(args):
            resolvable_args = args

        # print(f"Resolvable args: {resolvable_args}")
        if self.type == "resolvable":
            if len(resolvable_args):
                return self.resolvable(*resolvable_args)
            else:
                return self.resolvable()
        elif self.type == "singleton":
            if self.singleton is None:
                if len(resolvable_args):
                    self.singleton = self.resolvable(*resolvable_args)
                else:
                    self.singleton = self.resolvable()

            return self.singleton
