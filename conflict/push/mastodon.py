from io import BytesIO
from typing import Literal, Optional, Union

from aiohttp import ClientSession
from atoot import MastodonAPI
from pydantic import BaseModel, SecretStr

from conflict.schema.config import PushMethod


class Status(BaseModel):
    media: Optional[str]
    status: str


class Config(PushMethod):
    type: Literal['mastodon']
    instance: str
    access_token: SecretStr
    client_id: Optional[str]
    client_secret: Optional[SecretStr]
    use_https: Optional[bool] = True
    live_start: Union[str, Status]
    live_end: Union[str, Status]


async def push(msg, config: Config):
    async with ClientSession() as session:
        client = await MastodonAPI.create(**config.dict(include={'instance', 'client_id', 'use_https'}),
                                          access_token=config.access_token.get_secret_value(),
                                          client_secret=config.client_secret.get_secret_value(),
                                          session=session)
        if isinstance(msg, str):
            msg = Status(media=None, status=msg)
        media = None
        if msg.media:
            async with session.get(msg.media) as resp:
                content = await resp.read()
            f = BytesIO(content)
            media = (await client.upload_attachment(f))['id']
        await client.create_status(status=msg.status, media_ids=[media])
        await client.close()
