from enum import Enum
from dataclasses import dataclass, field
    

@dataclass
class Event:
    channel: any = field(default=None)
    returns: bool = field(default=False)


@dataclass
class Channel:
    name: any = field(default=None)
    compile_returns: bool = field(default=False)
    transformer_func: ( ) = field(default=lambda *_, **__: ( _, __ ))
    
    listeners: list[Event] = field(default_factory=list)


@dataclass
class Pool:
    channels: dict[any, Channel] = field(default_factory=list)
    
    def add_channel(self, channel: Channel):
        assert self.channels.get(channel.name) is None, ""
        self.channels[channel.name] = channel
        
        def wrapper(func):
            channel.transformer_func = func or (lambda *_, **__: ( _, __ ))
                
        return wrapper
    
    def add_event(self, event: Event):
        def wrapper(func):
            print("event time")
        
        return wrapper