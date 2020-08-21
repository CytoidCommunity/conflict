from logging import getLevelName
from typing import Any, List, Optional, Union, Literal

from pydantic import BaseModel, AnyHttpUrl, DirectoryPath, Extra, SecretStr, conlist, errors, validator


class Transcoding(BaseModel):
    format: str
    keep_origin: Optional[bool] = False


class S3(BaseModel):
    endpoint_url: AnyHttpUrl
    bucket: str
    access_key_id: str
    secret_access_key: SecretStr
    addressing_style: Optional[Literal['auto', 'virtual', 'path']] = 'auto'
    max_retry: Optional[int] = 5


class PushBase(BaseModel):
    class Config:
        extra = Extra.allow


class PushFallback(PushBase):
    live_start: Optional[Any]
    live_end: Optional[Any]


class PushMethod(PushBase):
    id: str
    type: str
    live_start: Any
    live_end: Any

    def __init__(self, fallback: Optional[dict] = None, **data):
        if type(fallback) is dict:
            data['live_start'] = data.get('live_start', fallback.get('live_start'))
            data['live_end'] = data.get('live_end', fallback.get('live_end'))
        super().__init__(**data)

    @validator('live_start', 'live_end')
    def check_none(cls, v):
        if v is None:
            raise errors.MissingError
        return v


class Push(BaseModel):
    fallback: Optional[PushFallback]
    methods: conlist(PushMethod, min_items=1)

    def __init__(self, **data):
        fallback = data.get('fallback')
        methods = data.get('methods')
        for method in methods:
            method['fallback'] = fallback
        super().__init__(fallback=fallback, methods=methods)

    @validator('methods', each_item=True)
    def check_method(cls, v: PushMethod):
        from conflict.push import get_module
        method = get_module(v.type)
        if method is None:
            raise ValueError(f'❌  Can NOT load push method \"{v.type}\"; '
                             f'Did you forget to install \"conflict[{v.type}]\"?')
        return method.Config(**v.dict(exclude_unset=True))


class Watcher(BaseModel):
    room_id: int
    nickname: Optional[str] = None
    capture: Optional[bool] = False
    push: Optional[List[str]]


class Config(BaseModel):
    log_level: Optional[Union[int, str]] = 'INFO'

    @validator('log_level')
    def check_level(cls, v):
        if getLevelName(getLevelName(v)) == v:
            return v
        raise ValueError(f'Unknown Level: {v}')

    get_play_url: Optional[AnyHttpUrl] = 'https://api.live.bilibili.com/room/v1/Room'

    @validator('get_play_url', always=True)
    def format_url(cls, v: AnyHttpUrl):
        return v.rstrip('/') + '/'

    check_interval: Optional[Union[int, float]] = 60
    retry_delay: Optional[Union[int, float]] = 3

    output: Optional[DirectoryPath] = '.'
    transcoding: Optional[Transcoding]
    s3: Optional[S3]

    push: Optional[Push] = []
    watchers: conlist(Watcher, min_items=1)

    @validator('watchers', each_item=True)
    def check_push_id(cls, v: Watcher, values: dict):
        if not v.push or 'push' not in values:
            return v
        all_ids = [method.id for method in values['push'].methods]
        wrong_ids = [push_id for push_id in v.push if push_id not in all_ids]
        if len(wrong_ids) > 0:
            raise ValueError('Push id(s) \"%s\" not found' % "\", \"".join(wrong_ids))
        return v
