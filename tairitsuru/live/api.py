from httpx import AsyncClient

from .exceptions import ApiFailed


def _handle_api_result(res: dict):
    if not res["code"] == 0:
        raise ApiFailed(**res)
    return res["data"]


async def get_room_info(room_id: int):
    async with AsyncClient() as client:
        resp = await client.get(
            "https://api.live.bilibili.com/room/v1/Room/get_info",
            params={"room_id": room_id})
    return _handle_api_result(resp.json())


async def get_user_info(room_id: int):
    async with AsyncClient() as client:
        resp = await client.get(
            "https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room",
            params={"roomid": room_id})
    return _handle_api_result(resp.json())


async def get_play_urls(room_id: int):
    async with AsyncClient() as client:
        resp = await client.get(
            "https://api.live.bilibili.com/room/v1/Room/playUrl",
            params={
                "cid": room_id,
                "quality": 4
            })
    return _handle_api_result(resp.json())
