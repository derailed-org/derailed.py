"""
MIT License

Copyright (c) 2022 VincentRPS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from asyncio import create_task, get_running_loop, iscoroutinefunction
from functools import partial
from typing import Any, Callable, Coroutine

__all__ = ['Dispatcher']


class Dispatcher:
    def __init__(self) -> None:
        self.events: dict[Any, list[Coroutine | Callable]] = {}

    async def _dispatch_under_names(self, event_name: Any, *args, **kwargs) -> None:
        events = self.events.get(event_name)

        if events is None:
            return

        for event in events:
            if iscoroutinefunction(event):
                await event(*args, **kwargs)  # type: ignore
            else:
                loop = get_running_loop()
                e = partial(event, *args, **kwargs)
                await loop.run_in_executor(None, e)  # type: ignore

    def dispatch(self, event: Any, *args, **kwargs) -> None:
        if isinstance(event, str):
            event = f'on_{event}'

        create_task(self._dispatch_under_names(event, *args, **kwargs))

    def add_listener(self, name: Any, function: Coroutine | Callable) -> None:
        if self.events.get(name):
            self.events[name].append(function)
        else:
            self.events[name] = [function]

    def remove_listener(self, name: Any, function: Coroutine | Callable) -> None:
        if self.events.get(name):
            self.events[name].remove(function)

    async def _handle_wait_for(self, func: Coroutine, *args, **kwargs) -> None:
        await func(*args, **kwargs)

    async def wait_for(self, name: str, func: Coroutine) -> None:
        part = partial(self._handle_wait_for, func)

        self.add_listener(name=name, function=part)
