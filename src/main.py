from cvg.socket import event

TEST_CHANNEL = b"TEST"

pool = event.Pool()

@pool.add_channel(event.Channel(TEST_CHANNEL))
def channel_transformer(*args, **kwargs):
    print("transform time!")
    return args, kwargs

@pool.add_event(event.Event(TEST_CHANNEL))
def event_listener(*args, **kwargs):
    print("event time!")
    return "hello", "there"

@pool.add_event(event.Event(TEST_CHANNEL))
def other_listener(*args, **kwargs):
    print("other time!")
    return "test", "this"


print(pool.emit(TEST_CHANNEL))