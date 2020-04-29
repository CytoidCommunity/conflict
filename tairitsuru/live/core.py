"""
The core algorithm of tairitsuru.
"""
import asyncio
import time
from functools import partial
from typing import Optional

import aiofiles

from tairitsuru.logger import Logger

from .api import get_play_urls, get_room_info, get_user_info
from .capture import capture


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

    def on_start(self, func):
        self.callback_start.append(func)

    def on_end(self, func):
        self.callback_end.append(func)

    def run_callback(self, callbacks, arg):
        if callbacks:
            [asyncio.create_task(func(arg)) for func in callbacks]

    async def run(self):
        while True:
            room = await get_room_info(self.room_id)
            user = await get_user_info(self.room_id)
            if not room["live_status"] == 1:
                self.logger.info("⭐️  %s 不在直播 %d", user["info"]["uname"],
                                 room["live_status"])
                await asyncio.sleep(self.check_interval)
                continue

            self.logger.info("⭐️  %s 直播中 %s", user["info"]["uname"],
                             room["live_time"])
            self.run_callback(self.callback_start, {
                "room": room,
                "user": user
            })
            start_at = time.time()
            while True:
                if self.capture:
                    filename = "%s-%s.flv" % (
                        user["info"]["uname"],
                        time.strftime("%Y-%m-%d_%H%M%S", time.localtime()))
                    url_info = await get_play_urls(self.room_id)
                    if len(url_info["durl"]) == 0:
                        self.logger.error("❌  Stream list is empty.")
                    else:
                        url = url_info["durl"][0]["url"]
                        self.logger.info("☑️  视频流捕获 Qual.%d",
                                         url_info["current_quality"])
                        self.logger.info("    %s", url)
                        self.logger.info("🌟  点亮爱豆……")
                        self.logger.info(
                            "    开始发光：%s",
                            time.strftime("%Y-%m-%d %H:%M:%S",
                                          time.localtime()))
                        self.logger.info("    %s", filename)
                        await capture(
                            url, filename,
                            "https://live.bilibili.com/%d" % self.room_id)
                else:
                    await asyncio.sleep(self.check_interval)
                room = await get_room_info(self.room_id)
                if not room["live_status"] == 1:
                    self.logger.info("⭐️  %s 直播结束 %d", user["info"]["uname"],
                                     room["live_status"])
                    end_at = time.time()
                    self.run_callback(
                        self.callback_end, {
                            "room": room,
                            "user": user,
                            "duration": end_at - start_at,
                            "filename": filename if self.capture else None
                        })
