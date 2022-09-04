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
import json
import logging
from typing import Any, TypedDict

from aiohttp import ClientResponse, ClientSession

from .enums import RelationshipType, TrackType
from .errors import HTTPException
from .types.guild import Guild
from .types.relationship import Relationship
from .types.role import Role
from .types.track import Track
from .types.user import Profile, Settings, User
from .utils import UNDEFINED, replace_undefined

_log = logging.getLogger(__name__)


class Error(TypedDict):
    detail: str


class Relatable(TypedDict):
    user_id: str
    relatable: bool


class GuildTrackModification(TypedDict):
    id: str
    position: int
    sync: bool
    parent_id: str | None


# TODO: implement rate limiting
class Interactor:
    def __init__(self, token: str, base_url: str = 'https://derailed.one/api') -> None:
        self._token = token
        self._base_url = base_url
        self._base_headers = {'Authorization': token}

    # ClientSession initialization can fail in a non-async environment
    async def _create_http(self) -> None:
        self._session = ClientSession()

    async def request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | list[dict[str, Any]] | None = None,
        reason: str | None = None,
    ) -> ClientResponse:
        headers = self._base_headers

        if reason:
            headers['X-Action-Reason'] = reason

        _log.debug(f'sending {method} request to {path} with {data} because {reason}')

        req = (
            await self._session.request(
                method=method, url=self._base_url + path, data=json.dumps(data)
            )
            if data
            else await self._session.request(
                method=method, url=self._base_url + path, headers=headers
            )
        )

        data: dict[str, Any] | Error = await req.json()

        if not req.ok:
            raise HTTPException(data['detail'])

        return data

    async def register(self, email: str, username: str, password: str) -> User:
        return await self.request(
            'POST',
            '/register',
            {'email': email, 'username': username, 'password': password},
        )

    async def login(self, email: str, password: str) -> User:
        return await self.request(
            'POST', '/login', {'email': email, 'password': password}
        )

    async def get_current_user(self) -> User:
        return await self.request('GET', '/users/@me')

    async def modify_current_user(
        self,
        username: str = UNDEFINED,
        email: str = UNDEFINED,
        password: str = UNDEFINED,
    ) -> User:
        return await self.request(
            'PATCH',
            '/users/@me',
            replace_undefined(username=username, email=email, password=password),
        )

    async def delete_current_user(self, password: str) -> None:
        return await self.request('DELETE', '/users/@me', {'password': password})

    async def put_presence(self, content: str) -> None:
        return await self.request('PUT', '/users/@me/presence', {'content': content})

    async def get_current_profile(self) -> Profile:
        return await self.request('GET', '/profiles/@me')

    async def get_profile(self, user_id: str | int) -> Profile:
        return await self.request('GET', f'/profiles/{user_id}')

    async def get_settings(self) -> Settings:
        return await self.request('GET', '/users/@me/settings')

    async def modify_settings(
        self, status: str = UNDEFINED, theme: str = UNDEFINED
    ) -> Settings:
        return await self.request(
            'PATCH',
            '/users/@me/settings',
            replace_undefined(status=status, theme=theme),
        )

    async def relatable(self, username: str, discriminator: str) -> Relatable:
        return await self.request(
            'GET',
            f'/relationships/relatable?username={username}&discriminator={discriminator}',
        )

    async def get_relationships(self) -> list[Relationship]:
        return await self.request('GET', '/users/@me/relationships')

    async def put_relationship(self, user_id: str, type: RelationshipType) -> None:
        return await self.request('PUT', f'/relationships/{user_id}', {'type': type})

    async def delete_relationship(self, user_id: str) -> None:
        return await self.request('DELETE', f'/relationships/{user_id}')

    async def get_guild(self, guild_id: str) -> Guild:
        return await self.request('GET', f'/guilds/{guild_id}')

    async def get_guild_preview(self, guild_id: str) -> Guild:
        return await self.request('GET', f'/guilds/{guild_id}/preview')

    async def create_guild(
        self, name: str, description: str = UNDEFINED, nsfw: bool = UNDEFINED
    ) -> Guild:
        return await self.request(
            'POST',
            '/guilds',
            replace_undefined(name=name, description=description, nsfw=nsfw),
        )

    async def modify_guild(
        self,
        guild_id: str,
        name: str = UNDEFINED,
        description: str = UNDEFINED,
        nsfw: bool = UNDEFINED,
    ) -> Guild:
        return await self.request(
            'PATCH',
            f'/guilds/{guild_id}',
            replace_undefined(name=name, description=description, nsfw=nsfw),
        )

    async def delete_guild(self, guild_id: str) -> None:
        return await self.request('DELETE', f'/guilds/{guild_id}')

    async def ban_member(
        self, guild_id: str, user_id: str, reason: str | None = None
    ) -> None:
        return await self.request(
            'POST', f'/guilds/{guild_id}/members/{user_id}/ban', reason=reason
        )

    async def kick_member(self, guild_id: str, user_id: str) -> None:
        return await self.request('DELETE', f'/guilds/{guild_id}/members/{user_id}')

    async def modify_member(
        self, guild_id: str, user_id: str, nick: str = UNDEFINED
    ) -> None:
        return await self.request(
            'PATCH',
            f'/guilds/{guild_id}/members/{user_id}',
            replace_undefined(nick=nick),
        )

    async def modify_member_nick(
        self, guild_id: str, user_id: str, nick: str | None
    ) -> None:
        return await self.request(
            'PATCH', f'/guilds/{guild_id}/members/{user_id}/nick', {'nick': nick}
        )

    async def get_guild_roles(self, guild_id: str) -> list[Role]:
        return await self.request('GET', f'/guilds/{guild_id}/roles')

    async def get_guild_role(self, guild_id: str, role_id: str) -> Role:
        return await self.request('GET', f'/guilds/{guild_id}/roles/{role_id}')

    async def create_role(
        self, guild_id: str, name: str, permissions: int, hoist: bool = UNDEFINED
    ) -> Role:
        return await self.request(
            'POST',
            f'/guilds/{guild_id}/roles',
            replace_undefined(name=name, permissions=permissions, hoist=hoist),
        )

    async def modify_role(
        self,
        guild_id: str,
        name: str,
        permissions: int,
        position: int,
        hoist: bool = UNDEFINED,
    ) -> Role:
        return await self.request(
            'POST',
            f'/guilds/{guild_id}/roles',
            replace_undefined(
                name=name, permissions=permissions, hoist=hoist, position=position
            ),
        )

    async def get_guild_tracks(self, guild_id: str) -> list[Track]:
        return await self.request('GET', f'/guilds/{guild_id}/tracks')

    async def get_guild_track(self, guild_id: str, track_id: str) -> Track:
        return await self.request('GET', f'/guilds/{guild_id}/tracks/{track_id}')

    async def create_guild_track(
        self,
        guild_id: str,
        name: str,
        type: TrackType,
        parent_id: str = UNDEFINED,
        position: int = UNDEFINED,
        topic: str = UNDEFINED,
    ) -> Track:
        return await self.request(
            'POST',
            f'/guild/{guild_id}/tracks',
            replace_undefined(
                name=name,
                type=type,
                parent_id=parent_id,
                position=position,
                topic=topic,
            ),
        )

    async def modify_guild_tracks(
        self, guild_id: str, modifications: list[GuildTrackModification]
    ) -> None:
        return await self.request('PATCH', f'/guilds/{guild_id}/tracks/', modifications)

    async def create_group_dm(
        self, name: str, user_ids: list[str], topic: str = UNDEFINED
    ) -> Track:
        return await self.request(
            'POST',
            '/users/@me/group-dms',
            replace_undefined(name=name, user_ids=user_ids, topic=topic),
        )

    async def modify_track(
        self, track_id: str, name: str = UNDEFINED, topic: str = UNDEFINED
    ) -> Track:
        return await self.request(
            'PATCH', f'/tracks/{track_id}', replace_undefined(name=name, topic=topic)
        )

    async def close_track(self, track_id: str) -> None:
        return await self.request('DELETE', f'/tracks/{track_id}')
