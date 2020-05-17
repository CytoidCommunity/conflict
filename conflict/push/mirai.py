import asyncio
from typing import Any, Dict, List, Union

import aiomirai
import aiomirai.api

from ..logger import Logger

aiomirai.api.Logger = Logger("push_mirai")


async def send(msg: Union[str, List[Dict[str, Any]]], **kwargs):
    api_root = kwargs["api_root"]
    auth_key = kwargs["auth_key"]
    qq = kwargs["qq"]
    api = aiomirai.SessionApi(api_root, auth_key, qq)

    msg = aiomirai.MessageChain(msg)

    coros = []
    for user in kwargs.get("users", []):
        coros.append(api.send_friend_message(target=user, message_chain=msg))
    for group in kwargs.get("groups", []):
        coros.append(api.send_group_message(target=group, message_chain=msg))
    async with api:
        await asyncio.gather(*coros)
