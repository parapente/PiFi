import pytest


def test_zstack_initialization():
    from lib.stack import ZStack

    stack = ZStack()
    assert stack.queue is not None
    assert stack.frames is not None
    assert stack.local_vars is not None
    assert stack.queuepos == 0
    assert stack.framespos == 0
    assert stack.local_vars_num == 0


def test_zstack_push_pop():
    from lib.stack import ZStack

    stack = ZStack()

    # Test basic push/pop
    stack.push(42)
    stack.push(100)
    assert stack.queuepos == 2

    assert stack.pop() == 100
    assert stack.queuepos == 1

    assert stack.pop() == 42
    assert stack.queuepos == 0


def test_zstack_push_pop_boundary():
    from lib.stack import ZStack

    stack = ZStack()

    # Test pushing beyond initial capacity (1000)
    for i in range(1000):
        stack.push(i)
    assert stack.queuepos == 1000
    assert stack.queuemaxpos == 1000

    # Push one more to trigger dynamic resizing
    stack.push(1000)
    assert stack.queuepos == 1001
    assert stack.queuemaxpos == 1001

    # Test popping all elements
    for i in range(1000, -1, -1):
        assert stack.pop() == i
    assert stack.queuepos == 0


def test_zstack_push_frame_pop_frame():
    from lib.stack import ZStack

    stack = ZStack()

    # Test basic frame operations
    stack.push_frame(42)
    stack.push_frame(100)
    assert stack.framespos == 2

    assert stack.pop_frame() == 100
    assert stack.framespos == 1

    assert stack.pop_frame() == 42
    assert stack.framespos == 0


def test_zstack_push_frame_pop_frame_boundary():
    from lib.stack import ZStack

    stack = ZStack()

    # Test pushing beyond initial capacity (3000)
    for i in range(3000):
        stack.push_frame(i)
    assert stack.framespos == 3000
    assert stack.framesmaxpos == 3000

    # Push one more to trigger dynamic resizing
    stack.push_frame(3000)
    assert stack.framespos == 3001
    assert stack.framesmaxpos == 3001

    # Test popping all elements
    for i in range(3000, -1, -1):
        assert stack.pop_frame() == i
    assert stack.framespos == 0


def test_zstack_local_vars():
    from lib.stack import ZStack

    stack = ZStack()

    # Test local vars management
    stack.local_vars = [1, 2, 3, 4, 5]
    stack.local_vars_num = 5

    # Push local vars to frame stack
    stack.push_local_vars()
    assert stack.framespos == 1

    # Modify local vars
    stack.local_vars = [10, 20, 30, 40, 50]

    # Pop back to original
    stack.pop_local_vars()
    assert stack.local_vars == [1, 2, 3, 4, 5]
    assert stack.framespos == 0


def test_zstack_eval_stack():
    from lib.stack import ZStack

    stack = ZStack()

    # Test evaluation stack operations
    stack.push(1)
    stack.push(2)
    stack.push(3)
    assert stack.queuepos == 3

    # Push evaluation stack (saves current queue and resets)
    stack.push_eval_stack()
    assert stack.queuepos == 0
    assert stack.queuemaxpos == 1000
    assert stack.framespos == 1

    # Verify saved data
    saved_data = stack.frames[0]
    assert saved_data == [1, 2, 3]


def test_zstack_pop_eval_stack():
    from lib.stack import ZStack

    stack = ZStack()

    # Setup evaluation stack
    stack.push(1)
    stack.push(2)
    stack.push(3)
    stack.push_eval_stack()

    # Test popping evaluation stack
    stack.pop_eval_stack()
    assert stack.queuepos == 3
    assert stack.queue == [1, 2, 3]
    assert stack.framespos == 0
