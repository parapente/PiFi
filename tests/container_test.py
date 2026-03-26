import pytest
from lib.container.container import Container
from lib.container.item import ItemType
from lib.error import InvalidContainerKeyException, InvalidContainerTypeException
from lib.stream import ZStream
from lib.window import ZWindow
from lib.zrandom import ZRandom


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

    container.bind("TestSingleton", lambda: TestClass(), ItemType.SINGLETON)
    a = container.resolve("TestSingleton")
    b = container.resolve("TestSingleton")
    assert a == b

    container.bind("TestSingleton", lambda *args: TestClass2(*args), ItemType.SINGLETON, 0)
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


# Tests for the registration system
def test_container_registration():
    """Test explicit class registration."""
    # Clear registry for clean state
    Container._registry.clear()

    # Register a class
    Container.register("ZRandom", ZRandom)

    # Resolve should work without manual binding
    container = Container()
    result = container.resolve("ZRandom")
    assert isinstance(result, ZRandom)

    # Get registered classes
    registered = Container.get_registered_classes()
    assert "ZRandom" in registered
    assert registered["ZRandom"] is ZRandom

    Container.destroy()


def test_container_unregister():
    """Test unregistering classes."""
    Container._registry.clear()

    Container.register("ZRandom", ZRandom)
    assert "ZRandom" in Container.get_registered_classes()

    Container.unregister("ZRandom")
    assert "ZRandom" not in Container.get_registered_classes()

    Container.destroy()


def test_container_registration_with_args():
    """Test resolving registered classes with arguments."""
    Container._registry.clear()

    # Note: Most registered classes don't take constructor args
    # but we can test with a custom class
    class TestClass:
        def __init__(self, value: int):
            self.value = value

    Container.register("TestClass", TestClass)

    container = Container()
    instance = container.resolve("TestClass", 42)
    assert isinstance(instance, TestClass)
    assert instance.value == 42

    Container.destroy()


def test_container_unknown_class():
    """Test that resolving an unregistered class raises error."""
    Container._registry.clear()
    container = Container()

    with pytest.raises(InvalidContainerKeyException) as exc_info:
        container.resolve("UnknownClass")

    assert "UnknownClass" in str(exc_info.value)
    assert "not available" in str(exc_info.value)

    Container.destroy()


def test_container_singleton_across_instances():
    """Test that singleton bindings persist across container instances."""
    Container._registry.clear()

    class SingletonClass:
        pass

    container1 = Container()
    container2 = Container()

    # Bind as singleton in first container
    container1.bind("Singleton", lambda: SingletonClass(), ItemType.SINGLETON)
    instance1 = container1.resolve("Singleton")
    instance2 = container2.resolve("Singleton")

    # Should both resolve to the SAME instance
    assert instance1 is instance2

    Container.destroy()


def test_container_bind_type_validation():
    """Test that invalid bind types raise errors."""
    container = Container()

    with pytest.raises(InvalidContainerTypeException):
        container.bind("Invalid", lambda: "test", type="invalid")

    Container.destroy()


def test_container_mixed_bind_and_registry():
    """Test using both manual binding and registry."""
    Container._registry.clear()

    class CustomClass:
        def __init__(self, name: str = "default"):
            self.name = name

    # Register in registry
    Container.register("Registered", CustomClass)

    container = Container()

    # Resolve from registry (no args)
    reg_instance = container.resolve("Registered")
    assert isinstance(reg_instance, CustomClass)
    assert reg_instance.name == "default"

    # Manually bind with custom args
    container.bind("Bound", lambda: CustomClass("bound"))
    bound_instance = container.resolve("Bound")
    assert bound_instance.name == "bound"

    Container.destroy()


def test_container_registry_isolation():
    """Test that registry is class-level and shared across instances."""
    Container._registry.clear()

    container1 = Container()
    container2 = Container()

    # Register via first container
    Container.register("Shared", ZRandom)

    # Both should see the registration
    assert "Shared" in Container.get_registered_classes()

    # Both can resolve it
    instance1 = container1.resolve("Shared")
    instance2 = container2.resolve("Shared")
    assert isinstance(instance1, ZRandom)
    assert isinstance(instance2, ZRandom)

    Container.destroy()


def test_container_destroy_clears_bindings():
    """Test that destroy clears instance bindings."""
    container = Container()
    container.bind("Test", lambda: "value")
    assert "Test" in container.bindings

    container.destroy()
    assert len(container.bindings) == 0
    assert "Test" not in container.bindings


def test_container_registry_persistence():
    """Test that registry persists after instance destroy."""
    Container._registry.clear()

    Container.register("Persistent", ZRandom)

    # Create and destroy container
    container = Container()
    container.destroy()

    # Registry should still have the class
    assert "Persistent" in Container.get_registered_classes()

    Container._registry.clear()  # Cleanup


def test_container_cannot_override_registry_with_bind():
    """Test that binding a key that exists in registry uses the binding."""
    Container._registry.clear()

    Container.register("Registered", ZRandom)

    container = Container()
    # Bind overrides registry
    container.bind("Registered", lambda: "bound_value")

    result = container.resolve("Registered")
    assert result == "bound_value"

    Container.destroy()


def test_container_thread_safety_singleton():
    """Test that Container singleton is thread-safe in basic usage."""
    # This is a simple check - full thread safety would require concurrent access
    container1 = Container()
    container2 = Container()
    assert container1 is container2  # Same instance

    Container.destroy()


def test_container_issue_11_security():
    """Test that the new registration system avoids the security vulnerability
    of pydoc.locate() by requiring explicit registration."""
    Container._registry.clear()

    # Try to resolve a class that wasn't explicitly registered
    container = Container()

    # Should raise InvalidContainerKeyException, not execute arbitrary code
    with pytest.raises(InvalidContainerKeyException):
        container.resolve("NonExistentClass")

    # Verify that the old dynamic lookup method was removed
    # by ensuring only explicitly registered classes work
    Container.register("ZRandom", ZRandom)
    result = container.resolve("ZRandom")
    assert isinstance(result, ZRandom)

    Container.destroy()

