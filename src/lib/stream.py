from lib.container.container import Container


class ZStream:
    selected = False
    filename = None


# Register the class with the container
Container.register("ZStream", ZStream)
