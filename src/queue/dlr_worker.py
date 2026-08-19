import asyncio
import json
import logging

import aio_pika

from src.dlr.service import forward_dlr
from src.queue.config import queue_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sms.dlr_worker")


async def main() -> None:
    connection = await aio_pika.connect_robust(queue_config.RABBITMQ_URL)
    channel = await connection.channel()
    # Contrairement au worker SMS, la transmission des DLR n'a pas besoin
    # d'être débitée : on peut en traiter plusieurs en parallèle.
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(queue_config.RABBITMQ_DLR_QUEUE, durable=True)

    logger.info("En attente de DLR à transmettre sur la queue '%s'...", queue_config.RABBITMQ_DLR_QUEUE)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                payload = json.loads(message.body.decode())
                await forward_dlr(payload)


if __name__ == "__main__":
    asyncio.run(main())
