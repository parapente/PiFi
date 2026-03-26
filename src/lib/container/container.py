from typing import Callable, Dict, Optional, Type, Any
from lib.container.item import Item, ItemType
from lib.error import InvalidContainerKeyException, InvalidContainerTypeException
from lib.singleton import Singleton


class Container(metaclass=Singleton):
    bindings: Dict[str, Item[Any]]
    _registry: Dict[
        str, Type[Any]
    ] = {}  # Class-level registry for explicit registration

    def __init__(self) -> None:
        self.bindings = {}

    @classmethod
    def register(cls, key: str, class_ref: Type[Any]) -> None:
        """Register a class in the container's registry.

        Args:
            key: The identifier used to resolve this class
            class_ref: The class object to register
        """
        cls._registry[key] = class_ref

    @classmethod
    def unregister(cls, key: str) -> None:
        """Remove a class from the registry."""
        if key in cls._registry:
            del cls._registry[key]

    @classmethod
    def get_registered_classes(cls) -> Dict[str, Type[Any]]:
        """Return a copy of the registry."""
        return cls._registry.copy()

    def bind(
        self,
        key: str,
        resolver: Callable[..., Any],
        type: ItemType = ItemType.RESOLVABLE,
        *args: Any,
    ) -> None:
        if type not in [ItemType.RESOLVABLE, ItemType.SINGLETON]:
            raise InvalidContainerTypeException("Invalid container item type")

        item = Item(type, resolver, args)
        self.bindings[key] = item

    def resolve(self, key: str, *args: Any) -> Any:
        """Resolve a service from the container.

        Args:
            key: The service identifier
            *args: Arguments to pass to the service constructor

        Returns:
            The resolved instance

        Raises:
            InvalidContainerKeyException: If the key is not found
        """
        if key not in self.bindings:
            result = self.find_class(key)
            if result is None:
                raise InvalidContainerKeyException(
                    f"Key {key} not available in container"
                )

            if len(args):
                item = Item(ItemType.RESOLVABLE, lambda *args: result(*args), args)
            else:
                item = Item(ItemType.RESOLVABLE, lambda: result())

            self.bindings[key] = item
        else:
            item = self.bindings[key]

        return item.resolve(args)

    @classmethod
    def destroy(cls) -> None:
        """Clear the container's bindings and reset singleton state.

        This is a classmethod to properly reset the singleton instance.
        """
        # Clear instance bindings if instance exists
        if hasattr(cls, "_instances") and cls in cls._instances:
            instance = cls._instances[cls]
            instance.bindings.clear()
        # Clear the class-level registry
        # cls._registry.clear()  # Optionally clear registry too

    def find_class(self, name: str) -> Optional[Type[Any]]:
        """Find a class in the registry.

        Args:
            name: The class identifier to look up

        Returns:
            The class if found in registry, None otherwise
        """
        return self._registry.get(name)
