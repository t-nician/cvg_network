from cvg.socket import event

TEST_CHANNEL = b"TEST"

pool = event.Pool()

@pool.add_channel(event.Channel(TEST_CHANNEL, compile_returns=True))
def channel_transformer(greeting):
    print("transforming", greeting)
    return greeting.removeprefix("typo")

pool.add_event(event.Event(TEST_CHANNEL, print, preargs=("[debug]",)))

@pool.add_event(event.Event(TEST_CHANNEL))
def first_event(greeting):
    print("first_event", greeting)
    return "hello", "there"

@pool.add_event(event.Event(TEST_CHANNEL))
def second_event(greeting):
    print("second_event", greeting)
    return "test", "this"


print(pool.emit(TEST_CHANNEL, "typoHello!"))