from copy import copy
from importlib import import_module
from typing import Union

from ..config import config

_methods: dict = {}


async def _push(type, msg, **kwargs):
    sender = import_module(f"tairitsuru.push.{type}")
    await sender.send(msg, **kwargs)


def _expand_arg(arg: dict):
    res = copy(arg)
    res["uid"] = res["room"]["uid"]
    res["room_id"] = res["room"]["room_id"]
    res["live_title"] = res["room"]["title"]
    res["cover"] = res["room"]["user_cover"]
    res["background"] = res["room"]["background"]
    res["user_face"] = res["user"]["info"]["face"]
    res["san"] = res["user"]["san"]
    res["user_name"] = res.get("user_name", res["user"]["info"]["uname"])
    return res


def _format_msg(msg: Union[str, dict, list], arg: dict):
    if isinstance(msg, str):
        return msg.format(**arg)
    if isinstance(msg, list):
        return [_format_msg(i, arg) for i in msg]
    if isinstance(msg, dict):
        return {k: _format_msg(v, arg) for k, v in msg.items()}


def _get_method(id_):
    global _methods
    if id_ not in _methods:
        res = copy(next(filter(lambda x: x.get("id") == id_, config["push"]["methods"])))
        del res["id"]
        if "live_start" not in res:
            res["live_start"] = config["push"]["default"]["live_start"]
        if "live_end" not in res:
            res["live_end"] = config["push"]["default"]["live_end"]
        _methods[id_] = res
    return _methods[id_]


async def live_start(id_, arg):
    method = _get_method(id_)
    msg = _format_msg(method["live_start"], _expand_arg(arg))
    await _push(msg=msg, **{k: method[k] for k in method.keys() if k not in {"live_start", "live_end"}})


async def live_end(id_, arg):
    method = _get_method(id_)
    msg = _format_msg(method["live_end"], _expand_arg(arg))
    await _push(msg=msg, **{k: method[k] for k in method.keys() if k not in {"live_start", "live_end"}})
