from functools import partial, wraps
from os import path
import asyncio
import logging
import time

from tenacity import retry, wait_fixed, before_log, before_sleep_log
from aiohttp import ClientSession
import aiofiles

from conflict.config import config
from conflict.core.exceptions import ApiFailed
from conflict.core.process import process_video
from conflict.log import get_logger
from conflict.push import push
from conflict.schema.config import Watcher
from conflict.schema.push import PushEvent


def _handle_api_result(res: dict):
    if not res['code'] == 0:
        raise ApiFailed(**res)
    return res['data']


class Worker:
    def __init__(self, worker_config: Watcher):
        self.config = worker_config
        self.logger = get_logger(f'{self.config.room_id}.live')
        self._retry = partial(retry,
                              wait=wait_fixed(config.retry_delay),
                              before=before_log(self.logger, logging.DEBUG),
                              before_sleep=before_sleep_log(self.logger, logging.WARNING))

    async def get_info(self) -> dict:
        @self._retry()
        @wraps(self.get_info)
        async def _get_room_info() -> dict:
            async with ClientSession() as session:
                async with session.get('https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom',
                                       params={'room_id': self.config.room_id}) as resp:
                    resp.raise_for_status()
                    return _handle_api_result(await resp.json())

        return await _get_room_info()

    async def get_play_url(self) -> dict:
        @self._retry()
        @wraps(self.get_play_url)
        async def _get_play_url() -> dict:
            async with ClientSession() as session:
                async with session.get(config.get_play_url + 'playUrl',
                                       params={
                                           'cid': self.config.room_id,
                                           'quality': 4,
                                           'platform': 'web'
                                       }) as resp:
                    if resp.status == 503:
                        return {}
                    resp.raise_for_status()
                    return _handle_api_result(await resp.json())

        return await _get_play_url()

    async def capture_stream(self, url, filename):
        @self._retry()
        @wraps(self.capture_stream)
        async def _capture_stream():
            async with ClientSession(
                    headers={
                        'User-Agent': 'Chrome/83.0.4103.116',
                        'Origin': 'https://live.bilibili.com',
                        'Referer': 'https://live.bilibili.com/%d' % self.config.room_id
                    }) as session:
                async with session.get(url) as resp:
                    if resp.status == 404:
                        return
                    resp.raise_for_status()
                    self.logger.info('🌐  %s', url)
                    self.logger.info('🌟  点亮爱豆……')
                    self.logger.info('🕐  开始发光：%s', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                    self.logger.info('📁  %s', filename)
                    async with aiofiles.open(filename, 'wb') as f:
                        while True:
                            chuck = await resp.content.read(1024)
                            if not chuck:
                                break
                            await f.write(chuck)

        await _capture_stream()

    async def run(self):
        while True:
            info = await self.get_info()
            room = info['room_info']
            anchor = info['anchor_info']
            if not room['live_status'] == 1:
                self.logger.info('⭐️  %s 不在直播', anchor['base_info']['uname'])
                await asyncio.sleep(config.check_interval)
                continue

            self.logger.info('⭐️  %s 直播中 %s', anchor['base_info']['uname'], room['live_start_time'])
            for method in self.config.push:
                asyncio.create_task(
                    push(
                        method, PushEvent.LIVE_START,
                        **({
                            **info, 'anchor_info': {
                                **anchor, 'base_info': {
                                    **anchor['base_info'], 'uname': self.config.nickname
                                }
                            }
                        } if self.config.nickname else info)))

            start_at = time.time()
            while True:
                filename = None
                if self.config.capture:
                    filename = '%s-%d-%s.flv' % (self.config.nickname
                                                 or anchor['base_info']['uname'], self.config.room_id,
                                                 time.strftime('%Y-%m-%d_%H%M%S', time.localtime()))
                    filename = path.join(str(config.output), filename)
                    url_info = await self.get_play_url()
                    if url_info == {}:
                        self.logger.info('❌  getPlayUrl 服务当前不可用')
                    elif len(url_info['durl']) == 0:
                        self.logger.info('❌  Stream list is empty')
                    else:
                        url = url_info['durl'][0]['url']
                        self.logger.info('')
                        self.logger.info('☑️  视频流捕获 - %s', url_info['quality_description'][0]['desc'])
                        await self.capture_stream(url, filename)
                        self.logger.info('⚠️  直播信号中断……')
                else:
                    await asyncio.sleep(config.check_interval - config.retry_delay)

                info = await self.get_info()
                room = info['room_info']
                anchor = info['anchor_info']
                if not room['live_status'] == 1:
                    self.logger.info('⭐️  %s 直播结束', anchor['base_info']['uname'])
                    end_at = time.time()
                    if self.config.capture:
                        asyncio.create_task(process_video(filename))
                    for method in self.config.push:
                        asyncio.create_task(
                            push(method,
                                 PushEvent.LIVE_END,
                                 **({
                                     **info, 'anchor_info': {
                                         **anchor, 'base_info': {
                                             **anchor['base_info'], 'uname': self.config.nickname
                                         }
                                     }
                                 } if self.config.nickname else info),
                                 duration=time.strftime("%H:%M:%S", time.gmtime(end_at - start_at))))
                    break

                await asyncio.sleep(config.retry_delay)
