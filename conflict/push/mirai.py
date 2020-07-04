from asyncio import gather
from typing import List, Literal, Optional

from aiomirai import SessionApi, MessageChain
from pydantic import AnyHttpUrl, SecretStr, validator

from conflict.schema.config import PushMethod


class Config(PushMethod):
    type: Literal['mirai']
    api_root: AnyHttpUrl
    auth_key: SecretStr
    qq: int
    users: Optional[List[int]] = []
    groups: Optional[List[int]] = []

    @validator('live_start', 'live_end')
    def msg_chain(cls, v):
        return MessageChain(v)


async def push(msg, config: Config):
    api = SessionApi(config.api_root, config.auth_key.get_secret_value(), config.qq)
    coros = []
    for user in config.users:
        coros.append(api.send_friend_message(target=user, message_chain=msg))
    for group in config.groups:
        coros.append(api.send_group_message(target=group, message_chain=msg))
    async with api:
        await gather(*coros)
