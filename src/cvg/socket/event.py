from enum import Enum
from uuid import uuid4
from dataclasses import dataclass, field


CHANNEL_ALREADY_EXISTS = "Channel '{0}' already exists!"
CHANNEL_DOESNT_EXIST = "Channel '{0}' doesn't exist!"

DEFAULT_CHANNEL_TRANSFORMER = lambda *_: ( _ )
DEFAULT_EVENT_FUNC = lambda *_: ( )


@dataclass
class Event:
    channel_name: any = field(default=None)

    func: ( any ) = field(default=DEFAULT_EVENT_FUNC)
    id: str = field(default_factory=lambda: uuid4().hex)
    
    preargs: tuple[any] = field(default_factory=tuple)


@dataclass
class Channel:
    name: any = field(default=None)
    
    compile_returns: bool = field(default=False)
    transformer_func: ( any ) = field(default=DEFAULT_CHANNEL_TRANSFORMER)
    
    listeners: list[Event] = field(default_factory=list)


@dataclass
class Pool:
    channels: dict[any, Channel] = field(default_factory=dict)
    transformer_emit: ( any ) = field(default=DEFAULT_CHANNEL_TRANSFORMER)
    
    def add_channel(self, channel: Channel):
        assert self.channels.get(channel.name) is None, CHANNEL_ALREADY_EXISTS.format(
            str(channel.name)
        )
        
        self.channels[channel.name] = channel
        
        def wrapper(func):
            channel.transformer_func = func or DEFAULT_CHANNEL_TRANSFORMER
                
        return wrapper
    
    def add_event(self, event: Event):
        channel = self.channels.get(event.channel_name)
            
        assert channel, CHANNEL_DOESNT_EXIST.format(
            str(event.channel_name)
        )
        
        channel.listeners.append(event)
        
        def wrapper(func):
            event.func = func
        
        return wrapper
    
    def emit_transformer(self, func: ( any )):
        self.transformer_emit = func or DEFAULT_CHANNEL_TRANSFORMER
        
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    
    def emit(self, channel_name: any, *args):
        channel = self.channels.get(channel_name)
        
        assert channel, CHANNEL_DOESNT_EXIST.format(
            str(channel_name)
        )
        
        args = self.transformer_emit(*args)
        args = channel.transformer_func(*args)
        
        if type(args) is not tuple:
            args = (args,)
        
        compiled_return = []
        singular_return = None
        
        for listener in channel.listeners:
            result = listener.func(*listener.preargs, *args)
            
            if channel.compile_returns and result is not None:
                compiled_return.append(result)
            elif singular_return is None and result is not None:
                singular_return = result
        
        return channel.compile_returns and compiled_return or singular_return