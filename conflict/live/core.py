"""
The core algorithm of conflict.
"""
import asyncio
import time
from functools import partial, wraps
from typing import Optional

from ..config import config
from ..logger import Logger
from ..misc import auto_retry

from .api import get_play_urls, get_room_info, get_user_info
from .capture import capture_stream


def run_callback(callbacks, arg):
    if callbacks:
        [asyncio.create_task(func(arg)) for func in callbacks]


class Worker:
    def __init__(self,
                 room_id: int,
                 capture: Optional[bool] = False,
                 check_interval: Optional[int] = 60):

        self.room_id = room_id
        self.capture = capture
        self.check_interval = check_interval

        self.logger = Logger(f"{room_id}.live")
        self.callback_start = []
        self.callback_end = []

        self.get_play_urls = auto_retry(self.logger)(
            wraps(get_play_urls)(partial(get_play_urls, get_play_url=config.get("get_play_url", {}).get("url"))))
        self.get_room_info = auto_retry(self.logger)(get_room_info)
        self.get_user_info = auto_retry(self.logger)(get_user_info)
        self.capture_stream = auto_retry(self.logger)(capture_stream)

    def on_start(self, func):
        self.callback_start.append(func)

    def on_end(self, func):
        self.callback_end.append(func)

    async def run(self):
        while True:
            room = await self.get_room_info(self.room_id)
            user = await self.get_user_info(self.room_id)
            if not room["live_status"] == 1:
                self.logger.info("⭐️  %s 不在直播 %d", user["info"]["uname"], room["live_status"])
                await asyncio.sleep(self.check_interval)
                continue

            self.logger.info("⭐️  %s 直播中 %s", user["info"]["uname"], room["live_time"])
            run_callback(self.callback_start, {
                "room": room,
                "user": user
            })
            start_at = time.time()
            while True:
                filename = None
                if self.capture:
                    filename = "%s-%d-%s.flv" % (
                        user["info"]["uname"], self.room_id,
                        time.strftime("%Y-%m-%d_%H%M%S", time.localtime()))
                    url_info = await self.get_play_urls(self.room_id)
                    if len(url_info["durl"]) == 0:
                        self.logger.log("❌  Stream list is empty.")
                    else:
                        url = url_info["durl"][0]["url"]
                        self.logger.info("☑️  视频流捕获 Qual.%d", url_info["current_quality"])
                        self.logger.info("    %s", url)
                        self.logger.info("🌟  点亮爱豆……")
                        self.logger.info("    开始发光：%s", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                        self.logger.info("    %s", filename)
                        await self.capture_stream(url, filename, "https://live.bilibili.com/%d" % self.room_id)
                else:
                    await asyncio.sleep(self.check_interval)
                room = await self.get_room_info(self.room_id)
                if not room["live_status"] == 1:
                    self.logger.info("⭐️  %s 直播结束 %d", user["info"]["uname"], room["live_status"])
                    end_at = time.time()
                    run_callback(
                        self.callback_end, {
                            "room": room,
                            "user": user,
                            "duration": time.strftime("%H:%M:%S", time.gmtime(end_at - start_at)),
                            "filename": filename if self.capture else None
                        })
                    break
