from importlib import import_module
from typing import Dict

from pydantic import BaseModel

from conflict.log import get_logger
from conflict.schema.config import PushMethod
from conflict.schema.push import PushEvent


def _gen_components(data: dict) -> dict:
    res = data.copy()
    res['uid'] = res['room_info']['uid']
    res['room_id'] = res['room_info']['room_id']
    res['live_title'] = res['room_info']['title']
    res['cover'] = res['room_info']['cover']
    res['background'] = res['room_info']['cover']
    res['keyframe'] = res['room_info']['keyframe']
    res['parent_area_name'] = res['room_info']['parent_area_name']
    res['area_name'] = res['room_info']['area_name']
    res['user_name'] = res['anchor_info']['base_info']['uname']
    res['user_face'] = res['anchor_info']['base_info']['face']
    return res


def _format(msg, data: dict):
    if isinstance(msg, str):
        return msg.format(**data)
    if isinstance(msg, list):
        return [_format(i, data) for i in msg]
    if isinstance(msg, dict):
        return {k: _format(v, data) for k, v in msg.items()}
    if isinstance(msg, BaseModel):
        return msg.parse_obj(_format(msg.dict(), data))


def get_module(name: str):
    try:
        module = import_module(f"conflict.push.{name}")
    except ImportError:
        return None
    return module


pool: Dict[str, PushMethod] = {}


def get_config(name: str) -> PushMethod:
    if not pool:
        from conflict.config import config
        for method in config.push.methods:
            pool[method.id] = method
    return pool[name]


async def push(name: str, event: PushEvent, **data):
    push_config = get_config(name)
    module = get_module(push_config.type)
    msg = _format(getattr(push_config, event), _gen_components(data))
    logger = get_logger('push')

    try:
        await module.push(msg, push_config)
    except:
        logger.exception('❌  Failed to push some messages.')
