from asyncio import gather
from typing import List, Literal, Optional

from aiocqhttp import HttpApi
from pydantic import AnyHttpUrl, SecretStr

from conflict.schema.config import PushMethod


class Config(PushMethod):
    type: Literal['cqhttp']
    api_root: AnyHttpUrl
    access_token: Optional[SecretStr]
    users: Optional[List[int]] = []
    groups: Optional[List[int]] = []
    discusses: Optional[List[int]] = []


async def push(msg, config: Config):
    api = HttpApi(config.api_root, config.access_token.get_secret_value() if config.access_token else None, 0)
    coros = []
    for user in config.users:
        coros.append(api.send_private_msg(user_id=user, message=msg))
    for group in config.groups:
        coros.append(api.send_group_msg(group_id=group, message=msg))
    for discuss in config.discusses:
        coros.append(api.send_discuss_msg(discuss_id=discuss, message=msg))
    await gather(*coros)
