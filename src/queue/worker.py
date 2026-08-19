import asyncio
import json
import logging
import uuid

import aio_pika

from src.database import async_session_factory
from src.gateway.factory import get_gateway
from src.messages import service as message_service
from src.messages.constants import MessageStatus
from src.queue.config import queue_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sms.worker")


async def process_message(body: dict) -> None:
    message_id = uuid.UUID(body["message_id"])

    async with async_session_factory() as db:
        message = await message_service.get_by_id(db, message_id)
        if message is None:
            logger.warning("Message %s introuvable, ignoré", message_id)
            return

        gateway = get_gateway()
        result = await gateway.send(
            sender=message.sender_name,
            to=message.to_number,
            text=message.text,
            dlr_url=message.dlr_url,
        )

        if result.success:
            await message_service.update_status(
                db, message, status=MessageStatus.SENT, provider_message_id=result.provider_message_id
            )
            logger.info("SMS %s -> %s envoyé (provider_id=%s)", message.sender_name, message.to_number, result.provider_message_id)
        else:
            await message_service.update_status(
                db, message, status=MessageStatus.REJECTED, error=result.description
            )
            logger.warning("SMS %s -> %s rejeté: %s", message.sender_name, message.to_number, result.description)


async def main() -> None:
    connection = await aio_pika.connect_robust(queue_config.RABBITMQ_URL)
    channel = await connection.channel()
    # Un seul message traité à la fois : c'est ce qui applique le débit
    # SMS_SEND_INTERVAL_MS, à la place du `throughput=` de Kannel.
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(queue_config.RABBITMQ_SMS_QUEUE, durable=True)

    logger.info("En attente de SMS sur la queue '%s'...", queue_config.RABBITMQ_SMS_QUEUE)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                body = json.loads(message.body.decode())
                await process_message(body)
                await asyncio.sleep(queue_config.SMS_SEND_INTERVAL_MS / 1000)


if __name__ == "__main__":
    asyncio.run(main())
