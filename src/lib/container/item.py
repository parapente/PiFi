from dataclasses import dataclass
from typing import Any, Callable, TypeVar, Generic, Optional

T = TypeVar('T')


@dataclass
class Item(Generic[T]):
    type: str
    resolvable: Callable[..., T]
    args: tuple[Any, ...] = ()
    singleton: Optional[T] = None

    def resolve(self, args: tuple[Any, ...]) -> T:
        """Resolve the item, creating an instance if needed.

        Args:
            args: Arguments to pass to the resolver (overrides default args)

        Returns:
            The resolved instance

        Raises:
            ValueError: If item type is unknown
        """
        # If no arguments were passed we use the default arguments
        resolvable_args = self.args
        if len(args):
            resolvable_args = args

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
        else:
            raise ValueError(f"Unknown item type: {self.type}")
