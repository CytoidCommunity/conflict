from typing import Optional

import httpx

from tairitsuru.config import config
from tairitsuru.logger import Logger
from tairitsuru.misc import auto_retry

from .exceptions import ApiFailed

_logger = Logger("live-api")


def _handle_api_result(res):
    if not res["code"] == 0:
        raise ApiFailed(**res)
    return res["data"]


@auto_retry(logger=_logger)
async def get_room_info(room_id: int,
                        client_args: Optional[dict] = {},
                        request_args: Optional[dict] = {}):
    async with httpx.AsyncClient(**client_args) as client:
        resp = await client.get(
            "https://api.live.bilibili.com/room/v1/Room/get_info",
            params={"room_id": room_id},
            **request_args)
    return _handle_api_result(resp.json())


@auto_retry(logger=_logger)
async def get_user_info(room_id: int,
                        client_args: Optional[dict] = {},
                        request_args: Optional[dict] = {}):
    async with httpx.AsyncClient(**client_args) as client:
        resp = await client.get(
            "https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room",
            params={"roomid": room_id},
            **request_args)
    return _handle_api_result(resp.json())


@auto_retry(logger=_logger)
async def get_play_urls(room_id: int,
                        client_args: Optional[dict] = {},
                        request_args: Optional[dict] = {}):
    async with httpx.AsyncClient(**client_args) as client:
        resp = await client.get(
            "https://api.live.bilibili.com/room/v1/Room/playUrl",
            params={
                "cid": room_id,
                "quality": 4
            },
            **request_args)
    return _handle_api_result(resp.json())
