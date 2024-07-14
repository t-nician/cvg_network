from enum import Enum
from dataclasses import dataclass, field


CHANNEL_ALREADY_EXISTS = "Channel '{0}' already exists!"
CHANNEL_DOESNT_EXIST = "Channel '{0}' doesn't exist!"


@dataclass
class Event:
    channel_name: any = field(default=None)
    
    func: ( ) = field(default=lambda _: ())


@dataclass
class Channel:
    name: any = field(default=None)
    compile_returns: bool = field(default=False)
    transformer_func: ( ) = field(default=lambda *_, **__: ( _, __ ))
    
    listeners: list[Event] = field(default_factory=list)


@dataclass
class Pool:
    channels: dict[any, Channel] = field(default_factory=dict)
    
    def add_channel(self, channel: Channel):
        assert self.channels.get(channel.name) is None, CHANNEL_ALREADY_EXISTS.format(
            str(channel.name)
        )
        
        self.channels[channel.name] = channel
        
        def wrapper(func):
            channel.transformer_func = func or (lambda *_, **__: ( _, __ ))
                
        return wrapper
    
    def add_event(self, event: Event):
        def wrapper(func):
            channel = self.channels.get(event.channel_name)
            
            assert channel, CHANNEL_DOESNT_EXIST.format(
                str(event.channel_name)
            )
            
            event.func = func
            channel.listeners.append(event)
        
        return wrapper
    
    def emit(self, channel_name: any, *args, **kwargs):
        channel = self.channels.get(channel_name)
        args, kwargs = channel.transformer_func(*args, **kwargs)
        
        assert channel, CHANNEL_DOESNT_EXIST.format(
            str(channel_name)
        )
        
        compiled_return = []
        singular_return = None
        
        for listener in channel.listeners:
            result = listener.func(*args, **kwargs)
            
            if channel.compile_returns and result is not None:
                compiled_return.extend(list(result))
            elif singular_return is None and result is not None:
                singular_return = result
        
        return channel.compile_returns and compiled_return or singular_return