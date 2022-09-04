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
import asyncio
import json
import logging
from platform import platform
from typing import Any

import websockets.client as websockets

from .errors import GatewayException
from .types.user import Settings, User, Verification

_log = logging.getLogger(__name__)


# TODO: Finish
class Gateway:
    def __init__(
        self, token: str, base_url: str = 'wss://derailed.one/gateway'
    ) -> None:
        self._token = token
        self._base_url = base_url
        self.session_id: str | None = None

    async def open_ws(self) -> None:
        self.ws = await websockets.connect(
            self._base_url, ping_interval=45, ping_timeout=4
        )

        self.receiver = asyncio.create_task(self._handle_messages)

        _log.debug('Connected to Gateway and started receiving messages')

    async def _handle_messages(self) -> None:
        # TODO: handle closes
        async for msg in self.ws:
            data: dict[str, Any] = json.loads(msg)

            _log.debug(data)

            if data['op'] == 0:
                if data['t'] == 'READY':
                    verification = Verification(**data['user'].pop('verification'))
                    self.user = User(**data['user'], verification=verification)
                    self.settings = Settings(**data['settings'])

            elif data['op'] == 2:
                raise GatewayException(data['d'])

            elif data['op'] == 3:
                self.session_id: str = data['d']['session_id']

    async def identify(self) -> None:
        await self.ws.send(
            json.dumps(
                {
                    'op': 1,
                    'd': {
                        'token': self._token,
                        'properties': {
                            'os': platform(),
                            'browser': 'derailed.py',
                            'device': 'derailed.py',
                            'library_github_repository': 'https://github.com/VincentRPS/derailed.py',
                            'client_version': '0.1.0',
                        },
                    },
                }
            )
        )

    async def get_guild_members(self, guild_id: str, limit: int = 0) -> None:
        await self.ws.send(
            json.dumps({'op': 4, 'd': {'guild_id': guild_id, 'limit': limit}})
        )
