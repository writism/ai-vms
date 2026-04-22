import asyncio
import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any

import redis.asyncio as aioredis

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

EventHandler = Callable[[str, dict], Coroutine[Any, Any, None]]


class RedisEventBus:
    def __init__(self, url: str | None = None):
        self._url = url or settings.redis_url
        self._redis: aioredis.Redis | None = None
        self._pubsub: aioredis.client.PubSub | None = None
        self._handlers: dict[str, list[EventHandler]] = {}
        self._task: asyncio.Task | None = None

    async def connect(self) -> None:
        self._redis = aioredis.from_url(self._url, decode_responses=True)
        self._pubsub = self._redis.pubsub()

    async def disconnect(self) -> None:
        if self._task:
            self._task.cancel()
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()

    async def publish(self, channel: str, data: dict) -> None:
        if self._redis is None:
            await self.connect()
        await self._redis.publish(channel, json.dumps(data))

    def subscribe(self, channel: str, handler: EventHandler) -> None:
        if channel not in self._handlers:
            self._handlers[channel] = []
        self._handlers[channel].append(handler)

    async def start_listening(self) -> None:
        if self._pubsub is None:
            await self.connect()

        channels = list(self._handlers.keys())
        if channels:
            await self._pubsub.subscribe(*channels)

        self._task = asyncio.create_task(self._listen_loop())

    async def _listen_loop(self) -> None:
        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    try:
                        data = json.loads(message["data"])
                    except (json.JSONDecodeError, TypeError):
                        data = {"raw": message["data"]}

                    handlers = self._handlers.get(channel, [])
                    for handler in handlers:
                        try:
                            await handler(channel, data)
                        except Exception:
                            logger.exception("Event handler error on channel %s", channel)
        except asyncio.CancelledError:
            pass


event_bus = RedisEventBus()
