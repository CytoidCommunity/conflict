from asyncio import gather
from typing import List, Literal, Optional, Union

from aiogram import Bot
from pydantic import BaseModel, SecretStr

from conflict.schema.config import PushMethod


class ProxyAuth(BaseModel):
    login: str
    password: Optional[str] = ''
    encoding: Optional[str] = 'latin1'


class Photo(BaseModel):
    photo: str
    caption: str


class Config(PushMethod):
    type: Literal['telegram']
    token: SecretStr
    connections_limit: Optional[int] = None
    proxy: Optional[str] = None
    proxy_auth: Optional[ProxyAuth] = None
    validate_token: Optional[bool] = True
    parse_mode: Optional[str] = None
    timeout: Optional[Union[int, float]] = None
    live_start: Union[str, Photo]
    live_end: Union[str, Photo]
    chat_ids: List[str]


async def push(msg, config: Config):
    bot = Bot(**config.dict(
        include={'connections_limit', 'proxy', 'proxy_auth', 'validate_token', 'parse_mode', 'timeout'}),
              token=config.token.get_secret_value())
    coros = []
    for chat_id in config.chat_ids:
        if isinstance(msg, str):
            coros.append(bot.send_message(chat_id, msg))
        elif isinstance(msg, Photo):
            coros.append(bot.send_photo(chat_id, msg.photo, msg.caption))
    await gather(*coros)
    await bot.close()
