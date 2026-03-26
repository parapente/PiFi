from dataclasses import dataclass

from lib.container.container import Container


@dataclass
class ZStream:
    selected: bool = False
    filename: str | None = None


# Register the class with the container
Container.register("ZStream", ZStream)
