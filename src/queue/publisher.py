import json
from typing import Any

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from src.queue.config import queue_config

_connection: AbstractRobustConnection | None = None
_channel: AbstractChannel | None = None


async def get_channel() -> AbstractChannel:
    global _connection, _channel

    if _channel is None or _channel.is_closed:
        _connection = await aio_pika.connect_robust(queue_config.RABBITMQ_URL)
        _channel = await _connection.channel()
        await _channel.declare_queue(queue_config.RABBITMQ_SMS_QUEUE, durable=True)

    return _channel


async def publish_send_task(payload: dict[str, Any]) -> None:
    channel = await get_channel()
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=queue_config.RABBITMQ_SMS_QUEUE,
    )
