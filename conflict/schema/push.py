from enum import Enum


class PushEvent(str, Enum):
    LIVE_START = 'live_start'
    LIVE_END = 'live_end'
